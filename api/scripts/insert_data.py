# scripts/insert_data.py
from pathlib import Path
import sys
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
import unicodedata
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from db.session import SessionLocal
# Importe o novo modelo de Municipio
from models.municipio import Municipio 
from models.evento import Evento
from models.datasus import Datasus
from models.previsao import Previsao
from models.dados_reais import EventosTotaisAnuais # Corrigido nome da classe se necessario
from models.ComparativoPrevisao import ComparativoPrevisao
from scripts.correlacao import Correlacao 
from scripts.table_scripts import Limpa_arquivo

class Conn:
    def __init__(self):
        self.municipio_map = {} # Cache para { "nome_limpo": id }

    def remover_acentos(self, texto):
        if isinstance(texto, str):
            return ''.join(
                c for c in unicodedata.normalize('NFD', texto)
                if unicodedata.category(c) != 'Mn'
            ).upper().strip() # Padronizei para UPPERCASE para evitar duplicatas "Nome" vs "NOME"
        return texto

    def _carregar_mapa_municipios(self, session):
        """Carrega todos os municípios do banco para um dicionário em memória."""
        print("--- Carregando mapa de municípios do banco... ---")
        municipios = session.query(Municipio).all()
        self.municipio_map = {m.nome: m.id for m in municipios}
        print(f"--- Mapa carregado com {len(self.municipio_map)} municípios. ---")

    def sync_municipios(self, SessionLocal, datasus_csv, evento_csv):
        """
        Lê os arquivos CSV, extrai nomes únicos de municípios e cadastra na tabela 'municipios'
        se ainda não existirem.
        """
        db = SessionLocal()
        try:
            print("--- Sincronizando Tabela de Municípios... ---")
            nomes_unicos = set()

            # 1. Extrair do Datasus
            df_datasus = Limpa_arquivo.load_datasus(datasus_csv)
            df_datasus['Município'] = df_datasus['Município'].str.replace(r'^\d+ ', '', regex=True)
            nomes_datasus = df_datasus['Município'].apply(self.remover_acentos).unique()
            nomes_unicos.update(nomes_datasus)

            # 2. Extrair de Eventos
            # CORREÇÃO DO DTYPE WARNING: low_memory=False
            df_evento = pd.read_csv(evento_csv, sep=";", low_memory=False) 
            
            df_evento_rs = df_evento[df_evento['uf'] == 'RS']
            nomes_eventos = df_evento_rs['municipio'].apply(self.remover_acentos).unique()
            nomes_unicos.update(nomes_eventos)

            # 3. Inserir novos
            objs = []
            for nome in nomes_unicos:
                if not nome: continue
                # Como definimos a constraint como (nome, uf), precisamos passar ambos
                objs.append({"nome": nome, "uf": "RS"}) 
            
            if objs:
                stmt = insert(Municipio).values(objs)
                
                # CORREÇÃO DO ERRO DE INSERT:
                # index_elements deve conter AS DUAS colunas da constraint criada no model
                stmt = stmt.on_conflict_do_nothing(index_elements=['nome', 'uf']) 
                
                db.execute(stmt)
                db.commit()
            
            # 4. Atualizar o mapa em memória
            self._carregar_mapa_municipios(db)

        except Exception as e:
            print(f"Erro ao sincronizar municípios: {e}")
            db.rollback()
        finally:
            db.close()

    def insert_datasus(self, SessionLocal, datasus_csv, ano):
        db = SessionLocal()
        try:
            if not self.municipio_map:
                self._carregar_mapa_municipios(db)

            df = Limpa_arquivo.load_datasus(datasus_csv)
            
            # Remove prefixos numéricos do nome do município (ex: "12345 Porto Alegre" -> "Porto Alegre")
            df['Município'] = df['Município'].str.replace(r'^\d+ ', '', regex=True)
            
            # Identifica as colunas de meses
            colunas_meses = [col for col in df.columns if col not in ["Município", "Total"]]
            
            # Transforma de largo para longo (Unpivot)
            df_longo = df.melt(id_vars=["Município"], value_vars=colunas_meses, var_name="mes_nome", value_name="mortes")
            
            # --- CORREÇÃO: Mapeamento de Meses (Nome -> Número) ---
            mapa_meses = {
                "Janeiro": 1, "Jan": 1,
                "Fevereiro": 2, "Fev": 2,
                "Março": 3, "Marco": 3, "Mar": 3,
                "Abril": 4, "Abr": 4,
                "Maio": 5, "Mai": 5,
                "Junho": 6, "Jun": 6,
                "Julho": 7, "Jul": 7,
                "Agosto": 8, "Ago": 8,
                "Setembro": 9, "Set": 9,
                "Outubro": 10, "Out": 10,
                "Novembro": 11, "Nov": 11,
                "Dezembro": 12, "Dez": 12
            }
            
            # Normaliza o texto (remove espaços e deixa a primeira letra maiúscula) e aplica o mapa
            # Ex: "janeiro " -> "Janeiro" -> 1
            df_longo['mes_int'] = df_longo['mes_nome'].astype(str).str.strip().str.title().map(mapa_meses)
            
            # Verifica se algum mês falhou na conversão
            erros_mes = df_longo[df_longo['mes_int'].isna()]
            if not erros_mes.empty:
                print("AVISO: Alguns meses não puderam ser convertidos e serão ignorados:")
                print(erros_mes['mes_nome'].unique())
                df_longo = df_longo.dropna(subset=['mes_int'])
            
            df_longo['mes'] = df_longo['mes_int'].astype(int)
            # -------------------------------------------------------

            # Limpeza e Conversão de valores
            df_longo['mortes'] = pd.to_numeric(df_longo['mortes'], errors='coerce').fillna(0).astype(int)
            
            # Mapear Nome -> ID do Município
            df_longo['Município_limpo'] = df_longo['Município'].apply(self.remover_acentos)
            df_longo['municipio_id'] = df_longo['Município_limpo'].map(self.municipio_map)
            
            # Remover linhas onde não achou o ID
            df_final = df_longo.dropna(subset=['municipio_id'])
            
            registros = df_final[['municipio_id', 'mes', 'mortes']].to_dict('records')
            
            # Adiciona o ano em cada registro
            for r in registros:
                r['ano'] = int(ano)

            if registros:
                print(f"--- Inserindo {len(registros)} registros no Datasus... ---")
                stmt = insert(Datasus).values(registros)
                # Importante: index_elements deve bater com a UniqueConstraint do banco
                stmt = stmt.on_conflict_do_nothing(index_elements=['municipio_id', 'ano', 'mes'])
                db.execute(stmt)
                db.commit()
                print("Datasus inserido com sucesso.")
            else:
                print("Nenhum registro válido para inserir no Datasus.")
                
        except Exception as e:
            print(f"Erro Datasus: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
        finally:
            db.close()

    def insert_evento(self, SessionLocal, evento_csv):
        db = SessionLocal()
        try:
            if not self.municipio_map:
                self._carregar_mapa_municipios(db)

            df = pd.read_csv(evento_csv, sep=";")
            df["data_referencia"] = pd.to_datetime(df["data_referencia"])
            
            df_rs = df[(df['uf'] == 'RS') & (df['evento'] == 'Tentativa de homicídio')].copy()
            df_rs['ano'] = df_rs['data_referencia'].dt.year
            df_rs['mes'] = df_rs['data_referencia'].dt.month # Melhor usar .month (int 1-12) se o banco for INT

            # Limpar nomes e Mapear IDs
            df_rs['municipio_limpo'] = df_rs['municipio'].apply(self.remover_acentos)
            df_rs['municipio_id'] = df_rs['municipio_limpo'].map(self.municipio_map)
            
            df_rs = df_rs.dropna(subset=['municipio_id'])

            # Agregar
            colunas_agrupamento = ['municipio_id', 'ano', 'mes']
            df_agregado = df_rs.groupby(colunas_agrupamento)['total_vitima'].sum().reset_index()
            df_agregado.rename(columns={'total_vitima': 'vitimas'}, inplace=True)

            registros = df_agregado.to_dict('records')
            
            if registros:
                print(f"--- Inserindo {len(registros)} registros de Eventos... ---")
                stmt = insert(Evento).values(registros)
                stmt = stmt.on_conflict_do_nothing(index_elements=['municipio_id', 'ano', 'mes'])
                db.execute(stmt)
                db.commit()
                print("Eventos inseridos com sucesso.")
                
        except Exception as e:
            print(f"Erro Eventos: {e}")
            db.rollback()
        finally:
            db.close()

    def insert_correlacao(self, SessionLocal, df_previsao):
        # df_previsao vindo do script de correlação deve conter 'municipio_id'
        db = SessionLocal()
        try:
            registros = df_previsao.to_dict('records')
            # Limpar chaves que não existem no model se houverem
            # O model espera: municipio_id, ano_previsao, etc.
            
            if registros:
                print(f"--- Inserindo {len(registros)} Previsões... ---")
                stmt = insert(Previsao).values(registros)
                stmt = stmt.on_conflict_do_nothing(index_elements=['municipio_id', 'ano_previsao'])
                db.execute(stmt)
                db.commit()
        except Exception as e:
            print(f"Erro Previsão: {e}")
            db.rollback()
        finally:
            db.close()

    def insert_dados_reais(self, SessionLocal, df_dados_reais):
        db = SessionLocal()
        try:
            registros = df_dados_reais.to_dict('records')
            if registros:
                stmt = insert(EventosTotaisAnuais).values(registros)
                stmt = stmt.on_conflict_do_nothing(index_elements=['municipio_id', 'ano'])
                db.execute(stmt)
                db.commit()
        except Exception as e:
            print(f"Erro Dados Reais: {e}")
            db.rollback()
        finally:
            db.close()

    def insert_comparativo(self, SessionLocal, df_comparacao):
        db = SessionLocal()
        try:
            # Substitui NaN do Pandas por None (NULL do SQL)
            # Isso é essencial para o campo 'dado_real_id' funcionar se estiver vazio
            df_comparacao = df_comparacao.where(pd.notnull(df_comparacao), None)
            
            registros = df_comparacao.to_dict('records')
            if not registros: return

            # Filtra apenas colunas que o Model conhece
            cols_validas = {c.name for c in ComparativoPrevisao.__table__.columns}
            registros_limpos = [{k: v for k, v in r.items() if k in cols_validas} for r in registros]

            stmt = insert(ComparativoPrevisao).values(registros_limpos)
            
            # Precisamos excluir as chaves primárias/estrangeiras da atualização
            update_cols = {
                col.name: col 
                for col in stmt.excluded 
                if col.name not in ['id', 'municipio_id', 'ano', 'previsao_id', 'dado_real_id']
            }

            # O Upsert
            stmt = stmt.on_conflict_do_update(
                index_elements=['municipio_id', 'ano'],
                set_=update_cols
            )
            db.execute(stmt)
            db.commit()
            print(f"Comparativo salvo: {len(registros)} registros.")
        except Exception as e:
            print(f"Erro Comparativo: {e}")
            import traceback
            traceback.print_exc() # Ótimo para debug
            db.rollback()
        finally:
            db.close()


if __name__ == "__main__":
    # 1. Defina as listas corretamente (sem o [i])
    eventos_arquivos = [
        "eventos2024.csv", "eventos2023.csv", "eventos2022.csv",
        "eventos2021.csv", "eventos2020.csv", "eventos2019.csv"
    ]
    datasus_arquivos = [
        'datasus2024.txt', 'datasus2023.txt', 'datasus2022.txt',
        'datasus2021.txt', 'datasus2020.txt', 'datasus2019.txt'
    ]
    anos = ["2024", "2023", "2022", "2021", "2020", "2019"]
    
    conn = Conn() # Instancie a conexão uma vez fora do loop

    # 2. Loop apenas para inserção de dados
    for i in range(len(eventos_arquivos)):
        print(f"--- Processando ano {anos[i]} ---")
        
        # Sincroniza municípios e insere dados brutos
        conn.sync_municipios(SessionLocal, datasus_arquivos[i], eventos_arquivos[i])
        conn.insert_evento(SessionLocal, eventos_arquivos[i])
        conn.insert_datasus(SessionLocal, datasus_arquivos[i], anos[i])

    # 3. Cálculos de correlação (FORA do loop de inserção)
    # Isso evita que o código fique lento e recalcule o que já foi feito
    print("--- Calculando Correlações e Previsões ---")
    
    datasus_df = Correlacao.prepara_correlacao_datasus()
    eventos_df = Correlacao.prepara_correlacao_eventos()

    c = Correlacao()
    correlacao_df = c.calcular_previsao_temporal_por_municipio(datasus_df, eventos_df)

    # Salvar logs
    correlacao_df.to_csv("correlacao_debug.csv", sep=";", index=False)
    conn.insert_correlacao(SessionLocal, correlacao_df)

    # Dados reais e comparativos
    df_reais = c.calcula_dados_reais()
    df_reais.to_csv("reais.csv", sep=";", index=False)
    conn.insert_dados_reais(SessionLocal, df_reais)

    df_comp = c.comparar_previsoes_com_reais()
    conn.insert_comparativo(SessionLocal, df_comp)
    
    print("--- Processo finalizado com sucesso! ---")