# Sistema de Analise Preditiva de Homicidios com Geoprocessamento 3D

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Frontend | Vue 3 + TypeScript + Vite |
| Mapa 3D | CesiumJS 1.105 (CDN) |
| Backend | FastAPI (Python 3.11) |
| Banco | PostgreSQL 15 |
| Container | Docker + Docker Compose |

## Estrutura

```
.
├── docker-compose.yml       # Orquestracao dos servicos
├── api/                     # FastAPI — backend e carga de dados
│   ├── Dockerfile
│   ├── startup.sh           # Script de inicializacao (migra + popula + inicia)
│   ├── main.py
│   ├── models/              # SQLAlchemy models (Municipio, ComparativoPrevisao)
│   ├── api/v1/endpoints/    # Rotas da API
│   ├── scripts/             # Scripts de carga e correlacao
│   ├── .env                 # Variaveis de ambiente (NAO comitar)
│   └── requirements.txt
├── app/                     # Vue 3 + TypeScript frontend
│   ├── Dockerfile           # Build Vite + serve Nginx
│   ├── nginx.conf           # Proxy /api → FastAPI
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html           # Carrega CesiumJS CDN
│   ├── public/
│   │   └── mapa/geojson/
│   │       └── tfg_oficial.geojson   # Malha dos municipios do RS
│   └── src/
│       ├── main.ts                  # Entry point
│       ├── App.vue                  # Root component
│       ├── types/index.ts           # TypeScript interfaces
│       ├── composables/
│       │   ├── useApi.ts            # Chamadas a API (fetchClassificacao, fetchMunicipio)
│       │   └── useNormalize.ts      # Normalizacao de strings
│       ├── components/
│       │   ├── map/
│       │   │   ├── CesiumGlobe.vue  # Globo 3D, GeoJSON, handlers de clique/hover
│       │   │   ├── YearSelector.vue # Seletor de ano estilizado
│       │   │   └── LegendPanel.vue  # Painel de legenda
│       │   └── dashboard/
│       │       ├── StatsCards.vue   # 4 cards de estatisticas
│       │       ├── HomicideChart.vue # Grafico ECharts (reais vs previsao)
│       │       └── DataTable.vue    # Tabela detalhada com badges
│       ├── views/
│       │   ├── MapView.vue          # Pagina do globo
│       │   └── MunicipioView.vue    # Pagina de dashboard por municipio
│       └── router/index.ts          # Vue Router com lazy-loading
└── .gitignore
```

## Requisitos

- **Docker** e **Docker Compose**
- Portas livres: `8081` (frontend), `8000` (API), `5432` (PostgreSQL)
- Arquivo `.env` configurado em `api/.env`

### Exemplo de `api/.env`

```env
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=nome_do_banco
DATABASE_URL=postgresql://seu_usuario:sua_senha@db:5432/nome_do_banco
CESIUM_TOKEN=seu_token_cesium_ion
DEBUG=false
```

`DATABASE_URL` pode ser qualquer dialect suportado pelo SQLAlchemy + psycopg2.

## Como executar

```bash
# 1. Clone o repositorio
git clone https://github.com/MatheusMFaccin/Sistema-de-Analise-Preditiva-de-Homicidios-com-Geoprocessamento-3D-e-Alertas-Inteligentes.git
cd Sistema-de-Analise-Preditiva-de-Homicidios-com-Geoprocessamento-3D-e-Alertas-Inteligentes

# 2. Configure o .env
cp api/.env.example api/.env
# Edite api/.env com suas credenciais e token Cesium Ion

# 3. Suba os containers
docker compose up -d
```

Na primeira execucao o backend roda:
1. Migracoes Alembic (criacao das tabelas)
2. Carga de dados via `insert_data.py` (DATASUS + eventos)
3. Correlacao e previsao para cada ano
4. Inicia o servidor FastAPI na porta `8000`

O frontend so inicia depois que o healthcheck da API retorna `healthy`.

## Acessar

| URL | Descricao |
|-----|-----------|
| http://localhost:8081/ | Mapa 3D Cesium com municipios coloridos |
| http://localhost:8081/municipio/rondinha/ | Dashboard do municipio (exemplo) |
| http://localhost:8081/api/v1/config/ | API — token Cesium |
| http://localhost:8081/api/v1/mapa/dados-classificacao/ | API — dados de classificacao |
| http://localhost:8081/api/v1/municipios/rondinha/ | API — detalhes do municipio |

## Funcionalidades

- **Globo 3D** com textura de relevo/satelite e 505 municipios do RS
- **Coloracao** por classificacao: verde (abaixo do previsto), vermelho (acima), azul (dentro), cinza (sem dados)
- **Seletor de ano** (2019–2024)
- **Clique no municipio** → dashboard com grafico ECharts + tabela detalhada
- **Stats cards** com total de vitimas, media, ultimo ano, ultima previsao
- **Tendencia** visual (aumento, queda ou estavel)
- **Otimizado para GPU fraca** (EllipsoidTerrainProvider, sem HDR/skybox opcionais)

## Comandos uteis

```bash
# Parar tudo
docker compose down

# Rebuildar o frontend apos alteracoes
docker compose build vue-app && docker compose up -d vue-app

# Rebuildar o backend apos alteracoes
docker compose build fastapi-app && docker compose up -d fastapi-app

# Ver logs
docker compose logs -f vue-app
docker compose logs -f fastapi-app

# Status dos containers
docker compose ps
```

## API Endpoints

### `GET /api/v1/config`

Retorna o token Cesium Ion e metadados do projeto.

### `GET /api/v1/mapa/dados-classificacao`

Dados de classificacao agrupados por ano para colorir o mapa.

```json
{
  "2024": [
    { "municipio": "PORTO ALEGRE", "classificacao": "Dentro do Previsto" },
    ...
  ]
}
```

### `GET /api/v1/municipios/{slug}`

Dados detalhados de um municipio: grafico e tabela.

```json
{
  "municipio": { "id": 1, "nome": "PORTO ALEGRE", "uf": "RS" },
  "grafico": {
    "labels_anos": [2019, 2020, 2021, 2022, 2023, 2024],
    "data_reais": [350, 380, 320, 300, 280, 260],
    "data_previsoes": [340, 360, 330, 310, 290, 270]
  },
  "tabela": [
    { "ano": 2019, "total_vitimas_ano": 350, "previsao_homicidios": 340.0, "classificacao": "Dentro do Previsto", "margem_erro_k": 0.5 }
  ]
}
```
