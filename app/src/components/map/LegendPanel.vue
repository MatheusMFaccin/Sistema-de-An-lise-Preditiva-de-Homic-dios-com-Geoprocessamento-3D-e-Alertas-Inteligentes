<script setup lang="ts">
const emit = defineEmits<{ (e: 'toggle'): void; (e: 'close'): void }>()
</script>

<template>
  <div class="legend-panel">
    <h3>Taxa de Homicidios</h3>
    <p class="sub">Classificacao por municipio</p>
    <ul>
      <li>
        <span class="cor-legenda" style="background:linear-gradient(135deg,#4ade80,#22c55e)"></span>
        Abaixo do Previsto
      </li>
      <li>
        <span class="cor-legenda" style="background:linear-gradient(135deg,#f87171,#ef4444)"></span>
        Acima do Previsto
      </li>
      <li>
        <span class="cor-legenda" style="background:linear-gradient(135deg,#60a5fa,#3b82f6)"></span>
        Dentro do Previsto
      </li>
      <li>
        <span class="cor-legenda" style="background:linear-gradient(135deg,#9ca3af,#6b7280)"></span>
        Padrao / Sem dados
      </li>
    </ul>
    <button class="fechar" @click="emit('close')">Fechar</button>
  </div>
</template>

<style scoped>
.legend-panel {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  z-index: 1001; background: rgba(15,12,41,0.88);
  backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  padding: 28px 32px; border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 16px 48px rgba(0,0,0,0.4);
  width: 320px; color: #fff;
}
h3 { margin: 0 0 4px; text-align: center; font-weight: 600; font-size: 16px; letter-spacing: -0.2px; }
.sub { text-align: center; color: rgba(255,255,255,0.4); font-size: 11px; margin-bottom: 20px; }
ul { list-style: none; padding: 0; margin: 0 0 20px; }
li {
  display: flex; align-items: center; margin-bottom: 14px; font-size: 13px; gap: 12px;
  color: rgba(255,255,255,0.85);
}
.cor-legenda {
  width: 20px; height: 20px; border-radius: 6px; flex-shrink: 0;
  border: 1px solid rgba(255,255,255,0.1);
}
.fechar {
  width: 100%; padding: 10px; background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;
  color: rgba(255,255,255,0.7); cursor: pointer; font-size: 13px;
  font-family: inherit; transition: all 0.2s;
}
.fechar:hover { background: rgba(255,255,255,0.12); color: #fff; }
</style>
