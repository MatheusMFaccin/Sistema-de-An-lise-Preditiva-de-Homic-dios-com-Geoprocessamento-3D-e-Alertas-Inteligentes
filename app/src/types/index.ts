export interface Municipio {
  id: number
  nome: string
  uf: string
}

export interface Grafico {
  labels_anos: number[]
  data_reais: number[]
  data_previsoes: number[]
}

export interface TabelaItem {
  ano: number
  total_vitimas_ano: number | null
  previsao_homicidios: number
  classificacao: string
  margem_erro_k: number | null
}

export interface MunicipioResponse {
  municipio: Municipio
  grafico: Grafico
  tabela: TabelaItem[]
}

export interface ClassificacaoItem {
  municipio: string
  classificacao: string
}

export interface ClassificacaoResponse {
  [ano: string]: ClassificacaoItem[]
}

export interface StatsCard {
  label: string
  value: string
  trend: 'up' | 'down' | 'flat'
  trendText: string
}

export type ClassificacaoLabel = 'Abaixo do Previsto' | 'Dentro do Previsto' | 'Acima do Previsto'
