<script setup lang="ts">
defineProps<{ anos: string[]; selected: string }>()
const emit = defineEmits<{ (e: 'change', ano: string): void }>()
</script>

<template>
  <div class="selector-inline">
    <label>Ano:</label>
    <select :value="selected" @change="emit('change', ($event.target as HTMLSelectElement).value)">
      <option v-for="ano in anos" :key="ano" :value="ano">{{ ano }}</option>
    </select>
  </div>
</template>

<style scoped>
.selector-inline { display: flex; align-items: center; gap: 8px; }
label { font-weight: 500; color: rgba(255,255,255,0.6); font-size: 12px; }
select {
  background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12);
  color: #fff; padding: 6px 12px; border-radius: 8px; font-size: 13px;
  font-family: inherit; cursor: pointer; outline: none;
  appearance: none; -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' fill='white'%3E%3Cpath d='M0 0l5 6 5-6z'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 10px center; padding-right: 30px;
}
select:hover { background: rgba(255,255,255,0.12); }
select option { background: #1a1a2e; color: #fff; }
</style>
