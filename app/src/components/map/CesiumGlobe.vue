<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { normalizar, fazerSlug } from '@/composables/useNormalize'
import { fetchClassificacao, fetchConfig } from '@/composables/useApi'
import type { ClassificacaoResponse } from '@/types'

const router = useRouter()
const API_BASE = window.location.origin

const anosDisponiveis = ref<string[]>([])
const anoSelecionado = ref('')
const legendaAberta = ref(false)
const cesiumToken = ref('')

let viewer: any = null
let entidades: any[] = []
let dadosPorAno: ClassificacaoResponse = {}

const CORES: Record<string, any> = {}

function initCores() {
  const C = (window as any).Cesium
  CORES['Abaixo do Previsto'] = C.Color.GREEN.withAlpha(0.85)
  CORES['Acima do Previsto'] = C.Color.RED.withAlpha(0.75)
  CORES['Dentro do Previsto'] = C.Color.BLUE.withAlpha(0.75)
  CORES['PADRAO'] = C.Color.GRAY.withAlpha(0.4)
}

function pintar() {
  if (!viewer || !anoSelecionado.value || !dadosPorAno[anoSelecionado.value]) return
  const mapa = new Map<string, string>()
  for (const item of dadosPorAno[anoSelecionado.value]) {
    const m = normalizar(item.municipio)
    if (m) mapa.set(m, item.classificacao)
  }
  for (const e of entidades) {
    const prop = e.properties?.NM_MUN
    if (!prop || !e.polygon) continue
    const nome = normalizar(prop.getValue())
    const cls = mapa.get(nome)
    e.polygon.material = CORES[cls!] ?? CORES['PADRAO']
    e.polygon.outline = true
    e.polygon.outlineColor = (window as any).Cesium.Color.GHOSTWHITE.withAlpha(0.5)
  }
  viewer.scene.requestRender()
}

async function carregarCesium(containerId: string) {
  const C = (window as any).Cesium
  if (!C) { console.error('Cesium indisponivel'); return }

  const token = cesiumToken.value || (await fetchConfig()).cesium_token
  C.Ion.defaultAccessToken = token

  viewer = new C.Viewer(containerId, {
    infoBox: false, selectionIndicator: false, shouldAnimate: false,
    sceneModePicker: false, navigationHelpButton: false, homeButton: false,
    orderIndependentTranslucency: false,
    terrainProvider: new C.EllipsoidTerrainProvider({}),
    contextOptions: { webgl: { failIfMajorPerformanceCaveat: false } },
  })

  viewer.scene.fog.enabled = false
  viewer.scene.highDynamicRange = false
  viewer.scene.fxaaEnabled = false

  const sc = viewer.scene.screenSpaceCameraController
  sc.enableCollisionDetection = false
  sc.minimumZoomDistance = 5000
  sc.maximumZoomDistance = 10000000

  initCores()

  // GeoJSON
  try {
    const ds = await C.GeoJsonDataSource.load(`${API_BASE}/mapa/geojson/tfg_oficial.geojson`)
    viewer.dataSources.add(ds)
    entidades = ds.entities.values

    if (anoSelecionado.value) pintar()

    viewer.camera.flyTo({
      destination: C.Cartesian3.fromDegrees(-53, -29.5, 1500000),
      orientation: { heading: 0, pitch: C.Math.toRadians(-40), roll: 0 },
      duration: 0,
    })

    // Click handler
    const clickHandler = new C.ScreenSpaceEventHandler(viewer.scene.canvas)
    clickHandler.setInputAction((m: any) => {
      const picked = viewer.scene.pick(m.position)
      if (C.defined(picked) && picked.id?.properties?.NM_MUN) {
        const nome = picked.id.properties.NM_MUN.getValue()
        router.push(`/municipio/${fazerSlug(nome)}`)
      }
    }, C.ScreenSpaceEventType.LEFT_CLICK)

    // Hover cursor
    const hoverHandler = new C.ScreenSpaceEventHandler(viewer.scene.canvas)
    hoverHandler.setInputAction((m: any) => {
      const picked = viewer.scene.pick(m.endPosition)
      viewer.scene.canvas.style.cursor =
        C.defined(picked) && picked.id?.properties?.NM_MUN ? 'pointer' : 'default'
    }, C.ScreenSpaceEventType.MOUSE_MOVE)
  } catch (e) {
    console.error('Falha ao carregar GeoJSON:', e)
  }
}

onMounted(async () => {
  try { dadosPorAno = await fetchClassificacao() } catch (e) { console.error(e) }
  anosDisponiveis.value = Object.keys(dadosPorAno).sort((a, b) => +b - +a)
  if (anosDisponiveis.value.length) anoSelecionado.value = anosDisponiveis.value[0]
  await carregarCesium('cesiumContainer')
})

onUnmounted(() => {
  viewer?.destroy()
  entidades = []
})

watch(anoSelecionado, () => pintar())
</script>

<template>
  <div class="mapa-page">
    <div id="cesiumContainer"></div>

    <!-- Topbar -->
    <div class="topbar">
      <div class="topbar-logo">RS</div>
      <div class="topbar-title">Mapa de Homicidios</div>
      <div class="topbar-divider"></div>
      <YearSelector
        v-if="anosDisponiveis.length"
        :anos="anosDisponiveis"
        :selected="anoSelecionado"
        @change="anoSelecionado = $event"
      />
      <div class="trigger" @click="legendaAberta = !legendaAberta">&#9432;</div>
    </div>

    <LegendPanel v-if="legendaAberta" @close="legendaAberta = false" />
  </div>
</template>

<style scoped>
.mapa-page { width: 100%; height: 100vh; position: relative; }
#cesiumContainer { width: 100%; height: 100%; }
.topbar {
  position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
  z-index: 1000; background: rgba(15,12,41,0.75);
  backdrop-filter: blur(16px); padding: 10px 20px; border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  display: flex; align-items: center; gap: 16px;
  color: #fff; font-size: 13px;
}
.topbar-logo {
  width: 30px; height: 30px; border-radius: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 12px;
}
.topbar-title { font-weight: 600; font-size: 14px; letter-spacing: -0.2px; white-space: nowrap; }
.topbar-divider { width: 1px; height: 24px; background: rgba(255,255,255,0.12); }
.trigger {
  width: 34px; height: 34px; border-radius: 10px;
  background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; color: rgba(255,255,255,0.8);
  cursor: pointer; transition: all 0.2s; user-select: none;
}
.trigger:hover { background: rgba(255,255,255,0.15); }

@media (max-width: 640px) {
  .topbar { top: 12px; padding: 8px 14px; gap: 10px; flex-wrap: wrap; justify-content: center; }
  .topbar-divider { display: none; }
}
</style>
