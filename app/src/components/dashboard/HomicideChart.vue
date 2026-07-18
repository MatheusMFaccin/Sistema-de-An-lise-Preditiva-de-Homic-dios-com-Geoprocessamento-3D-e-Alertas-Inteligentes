<script setup lang="ts">
import { ref, shallowRef, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { MunicipioResponse } from '@/types'

const props = defineProps<{ dados: MunicipioResponse }>()

const chartEl = ref<HTMLDivElement>()
const chart = shallowRef<echarts.ECharts>()

function mountChart() {
  if (!chartEl.value) return
  chart.value = echarts.init(chartEl.value)
  chart.value.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#eef0f4',
      borderWidth: 1,
      textStyle: { color: '#1a1a2e', fontSize: 12 },
      formatter: (params: any) => {
        let s = `<strong style="font-size:14px;">${params[0].axisValue}</strong><br/>`
        params.forEach((p: any) => {
          s += `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${p.color};margin-right:8px;"></span>`
          s += `${p.seriesName}: <strong>${p.value}</strong><br/>`
        })
        return s
      },
    },
    legend: {
      data: ['Dados Reais (SINESP/DATASUS)', 'Previsao do Modelo'],
      top: 0,
      textStyle: { fontSize: 12, color: '#4a4d5e' },
    },
    grid: { left: 60, right: 24, top: 48, bottom: 40 },
    xAxis: {
      type: 'category',
      data: props.dados.grafico.labels_anos,
      axisLine: { lineStyle: { color: '#eef0f4' } },
      axisLabel: { color: '#8b8fa3', fontWeight: 600 },
      axisTick: { show: false },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      name: 'Homicidios',
      nameTextStyle: { color: '#8b8fa3', fontSize: 11 },
      axisLine: { show: false },
      axisLabel: { color: '#8b8fa3' },
      splitLine: { lineStyle: { color: '#f0f2f5', type: 'dashed' } },
    },
    series: [
      {
        name: 'Dados Reais (SINESP/DATASUS)',
        type: 'line',
        data: props.dados.grafico.data_reais,
        smooth: true,
        lineStyle: { color: '#667eea', width: 3 },
        itemStyle: { color: '#667eea' },
        symbol: 'circle',
        symbolSize: 8,
        areaStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(102,126,234,0.25)' },
              { offset: 1, color: 'rgba(102,126,234,0.01)' },
            ],
          },
        },
      },
      {
        name: 'Previsao do Modelo',
        type: 'line',
        data: props.dados.grafico.data_previsoes,
        smooth: true,
        lineStyle: { color: '#f472b6', width: 2.5, type: 'dashed' },
        itemStyle: { color: '#f472b6' },
        symbol: 'diamond',
        symbolSize: 8,
      },
    ],
  })
}

onMounted(mountChart)
onUnmounted(() => {
  chart.value?.dispose()
  window.removeEventListener('resize', handleResize)
})

function handleResize() { chart.value?.resize() }
window.addEventListener('resize', handleResize)
</script>

<template>
  <div class="chart-card">
    <div class="chart-header">
      <div>
        <div class="chart-title">Evolucao de Homicidios</div>
        <div class="chart-subtitle">Dados reais vs previsao do modelo por ano</div>
      </div>
    </div>
    <div ref="chartEl" style="width:100%;height:380px"></div>
  </div>
</template>

<style scoped>
.chart-card {
  background: #fff; border-radius: 12px; padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 24px;
  border: 1px solid rgba(0,0,0,0.04);
}
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.chart-title { font-size: 16px; font-weight: 600; color: #1a1a2e; }
.chart-subtitle { font-size: 12px; color: #8b8fa3; margin-top: 2px; }
</style>
