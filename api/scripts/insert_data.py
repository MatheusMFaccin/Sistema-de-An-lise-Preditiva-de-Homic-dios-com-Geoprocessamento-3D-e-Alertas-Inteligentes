# scripts/insert_data.py
from pathlib import Path
import sys
import os
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from db.session import SessionLocal
from models.evento import Evento
from models.datasus import Datasus
from models.previsao import Previsao
from models.dados_reais import DadosReaisAnuais
from models.ComparativoPrevisao import ComparativoPrevisao
from scripts.correlacao import Correlacao 
from scripts.table_scripts import Limpa_arquivo
from datetime import date
from sqlalchemy.dialects.postgresql import insert
import re
import unicodedata
from correlacao import Correlacao



BASE = Path(__file__).resolve().parent
class Conn:
    def __init__(self):
        pass
    def remover_acentos(self,texto):
        if isinstance(texto, str):
            return ''.join(
                c for c in unicodedata.normalize('NFD', texto)
                if unicodedata.category(c) != 'Mn'
            )
        return texto
    def insert_datasus(self, SessionLocal,datasus_csv,ano):
        
        df = Limpa_arquivo.load_datasus(datasus_csv)
        print(df)
        df['Município'] = df['Município'].str.replace(r'^\d+ ', '', regex=True)
        df.to_csv("debug_datasus.txt", sep=";", index=False)
        print()
        db = SessionLocal()

        colunas_meses = [col for col in df.columns if col not in ["Município", "Total"]]
    
        
        df_longo = df.melt(
            id_vars=["Município"],      #
            value_vars=colunas_meses,   
            var_name="mes",             
            value_name="mortes"         
        )
        
        
        df_longo['mortes'] = df_longo['mortes'].astype(int)
        df_longo.to_csv("debug_txt",index=False)
        print(f"--- 1. Preparando {len(df_longo)} registros para inserir... ---")

        df_longo['Município'] = df_longo['Município'].apply(self.remover_acentos)
        registros_dict = df_longo.to_dict('records')
        

        for r in registros_dict:
            r['ano'] = ano 
            r['municipio'] = r.pop('Município')
        
        if not registros_dict:
            
            db.close()
            return 

        try:
            
            stmt = insert(Datasus).values(registros_dict)
            
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['municipio', 'mes', 'ano']
            )
            
            db.execute(stmt)
            db.commit()
            
            print("susesso")
        except Exception as e:
            print(f"Erro durante a inserção do Datasus: {e}")
            db.rollback()
        finally:
            db.close()

    def mes_ano(self,texto):
        objeto_data = date.fromisoformat(texto)
        ano = objeto_data.year
        mes = objeto_data.month
        return ano, mes
    def insert_evento(self, SessionLocal, evento_csv):
    

        df = pd.read_csv(evento_csv, sep=";")
        df["data_referencia"] = pd.to_datetime(df["data_referencia"]).dt.date

        df['data_referencia'] = pd.to_datetime(df['data_referencia'])
        df_rs = df[df['uf'] == 'RS' ]
        df_rs = df_rs[df_rs['evento'] == 'Tentativa de homicídio']

        df_rs['ano'] = df_rs['data_referencia'].dt.year
        df_rs['mes'] = df_rs['data_referencia'].dt.day

        
        print("--- 4. Agregando totais por município/mês/ano... ---")
        colunas_agrupamento = ['uf', 'municipio', 'ano', 'mes']
        
        
        df_previsao = df_rs.groupby(colunas_agrupamento)['total_vitima'].sum().reset_index()

        
        df_previsao.rename(columns={'total_vitima': 'vitimas'}, inplace=True)
        
        
        df_previsao.to_csv("debug_agregado.txt", sep=";", index=False)
        print(f"--- {len(df_previsao)} registros agregados prontos para inserir. ---")
        print(df_previsao.head()) 

        db = SessionLocal()
        

        df_previsao['municipio'] = df_previsao['municipio'].apply(self.remover_acentos)

        print(f"--- 5. Preparando {len(df_previsao)} registros para inserir... ---")
        registros = df_previsao.to_dict('records')

        # Garante que os tipos estão corretos (int, não float)
        for r in registros:
            r['ano'] = int(r['ano'])
            r['mes'] = str(r['mes'])
            r['vitimas'] = int(r['vitimas'])

        if registros: # Só executa se houver registros
            try:
                # Cria a declaração de INSERT
                stmt = insert(Evento).values(registros)
                
                # Diz ao PostgreSQL: "SE HOUVER CONFLITO (duplicata), NÃO FAÇA NADA"
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['uf', 'municipio', 'ano', 'mes']
                )
                
                # Executa tudo de uma vez
                db.execute(stmt)
                db.commit()
                print("Dados inseridos/ignorados com sucesso!")
                
            except Exception as e:
                print(f"Erro durante a inserção em massa: {e}")
                db.rollback()
            finally:
                db.close()
        else:
            print("--- Nenhum registro para inserir. ---")
            db.close()
        
    
    def insert_correlacao(self, SessionLocal, df_previsao):
        db = SessionLocal()
        


        print(f"--- 5. Preparando {len(df_previsao)} registros para inserir... ---")
        registros = df_previsao.to_dict('records')

        

        if registros: # Só executa se houver registros
            try:
                # Cria a declaração de INSERT
                stmt = insert(Previsao).values(registros)
                
                # Diz ao PostgreSQL: "SE HOUVER CONFLITO (duplicata), NÃO FAÇA NADA"
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['municipio', 'ano_previsao']
                )
                
                # Executa tudo de uma vez
                db.execute(stmt)
                db.commit()
                print("Dados inseridos/ignorados com sucesso!")
                
            except Exception as e:
                print(f"Erro durante a inserção em massa: {e}")
                db.rollback()
            finally:
                db.close()
    
    
    def insert_dados_reais(self, SessionLocal, df_dados_reais):

        db = SessionLocal()
        


        print(f"--- 5. Preparando {len(df_dados_reais)} registros para inserir... ---")
        registros = df_dados_reais.to_dict('records')

        

        if registros: # Só executa se houver registros
            try:
                # Cria a declaração de INSERT
                stmt = insert(DadosReaisAnuais).values(registros)
                
                # Diz ao PostgreSQL: "SE HOUVER CONFLITO (duplicata), NÃO FAÇA NADA"
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['municipio', 'ano']
                )
                
                # Executa tudo de uma vez
                db.execute(stmt)
                db.commit()
                print("Dados inseridos/ignorados com sucesso!")
                
            except Exception as e:
                print(f"Erro durante a inserção em massa: {e}")
                db.rollback()
            finally:
                db.close()
    def insert_comparativo(self, SessionLocal, df_comparacao):


        # 1. Chame sua função para obter o DataFrame
        print("Calculando comparações...")
        

        if df_comparacao.empty:
            print("Nenhum dado de comparação foi gerado para salvar.")
            return # Para a execução da função

        # 3. Converta o DataFrame para uma lista de dicionários
        dados_para_salvar = df_comparacao.to_dict('records')

        # 4. Crie o comando de insert (UPSERT)
        stmt = insert(ComparativoPrevisao).values(dados_para_salvar)

        # 5. Defina QUAIS colunas devem ser ATUALIZADAS em caso de conflito
        # (Basicamente, tudo, exceto as chaves 'municipio' e 'ano')
        update_cols = {
            'total_vitimas_ano': stmt.excluded.total_vitimas_ano,
            'previsao_homicidios': stmt.excluded.previsao_homicidios, # Verifique este nome
            'previsao_min': stmt.excluded.previsao_min,
            'previsao_max': stmt.excluded.previsao_max,
            'classificacao': stmt.excluded.classificacao,
            'margem_erro_k': stmt.excluded.margem_erro_k,
            'correlacao_temporal_r': stmt.excluded.correlacao_temporal_r,
            'erro_padrao_se': stmt.excluded.erro_padrao_se,
            'fator_penalidade_fr': stmt.excluded.fator_penalidade_fr,
            'n_anos_dados': stmt.excluded.n_anos_dados
        }

        # 6. Finalize o comando, especificando o conflito e as atualizações
        stmt = stmt.on_conflict_do_update(
            index_elements=['municipio', 'ano'], # A restrição única
            set_=update_cols                  
        )

        # 7. Execute
        db = SessionLocal()
        print(f"Salvando/Atualizando {len(dados_para_salvar)} linhas no banco...")
        try:
            db.execute(stmt)
            db.commit()
            print(f"Sucesso: {len(dados_para_salvar)} linhas de comparação salvas/atualizadas.")
        except Exception as e:
            db.rollback()
            print(f"Erro ao salvar dados de comparação: {e}")
        finally:
            db.close()

if __name__ == "__main__":
    evento_caminho = "eventos2024.csv"
    datasus_caminho = 'datasus2024.txt'
    ano_datasus = "2024"
    conn = Conn()
    conn.insert_evento(SessionLocal, evento_caminho)
    conn.insert_datasus(SessionLocal,datasus_caminho,ano_datasus)
    datasus = Correlacao.prepara_correlacao_datasus()
    eventos = Correlacao.prepara_correlacao_eventos()
    c = Correlacao()
    correlacao = c.calcular_previsao_temporal_por_municipio(datasus,eventos)
    correlacao.to_csv("correlacao.txt", sep=";", index=False)
    df_anual = c.calcula_dados_reais()
    df_anual.to_csv("dados_reais.txt", sep=";", index=False)
    conn.insert_correlacao(SessionLocal, correlacao)
    conn.insert_dados_reais(SessionLocal, df_anual)
    df_comparacao = c.comparar_previsoes_com_reais()
    df_comparacao.to_csv("comparacao.txt", sep=";",index = False)
    conn.insert_comparativo(SessionLocal, df_comparacao)



