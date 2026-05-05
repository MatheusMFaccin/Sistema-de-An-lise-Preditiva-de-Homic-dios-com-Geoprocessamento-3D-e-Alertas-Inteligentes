# 📊 Análise de Segurança Pública — DataSUS vs Eventos (RS)

Sistema de análise e previsão de homicídios no Rio Grande do Sul, cruzando dados do **DataSUS** (mortalidade por causas externas) com dados de **eventos de segurança pública** (tentativas de homicídio). O projeto utiliza regressão linear para gerar previsões por município e exibe os resultados em um **mapa 3D interativo** com CesiumJS.

---

## 📋 1. Pré-requisitos

Certifique-se de ter instalado em sua máquina:

- [Git](https://git-scm.com/)
- [Docker e Docker Compose](https://www.docker.com/) (para o banco de dados e serviços)
- [Python 3.10+](https://www.python.org/)

---

## 🛠️ 2. Instalação

### 2.1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/seu-projeto.git
cd seu-projeto
```

### 2.2. Crie o Ambiente Virtual (Recomendado)

Isso isola as bibliotecas do projeto do seu sistema global.

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 2.3. Instale as Dependências

```bash
pip install -r requirements.txt
```

> **Nota:** Se você ainda não criou esse arquivo, gere-o com `pip freeze > requirements.txt`.

---

## ⚙️ 3. Configuração de Ambiente (.env)

O projeto utiliza variáveis de ambiente para credenciais sensíveis.

Crie um arquivo chamado `.env` na raiz do projeto e ajuste conforme necessário:

```ini
# .env
# Ajuste usuário, senha, host e nome do banco conforme seu Docker
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/nome_do_banco
```

---

## 🐳 4. Subindo o Banco de Dados

Utilizamos Docker para rodar o PostgreSQL:

```bash
docker-compose up --build -d
```

Aguarde alguns segundos para o banco iniciar.

---

## 🔄 5. Migrações (Alembic)

Agora precisamos criar as tabelas (`eventos`, `datasus`, `previsoes`, `comparativo_previsoes`, etc.) no banco de dados usando o Alembic.

1. Entre no contêiner do FastAPI:

```bash
docker exec -it <id_do_conteiner> bash
```

2. Certifique-se de que está na raiz do projeto e execute as migrações:

```bash
alembic upgrade head
alembic revision --autogenerate -m "criando as tabelas do banco"
alembic upgrade head
```

Se não houver erros, seu banco de dados está pronto e estruturado.

---

## 📊 6. Executando a Carga e Análise de Dados

Para popular o banco de dados, gerar previsões e salvar os comparativos, entre no contêiner do FastAPI e execute:

```bash
docker exec -it <id_do_conteiner> bash
python scripts/insert_data.py
```

### O que este script fará (resumo):

1. Lerá os arquivos CSV/TXT originais (eventos de segurança e dados do DataSUS)
2. Limpará e normalizará os dados (remoção de acentos, padronização de nomes)
3. Sincronizará a tabela de municípios
4. Inserirá os dados brutos nas tabelas `eventos` e `datasus`
5. Calculará as previsões (Regressão Linear) e salvará em `previsoes`
6. Comparará os dados reais vs previstos e salvará em `comparativo_previsoes`

---

## 📐 7. Metodologia Estatística

### 7.1. Correlação Temporal (r)

A **correlação de Pearson** é utilizada para medir a relação linear entre duas variáveis numéricas por município: o **total anual de mortes** (DataSUS) e o **total anual de vítimas de tentativas de homicídio** (eventos de segurança).

#### Como é calculada

Para cada município, os dados mensais são primeiro **agregados por ano**, resultando em dois vetores anuais:

- `total_mortes_ano` — soma de mortes (DataSUS) no ano
- `total_vitimas_ano` — soma de vítimas de eventos no ano

A correlação é calculada com o método `.corr()` do Pandas (equivalente ao coeficiente de Pearson):

```python
r_temporal = Y_train_vitimas.corr(Y_train_mortes)
```

A fórmula matemática subjacente é:

$$
r = \frac{\sum_{i=1}^{n}(x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{n}(x_i - \bar{x})^2 \cdot \sum_{i=1}^{n}(y_i - \bar{y})^2}}
$$

Onde:
- **$x$** = total de vítimas de eventos por ano
- **$y$** = total de mortes DataSUS por ano
- **$n$** = número de anos com dados disponíveis

#### Interpretação do r

| Valor de \|r\| | Interpretação |
|:---:|:---|
| 0.9 – 1.0 | Correlação muito forte |
| 0.7 – 0.9 | Correlação forte |
| 0.5 – 0.7 | Correlação moderada |
| 0.0 – 0.5 | Correlação fraca |

> **Observação:** A correlação só é calculada quando ambas as variáveis possuem variância maior que zero (ou seja, há variação nos dados ao longo dos anos). Caso contrário, o valor de `r` será `NaN`.

---

### 7.2. Margem de Erro (k)

A margem de erro **k** define o intervalo de confiança da previsão: `[previsão - k, previsão + k]`. Ela é composta por dois fatores:

#### 7.2.1. Erro Padrão da Regressão (SE)

O erro padrão mede o desvio médio entre os valores reais e os valores previstos pelo modelo de regressão linear:

$$
SE = \sqrt{\frac{\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}{n - 2}}
$$

Onde:
- **$y_i$** = valor real (total de vítimas no ano)
- **$\hat{y}_i$** = valor previsto pelo modelo de regressão linear
- **$n$** = número de anos de dados
- **$n - 2$** = graus de liberdade (ajuste para regressão linear simples)

> O SE só é calculado quando há mais de 2 anos de dados (`n > 2`). Caso contrário, será `NaN`.

#### 7.2.2. Fator de Penalidade ($f_r$)

O fator de penalidade ajusta a margem de erro com base na **qualidade da correlação** entre as duas fontes de dados. Quanto mais fraca a correlação, maior a margem de erro aplicada:

| Valor de \|r\| | Fator de Penalidade ($f_r$) |
|:---:|:---:|
| ≥ 0.9 | 1.0 |
| ≥ 0.7 | 1.5 |
| ≥ 0.5 | 2.0 |
| < 0.5 ou NaN | 2.5 |

#### 7.2.3. Cálculo Final

A margem de erro é o produto dos dois componentes:

$$
k = SE \times f_r
$$

Isso resulta no **intervalo de previsão**:

$$
\text{previsão}_{min} = \text{previsão} - k
$$
$$
\text{previsão}_{max} = \text{previsão} + k
$$

#### 7.2.4. Classificação

Após comparar os dados reais com a previsão, cada município recebe uma **classificação** para o ano:

| Classificação | Condição |
|:---|:---|
| **Acima do Previsto** | `total_vitimas_ano > previsao_max` |
| **Abaixo do Previsto** | `total_vitimas_ano < previsao_min` |
| **Dentro do Previsto** | `previsao_min ≤ total_vitimas_ano ≤ previsao_max` |

---

### 7.3. Modelo de Regressão Linear

O modelo utiliza **regressão linear simples** (via `sklearn.LinearRegression`) para prever o número de vítimas de homicídio, usando o **ano** como variável independente (X) e o **total de vítimas** como variável dependente (Y).

- **Treinamento:** O modelo é ajustado com os dados históricos de cada município (anos 2019–2024)
- **Previsão futura:** Após o ajuste, o modelo prevê o valor para o **próximo ano** (ano máximo + 1)
- **Filtro:** Apenas municípios com **mais de 2 anos** de dados cruzados (DataSUS + Eventos) são incluídos na análise
- **Anos de interesse:** As previsões são filtradas para os anos 2022, 2023, 2024 e 2025

---

## 🗺️ 8. Geração do Mapa Interativo

### 8.1. Obtenção do GeoJSON via QGIS

O mapa de municípios do Rio Grande do Sul foi gerado a partir de dados geoespaciais oficiais e processado no **QGIS** (versão 3.40.5 - Bratislava).

#### Processo de criação do GeoJSON

1. **Fonte dos dados:** Foi utilizado o shapefile oficial dos municípios do RS, disponibilizado pelo IBGE (malha municipal)

2. **Importação no QGIS:** O shapefile foi carregado no QGIS como uma camada vetorial

3. **Sistema de Referência de Coordenadas:** O arquivo utiliza o sistema **SIRGAS 2000** (EPSG:4674), que é o sistema geodésico oficial do Brasil:
   ```
   +proj=longlat +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +no_defs
   ```

4. **Exportação para GeoJSON:** A camada foi exportada pelo QGIS no formato GeoJSON (`tfg_oficial.geojson`), preservando a propriedade `NM_MUN` (nome do município) que é essencial para o cruzamento com os dados de classificação

5. **Resultado:** Um arquivo GeoJSON (~24 MB) contendo os polígonos de todos os municípios do Rio Grande do Sul, com seus contornos geográficos e metadados

### 8.2. Renderização com CesiumJS

O mapa interativo é renderizado no frontend usando **CesiumJS**, uma biblioteca JavaScript para visualização 3D de dados geoespaciais.

#### Fluxo de renderização

1. **Backend (Django):** A view `mapa` consulta a tabela `comparativo_previsoes` no banco de dados e organiza os dados de classificação por ano. Esses dados são serializados em JSON e enviados ao template:

   ```python
   # views.py
   dados_classificacao = ComparativoPrevisoes.objects.values(
       'municipio__nome', 'classificacao', 'ano'
   )
   ```

2. **Carregamento do GeoJSON:** O CesiumJS carrega o arquivo `tfg_oficial.geojson` como uma `GeoJsonDataSource`, criando entidades (polígonos) para cada município:

   ```javascript
   const geojsonUrl = "{% static 'mapa/geojson/tfg_oficial.geojson' %}";
   Cesium.GeoJsonDataSource.load(geojsonUrl).then(dataSource => {
       viewer.dataSources.add(dataSource);
       viewer.zoomTo(dataSource);
   });
   ```

3. **Matching por nome:** Para cada polígono do GeoJSON, o sistema extrai a propriedade `NM_MUN` e compara (após normalização — remoção de acentos e conversão para minúsculas) com os dados de classificação vindos do banco

4. **Coloração dinâmica:** Cada município recebe uma cor baseada na sua classificação para o ano selecionado:

   | Cor | Classificação |
   |:---:|:---|
   | 🟢 Verde | Abaixo do Previsto |
   | 🔴 Vermelho | Acima do Previsto |
   | 🔵 Azul | Dentro do Previsto |
   | ⚪ Cinza | Sem dados / Padrão |

5. **Seletor de ano:** Um dropdown permite ao usuário alternar entre os anos disponíveis, atualizando as cores do mapa em tempo real sem recarregar a página

---

## 🌐 9. Executando a Aplicação Web

1. Entre na pasta `app` pelo terminal

2. Execute os seguintes comandos:

```bash
docker-compose up --build -d

docker exec -it <id_do_conteiner> bash

python manage.py inspectdb consultas > models.py

exit
```

3. Acesse a URL: [http://localhost:8001/mapa/](http://localhost:8001/mapa/)

---

## 🏗️ 10. Arquitetura do Projeto

```
tcc_final/
├── api/                          # Backend FastAPI (ETL + Análise)
│   ├── scripts/
│   │   ├── insert_data.py        # Script principal de ETL
│   │   ├── correlacao.py         # Cálculos de correlação e previsão
│   │   ├── table_scripts.py      # Limpeza de arquivos
│   │   ├── eventos20XX.csv       # Dados de eventos de segurança (por ano)
│   │   └── datasus20XX.txt       # Dados de mortalidade do DataSUS (por ano)
│   ├── models/                   # Models SQLAlchemy
│   │   ├── municipio.py
│   │   ├── evento.py
│   │   ├── datasus.py
│   │   ├── previsao.py
│   │   ├── dados_reais.py
│   │   └── ComparativoPrevisao.py
│   ├── db/                       # Configuração do banco de dados
│   ├── alembic/                  # Migrações do banco
│   ├── docker-compose.yml
│   └── Dockerfile
│
├── app/                          # Frontend Django (Visualização)
│   ├── mapa/
│   │   ├── views.py              # View que monta os dados de classificação
│   │   ├── templates/
│   │   │   └── contato.html      # Template com mapa CesiumJS
│   │   └── static/mapa/geojson/
│   │       └── tfg_oficial.geojson  # Polígonos dos municípios do RS
│   ├── consultas/
│   │   └── models.py             # Models Django (espelhados do PostgreSQL)
│   ├── docker-compose.yml
│   └── Dockerfile
│
└── README.md
```

---

## 📚 Tecnologias Utilizadas

| Tecnologia | Uso |
|:---|:---|
| **Python 3.10+** | Linguagem principal |
| **FastAPI** | API backend para ETL |
| **Django** | Frontend web (mapa) |
| **PostgreSQL** | Banco de dados relacional |
| **SQLAlchemy + Alembic** | ORM e migrações |
| **Pandas** | Manipulação e limpeza de dados |
| **scikit-learn** | Regressão Linear |
| **NumPy** | Cálculos numéricos |
| **CesiumJS** | Mapa 3D interativo |
| **QGIS** | Geração do GeoJSON a partir de shapefiles |
| **Docker** | Containerização dos serviços |
