<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchMunicipio } from '@/composables/useApi'
import type { MunicipioResponse } from '@/types'
import StatsCards from '@/components/dashboard/StatsCards.vue'
import HomicideChart from '@/components/dashboard/HomicideChart.vue'
import DataTable from '@/components/dashboard/DataTable.vue'

const route = useRoute()
const router = useRouter()
const dados = ref<MunicipioResponse | null>(null)
const erro = ref('')
const carregando = ref(true)

onMounted(async () => {
  try {
    dados.value = await fetchMunicipio(route.params.slug as string)
  } catch (e) {
    erro.value = 'Municipio nao encontrado'
  } finally {
    carregando.value = false
  }
})

function voltar() { router.push('/') }
</script>

<template>
  <div class="dashboard">
    <!-- Top Bar -->
    <div class="topbar">
      <div class="topbar-left">
        <div class="topbar-logo">RS</div>
        <div>
          <h1 v-if="dados">{{ dados.municipio.nome }}</h1>
          <div class="sub">{{ dados?.municipio.uf ?? '' }} &middot; Dashboard de Homicidios</div>
        </div>
      </div>
      <button class="btn-voltar" @click="voltar">&larr; Voltar ao Mapa</button>
    </div>

    <div class="container">
      <div v-if="carregando" class="loading">
        <div class="spinner"></div> Carregando...
      </div>
      <div v-else-if="erro" class="erro">{{ erro }}</div>
      <template v-else-if="dados">
        <StatsCards :dados="dados" />
        <HomicideChart :dados="dados" />
        <DataTable :tabela="dados.tabela" />
      </template>
    </div>
  </div>
</template>

<style scoped>
* { box-sizing: border-box; }
.dashboard { font-family: 'Inter', sans-serif; background: #f0f2f5; min-height: 100vh; color: #1a1a2e; }
.topbar {
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #fff;
  padding: 0 32px; height: 64px; display: flex; align-items: center;
  justify-content: space-between; position: sticky; top: 0; z-index: 100;
  box-shadow: 0 2px 20px rgba(0,0,0,0.15);
}
.topbar-left { display: flex; align-items: center; gap: 16px; }
.topbar-logo {
  width: 32px; height: 32px; border-radius: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 14px;
}
h1 { font-size: 16px; font-weight: 600; letter-spacing: -0.3px; margin: 0; }
.sub { font-size: 12px; color: rgba(255,255,255,0.5); font-weight: 400; }
.btn-voltar {
  padding: 8px 18px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.08); color: #fff; cursor: pointer;
  font-size: 13px; font-weight: 500; transition: all 0.2s;
}
.btn-voltar:hover { background: rgba(255,255,255,0.15); }
.container { max-width: 1200px; margin: 0 auto; padding: 24px 32px; }
.loading, .erro {
  display: flex; align-items: center; justify-content: center;
  height: 200px; color: #8b8fa3; font-size: 14px;
}
.spinner {
  width: 28px; height: 28px; border: 3px solid #eef0f4;
  border-top-color: #667eea; border-radius: 50%;
  animation: spin 0.8s linear infinite; margin-right: 12px;
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .container { padding: 16px; }
  .topbar { padding: 0 16px; }
}
</style>
