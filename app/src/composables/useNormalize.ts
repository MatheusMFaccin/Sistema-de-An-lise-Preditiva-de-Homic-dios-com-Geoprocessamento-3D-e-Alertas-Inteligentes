export function normalizar(texto: string | undefined | null): string {
  if (!texto) return ''
  return String(texto)
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

export function fazerSlug(nome: string): string {
  return normalizar(nome).replace(/\s+/g, '-')
}
