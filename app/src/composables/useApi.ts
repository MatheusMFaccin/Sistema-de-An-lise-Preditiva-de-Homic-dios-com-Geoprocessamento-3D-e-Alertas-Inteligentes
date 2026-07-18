import type { MunicipioResponse, ClassificacaoResponse } from '@/types'

const API_BASE = window.location.origin

export async function fetchClassificacao(): Promise<ClassificacaoResponse> {
  const r = await fetch(`${API_BASE}/api/v1/mapa/dados-classificacao`)
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return r.json()
}

export async function fetchMunicipio(slug: string): Promise<MunicipioResponse> {
  const r = await fetch(`${API_BASE}/api/v1/municipios/${encodeURIComponent(slug)}`)
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return r.json()
}

export async function fetchConfig(): Promise<{ cesium_token: string }> {
  const r = await fetch(`${API_BASE}/api/v1/config`)
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return r.json()
}
