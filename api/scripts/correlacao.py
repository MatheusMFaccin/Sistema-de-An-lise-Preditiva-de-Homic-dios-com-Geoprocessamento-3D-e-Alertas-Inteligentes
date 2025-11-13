import pandas as pd
from sqlalchemy import create_engine
from db.session import engine
import unicodedata
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import warnings
import numpy as np

class Correlacao:
        def __init__(self):
            pass
        def prepara_correlacao_datasus():
        
            print("--- Lendo tabela 'datasus' (formato longo)... ---")
            
            df_datasus = pd.read_sql(
                "SELECT municipio, mes, mortes, ano FROM datasus", 
                con=engine
            )

            df_datasus.rename(columns={
                "mortes": "mortes_no_mes_municipio",
                "mes": "mes_nome"
            }, inplace=True)
            
            
            df_datasus["mes_nome"] = df_datasus["mes_nome"].str.strip().str.lower()
            
            mapa_meses = {
                "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
                "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
                "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
            }

            
            df_datasus["mes"] = df_datasus["mes_nome"].map(mapa_meses)
            
            
            df_datasus = df_datasus[df_datasus["municipio"] != "total"]

            
            df_datasus.to_csv("mortalidade.txt", sep=";", index=False, encoding="utf-8")
            
            print("--- Preparação do Datasus (formato longo) concluída. ---")
            
            return df_datasus

        def prepara_correlacao_eventos(): 
        
            print("--- Lendo tabela 'eventos' (formato longo)... ---")
            df_eventos = pd.read_sql(
                "SELECT uf, municipio, mes, ano, vitimas FROM eventos", 
                con=engine
            )
            
            df_rs = df_eventos[df_eventos['uf'] == 'RS'].copy()
            
            vitimas_por_mes = df_rs.rename(
                columns={"vitimas": "vitimas_homicidio_no_mes_municipio"}
            )

            

            
            mapa_meses_num_para_nome = {
                1: "janeiro", 2: "fevereiro", 3: "marco", 4: "abril",
                5: "maio", 6: "junho", 7: "julho", 8: "agosto",
                9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
            }
            
            
            try:
                vitimas_por_mes['mes'] = vitimas_por_mes['mes'].astype(int)
            except ValueError as e:
                print(f"AVISO: A coluna 'mes' pode conter valores não numéricos. Limpando...")
                vitimas_por_mes = vitimas_por_mes[pd.to_numeric(vitimas_por_mes['mes'], errors='coerce').notna()]
                vitimas_por_mes['mes'] = vitimas_por_mes['mes'].astype(int)

            
            vitimas_por_mes['mes'] = vitimas_por_mes['mes'].map(mapa_meses_num_para_nome)

            
            vitimas_por_mes = vitimas_por_mes[[
                "municipio", "mes", "ano", "vitimas_homicidio_no_mes_municipio"
            ]]
            
            
            vitimas_por_mes = vitimas_por_mes[vitimas_por_mes["municipio"] != "NAO INFORMADO"]
            
            
            vitimas_por_mes.to_csv("homicidos.txt", sep=";", index=False, encoding="utf-8")
            
            print("--- Preparação de Eventos (formato longo) concluída. ---")
            return vitimas_por_mes
        

        def calcular_fator_penalidade(self, r):
            """
            Calcula o fator de penalidade f(r) com base no coeficiente de correlação r.
            """
            if pd.isna(r):
                return 2.5 # Penalidade máxima se a correlação não puder ser calculada
            
            r_abs = abs(r)
            if r_abs >= 0.9:
                return 1.0
            elif r_abs >= 0.7:
                return 1.5
            elif r_abs >= 0.5:
                return 2.0
            else: # |r| < 0.5
                return 2.5

        def calcular_previsao_para_grupo(self, group):
            """
            Recebe os dados anuais de UM município e calcula a previsão e margem de erro.
            AGORA RETORNA UM DATAFRAME com as previsões de 2019-2025.
            """
            # Ordena por ano (importante para séries temporais)
            group = group.sort_values('ano')
            
            # Prepara os dados para a Regressão Linear
            X_train = group[['ano']]
            Y_train_mortes = group['total_mortes_ano']
            Y_train_vitimas = group['total_vitimas_ano']
            
            # --- A. Treinar o Modelo ---
            model = LinearRegression()
            model.fit(X_train, Y_train_vitimas)
            
            # --- B. Calcular o 'r' (Correlação Temporal) ---
            if Y_train_mortes.var() > 0 and Y_train_vitimas.var() > 0:
                r_temporal = Y_train_vitimas.corr(Y_train_mortes)
            else:
                r_temporal = np.nan

            # --- C. Calcular o 'Se' (Erro Padrão da Estimativa) ---
            Y_pred_train = model.predict(X_train) 
            n = len(group)
            graus_de_liberdade = n - 2
            
            if graus_de_liberdade <= 0:
                se = np.nan
            else:
                sum_sq_error = ((Y_train_vitimas - Y_pred_train) ** 2).sum()
                se = np.sqrt(sum_sq_error / graus_de_liberdade)

            # --- D. Calcular a Margem de Erro (k) ---
            f_r = self.calcular_fator_penalidade(r_temporal)
            k = se * f_r

            # --- E. Criar o DataFrame de Resultado (PASSADO) ---
            # Y_pred_train é um float, o que é correto
            df_resultado_grupo = pd.DataFrame({
                'ano_previsao': group['ano'],
                'previsao_homicidios': Y_pred_train
            })

            # --- F. Fazer a Previsão (FUTURO) ---
            ano_max = group['ano'].max()
            proximo_ano_array = np.array([[ ano_max + 1 ]]) # ex: [[2025]]
            previsao_futura = model.predict(proximo_ano_array)[0]
            
            # !!! MUDANÇA AQUI !!!
            # Removi o arredondamento daqui para manter todos os cálculos
            # em float até o final.
            # --------------------
            # if previsao_futura < 0:
            #     previsao_futura = 0
            # previsao_futura = round(previsao_futura)

            # --- G. Adicionar a Previsão Futura ao DataFrame ---
            # previsao_futura agora também é um float
            df_linha_futura = pd.DataFrame({
                'ano_previsao': [ano_max + 1],
                'previsao_homicidios': [previsao_futura]
            })
            df_resultado_grupo = pd.concat([df_resultado_grupo, df_linha_futura], ignore_index=True)

            # --- H. Adicionar as colunas de erro (são iguais para todas as linhas) ---
            # Todos os cálculos são feitos com floats, mantendo a precisão
            df_resultado_grupo['margem_erro_k'] = k
            df_resultado_grupo['previsao_min'] = df_resultado_grupo['previsao_homicidios'] - k
            df_resultado_grupo['previsao_max'] = df_resultado_grupo['previsao_homicidios'] + k
            df_resultado_grupo['correlacao_temporal_r'] = r_temporal
            df_resultado_grupo['erro_padrao_se'] = se
            df_resultado_grupo['fator_penalidade_fr'] = f_r
            df_resultado_grupo['n_anos_dados'] = n
            
            # --- I. Filtrar para os anos que você solicitou ---
            anos_desejados = [2022, 2023, 2024, 2025]
            # Adiciona .copy() para evitar um SettingWithCopyWarning
            df_resultado_filtrado = df_resultado_grupo[df_resultado_grupo['ano_previsao'].isin(anos_desejados)].copy()
            
            # --- J. (NOVO) ARREDONDAR E AJUSTAR SAÍDAS FINAIS ---
            
            # Lista das colunas que você quer como inteiros não-negativos
            colunas_para_inteiro = ['previsao_homicidios', 'previsao_min', 'previsao_max']

            for col in colunas_para_inteiro:
                # 1. Arredonda para o inteiro mais próximo (.round())
                # 2. Garante que o valor mínimo seja 0 (.apply(lambda x: max(0, x)))
                # 3. Preenche qualquer NaN com 0 (caso 'k' seja NaN, por exemplo)
                # 4. Converte o tipo da coluna para inteiro (.astype(int))
                df_resultado_filtrado[col] = df_resultado_filtrado[col].round().apply(lambda x: max(0, x)).fillna(0).astype(int)

            # Opcional: Se quiser arredondar as colunas estatísticas (k, r, se) 
            # para 4 casas decimais para melhor visualização:
            col_stats = ['margem_erro_k', 'correlacao_temporal_r', 'erro_padrao_se', 'fator_penalidade_fr']
            df_resultado_filtrado[col_stats] = df_resultado_filtrado[col_stats].round(4)
            
            return df_resultado_filtrado
        def calcular_previsao_temporal_por_municipio(self,df_datasus, df_eventos):
           
            
            # --- Etapa 1: Merge (sem alterações) ---
            df_datasus["mes"] = df_datasus["mes_nome"].astype(str)
            df_eventos["mes"] = df_eventos["mes"].astype(str)
            df_datasus["ano"] = df_datasus["ano"].astype(int)
            df_eventos["ano"] = df_eventos["ano"].astype(int)
            
            df_merged = pd.merge(
                df_datasus,
                df_eventos,
                on=["municipio", "mes", "ano"],
                how="inner" 
            )
            
            df_merged = df_merged.dropna(subset=["mortes_no_mes_municipio", "vitimas_homicidio_no_mes_municipio"])
            df_merged["mortes_no_mes_municipio"] = df_merged["mortes_no_mes_municipio"].astype(float)
            df_merged["vitimas_homicidio_no_mes_municipio"] = df_merged["vitimas_homicidio_no_mes_municipio"].astype(float)

            # --- Etapa 2: Agregar Dados Mensais para Anuais (sem alterações) ---
            print("Agregando dados mensais para anuais...")
            df_anual = df_merged.groupby(['municipio', 'ano']).agg(
                total_mortes_ano=('mortes_no_mes_municipio', 'sum'),
                total_vitimas_ano=('vitimas_homicidio_no_mes_municipio', 'sum')
            ).reset_index()

            # --- Etapa 3: Filtrar Municípios com Dados Insuficientes (sem alterações) ---
            group_sizes = df_anual.groupby('municipio').size()
            municipios_validos = group_sizes[group_sizes > 2].index
            
            if len(municipios_validos) == 0:
                print("Erro: Nenhum município tem dados suficientes ( > 2 anos) para calcular a previsão.")
                return pd.DataFrame()
                
            df_anual_filtrado = df_anual[df_anual['municipio'].isin(municipios_validos)]
            print(f"Calculando previsões para {len(municipios_validos)} municípios...")

            # --- Etapa 4: Aplicar a função de previsão (sem alterações) ---
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                df_previsoes = df_anual_filtrado.groupby('municipio').apply(self.calcular_previsao_para_grupo)

            df_previsoes = df_previsoes.reset_index()
            
            # Remove o índice antigo do 'apply' se ele existir
            if 'level_1' in df_previsoes.columns:
                df_previsoes = df_previsoes.drop(columns=['level_1'])
                
            # Altera a ordenação para ser mais lógica
            df_previsoes = df_previsoes.sort_values(by=['municipio', 'ano_previsao'], ascending=True)
            
            print("Cálculo de previsão concluído.")
            return df_previsoes
        
        def calcula_dados_reais(self):
            df_eventos = pd.read_sql(
                "SELECT uf, municipio, mes, ano, vitimas FROM eventos", 
                con=engine
            )
            df_anual = df_eventos.groupby(['municipio','ano']).agg(total_vitimas_ano = ('vitimas','sum') ).reset_index()
            return df_anual

        def comparar_previsoes_com_reais(self):
            
            print("Iniciando comparação...")

            # --- 1. Carregar os Dados ---
            try:
                df_previsoes = pd.read_sql(
                    "SELECT * FROM previsoes", 
                    con=engine
                )
                df_reais = pd.read_sql(
                    "SELECT * FROM dados_reais_anuais", 
                    con=engine
                )
            except Exception as e:
                print(f"Erro ao ler tabelas do banco: {e}")
                return pd.DataFrame() # Retorna DF vazio em caso de erro

            if df_previsoes.empty:
                print("A tabela 'previsoes' está vazia. Não há nada para comparar.")
                return pd.DataFrame()
            if df_reais.empty:
                print("A tabela 'dados_reais_anuais' está vazia. Não há nada para comparar.")
                return pd.DataFrame()

            # --- 2. Unir (Merge) os DataFrames ---
            
            # Renomeia a coluna de ano da previsão para ser igual à coluna de ano real
            df_previsoes_clean = df_previsoes.rename(columns={'ano_previsao': 'ano'})

            # Une as tabelas usando 'municipio' e 'ano' como chaves
            df_comparativo = pd.merge(
                df_previsoes_clean,
                df_reais,
                on=['municipio', 'ano'],
                how='inner' # 'inner' garante que só teremos linhas com dados reais E previsão
            )

            if df_comparativo.empty:
                print("Nenhum dado real e de previsão correspondente (municipio/ano) foi encontrado.")
                return df_comparativo

            # --- 3. Criar a Classificação ---
            
            # Lista de condições
            conditions = [
                # 1. O valor real foi MAIOR que a previsão máxima?
                (df_comparativo['total_vitimas_ano'] > df_comparativo['previsao_max']),
                
                # 2. O valor real foi MENOR que a previsão mínima?
                (df_comparativo['total_vitimas_ano'] < df_comparativo['previsao_min'])
            ]

            # Lista de resultados (na mesma ordem das condições)
            choices = [
                'Acima do Previsto',
                'Abaixo do Previsto'
            ]

            # Aplica a lógica
            df_comparativo['classificacao'] = np.select(
                conditions, 
                choices, 
                default='Dentro do Previsto' # Se nenhuma condição for atendida
            )
            
            print(f"Comparação concluída. {len(df_comparativo)} linhas classificadas.")
            return df_comparativo