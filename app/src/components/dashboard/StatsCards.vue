<script setup lang="ts">
import { computed } from 'vue'
import type { MunicipioResponse, StatsCard } from '@/types'

const props = defineProps<{ dados: MunicipioResponse }>()

const stats = computed<StatsCard[]>(() => {
  const d = props.dados
  const reais = d.grafico.data_reais
  const previsoes = d.grafico.data_previsoes
  const anos = d.grafico.labels_anos
  const n = reais.length

  const total = reais.reduce((a: number, b: number) => a + b, 0)
  const media = (total / n).toFixed(1)
  const ultimo = reais[n - 1]
  const penultimo = reais[n - 2]
  const ultimaPrev = previsoes[n - 1]
  const ultimoAno = anos[n - 1]

  const tendencia: 'up' | 'down' | 'flat' =
    ultimo > penultimo ? 'up' : ultimo < penultimo ? 'down' : 'flat'

  const trendText =
    tendencia === 'up'
      ? `Aumento vs ${penultimo} do ano anterior`
      : tendencia === 'down'
        ? `Queda vs ${penultimo} do ano anterior`
        : 'Estavel'

  return [
    { label: 'Total de Vitimas', value: String(total), trend: tendencia, trendText },
    { label: 'Media Anual', value: media, trend: 'flat', trendText: 'Casos por ano' },
    { label: `Ultimo Ano (${ultimoAno})`, value: String(ultimo), trend: tendencia, trendText: `vs ${penultimo} do ano anterior` },
    { label: 'Ultima Previsao', value: ultimaPrev.toFixed(0), trend: 'flat', trendText: `Modelo para ${ultimoAno}` },
  ]
})
</script>

<template>
  <div class="stats-grid">
    <div v-for="(s, i) in stats" :key="i" class="stat-card">
      <div class="stat-label">{{ s.label }}</div>
      <div class="stat-value">{{ s.value }}</div>
      <div class="stat-trend" :class="s.trend">
        <span class="stat-icon">{{ s.trend === 'up' ? '↑' : s.trend === 'down' ? '↓' : '→' }}</span>
        {{ s.trendText }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  background: #fff; border-radius: 12px; padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06); border: 1px solid rgba(0,0,0,0.04);
  transition: all 0.2s;
}
.stat-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); transform: translateY(-1px); }
.stat-label { font-size: 12px; font-weight: 600; color: #8b8fa3; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.stat-value { font-size: 28px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; }
.stat-trend { font-size: 12px; font-weight: 500; margin-top: 4px; display: flex; align-items: center; gap: 4px; }
.stat-trend.up { color: #22c55e; }
.stat-trend.down { color: #ef4444; }
.stat-trend.flat { color: #8b8fa3; }
.stat-icon { font-size: 16px; }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .stat-value { font-size: 22px; }
}
</style>
