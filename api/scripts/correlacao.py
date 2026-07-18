import pandas as pd
from sqlalchemy import create_engine
from db.session import engine
from sklearn.linear_model import LinearRegression
import warnings
import numpy as np

class Correlacao:
    def __init__(self):
        pass

    @staticmethod
    def prepara_correlacao_datasus():
        print("--- Lendo tabela 'datasus' do BD... ---")
        # Agora buscamos municipio_id diretamente
        query = """
            SELECT municipio_id, mes, mortes, ano 
            FROM datasus
        """
        df = pd.read_sql(query, con=engine)
        
        # Conversão de nome de mês para número (se necessário)
        # Assumindo que no banco já salvamos int (1-12), mas se ainda for string:
        mapa_meses = {
            "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4,
            "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
            "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
        }
        
        # Verifica se 'mes' é string e converte
        if df['mes'].dtype == 'object':
             df["mes_nome"] = df["mes"].str.strip().str.lower()
             df["mes"] = df["mes_nome"].map(mapa_meses)
             df.drop(columns=["mes_nome"], inplace=True)
        
        # Renomear para padrao do calculo
        df.rename(columns={"mortes": "mortes_no_mes_municipio"}, inplace=True)
        
        return df

    @staticmethod
    def prepara_correlacao_eventos(): 
        print("--- Lendo tabela 'eventos' do BD... ---")
        query = """
            SELECT municipio_id, mes, ano, vitimas 
            FROM eventos
        """
        df = pd.read_sql(query, con=engine)
        
        # Se no banco o mes for int, perfeito.
        df.rename(columns={"vitimas": "vitimas_homicidio_no_mes_municipio"}, inplace=True)
        
        return df

    def calcular_fator_penalidade(self, r):
        if pd.isna(r): return 2.5 
        r_abs = abs(r)
        if r_abs >= 0.9: return 1.0
        elif r_abs >= 0.7: return 1.5
        elif r_abs >= 0.5: return 2.0
        return 2.5

    def calcular_previsao_para_grupo(self, group):
        # Lógica idêntica, apenas garante ordenação
        group = group.sort_values('ano')
        
        X_train = group[['ano']]
        Y_train_vitimas = group['total_vitimas_ano']
        # Se tiver dados de mortes (datasus)
        Y_train_mortes = group['total_mortes_ano'] if 'total_mortes_ano' in group else None

        model = LinearRegression()
        model.fit(X_train, Y_train_vitimas)

        r_temporal = np.nan
        if Y_train_mortes is not None and Y_train_mortes.var() > 0 and Y_train_vitimas.var() > 0:
            r_temporal = Y_train_vitimas.corr(Y_train_mortes)

        Y_pred_train = model.predict(X_train) 
        n = len(group)
        
        # Calculo erro padrao
        if n > 2:
            sum_sq_error = ((Y_train_vitimas - Y_pred_train) ** 2).sum()
            se = np.sqrt(sum_sq_error / (n - 2))
        else:
            se = np.nan

        f_r = self.calcular_fator_penalidade(r_temporal)
        k = (se * f_r) if not pd.isna(se) else 0

        # Previsão para anos históricos
        df_res = pd.DataFrame({
            'ano_previsao': group['ano'],
            'previsao_homicidios': Y_pred_train
        })

        # Previsão Futura (Ano Max + 1)
        ano_max = group['ano'].max()
        prox_ano = np.array([[ ano_max + 1 ]])
        prev_futura = model.predict(prox_ano)[0]
        
        df_futuro = pd.DataFrame({'ano_previsao': [ano_max + 1], 'previsao_homicidios': [prev_futura]})
        df_res = pd.concat([df_res, df_futuro], ignore_index=True)

        # Métricas
        df_res['margem_erro_k'] = k
        df_res['previsao_min'] = df_res['previsao_homicidios'] - k
        df_res['previsao_max'] = df_res['previsao_homicidios'] + k
        df_res['correlacao_temporal_r'] = r_temporal
        df_res['erro_padrao_se'] = se
        df_res['fator_penalidade_fr'] = f_r
        df_res['n_anos_dados'] = n
        
        # Mantém todos os anos do grupo + o ano futuro
        anos_originais = group['ano'].unique()
        anos_para_manter = sorted(set(anos_originais) | {ano_max + 1})
        df_res = df_res[df_res['ano_previsao'].isin(anos_para_manter)].copy()
        
        cols_int = ['previsao_homicidios', 'previsao_min', 'previsao_max']
        for col in cols_int:
            df_res[col] = df_res[col].round().apply(lambda x: max(0, x)).fillna(0).astype(int)

        return df_res

    def calcular_previsao_temporal_por_municipio(self, df_datasus, df_eventos):
        # Merge usando municipio_id
        df_merged = pd.merge(
            df_datasus, df_eventos,
            on=["municipio_id", "mes", "ano"],
            how="inner"
        )
        
        # Agregação Anual
        df_anual = df_merged.groupby(['municipio_id', 'ano']).agg(
            total_mortes_ano=('mortes_no_mes_municipio', 'sum'),
            total_vitimas_ano=('vitimas_homicidio_no_mes_municipio', 'sum')
        ).reset_index()

        # Filtro de dados suficientes
        sizes = df_anual.groupby('municipio_id').size()
        ids_validos = sizes[sizes > 2].index
        df_filtrado = df_anual[df_anual['municipio_id'].isin(ids_validos)]

        print(f"Calculando para {len(ids_validos)} municípios...")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Groupby por ID
            df_previsoes = df_filtrado.groupby('municipio_id').apply(self.calcular_previsao_para_grupo)

        # --- CORREÇÃO DO ERRO AQUI ---
        # Se 'municipio_id' já existir nas colunas (resultado do apply), removemos para evitar conflito com o índice
        if 'municipio_id' in df_previsoes.columns:
            df_previsoes = df_previsoes.drop(columns=['municipio_id'])
            
        # Agora é seguro resetar o índice
        df_previsoes = df_previsoes.reset_index()
        # -----------------------------

        if 'level_1' in df_previsoes.columns: 
            df_previsoes.drop(columns=['level_1'], inplace=True)
        
        return df_previsoes
        
    def calcula_dados_reais(self):
        # Agrega dados reais baseado no banco atualizado
        query = "SELECT municipio_id, ano, vitimas FROM eventos"
        df = pd.read_sql(query, con=engine)
        return df.groupby(['municipio_id','ano']).agg(total_vitimas_ano=('vitimas','sum')).reset_index()

    def comparar_previsoes_com_reais(self):
        print("Iniciando comparação...")
        try:
            # Trazendo os IDs para manter a rastreabilidade
            df_prev = pd.read_sql("SELECT id, municipio_id, ano_previsao, previsao_homicidios, previsao_min, previsao_max FROM previsoes", con=engine)
            df_reais = pd.read_sql("SELECT id, municipio_id, ano, total_vitimas_ano FROM dados_reais_anuais", con=engine)
        except Exception as e:
            print(e)
            return pd.DataFrame()

        if df_prev.empty or df_reais.empty: return pd.DataFrame()

        df_prev = df_prev.rename(columns={'ano_previsao': 'ano'})
        
        # Merge por ID do municipio e Ano
        df_comp = pd.merge(df_prev, df_reais, on=['municipio_id', 'ano'], how='inner')

        # --- CORREÇÃO CRÍTICA AQUI ---
        # O merge criou 'id_x' (da previsao) e 'id_y' (dos dados reais).
        # Precisamos renomear para bater com o Model 'ComparativoPrevisao'
        df_comp.rename(columns={
            'id_x': 'previsao_id',
            'id_y': 'dado_real_id'
        }, inplace=True)
        # -----------------------------

        conditions = [
            (df_comp['total_vitimas_ano'] > df_comp['previsao_max']),
            (df_comp['total_vitimas_ano'] < df_comp['previsao_min'])
        ]
        choices = ['Acima do Previsto', 'Abaixo do Previsto']
        
        df_comp['classificacao'] = np.select(conditions, choices, default='Dentro do Previsto')
        
        # Preencher métricas extras que não vêm do merge (se existirem no seu DF original, mantenha)
        # Se o modelo exige margem_erro_k e ela não veio no SELECT lá em cima, você precisa buscar ou calcular.
        # Vou assumir que você pode adicionar margem_erro_k no SELECT do df_prev se precisar.
        
        return df_comp