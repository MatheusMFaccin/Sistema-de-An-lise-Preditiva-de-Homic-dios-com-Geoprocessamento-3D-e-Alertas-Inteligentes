<script setup lang="ts">
import type { TabelaItem } from '@/types'

defineProps<{ tabela: TabelaItem[] }>()

function badgeClass(cl: string): string {
  if (cl === 'Abaixo do Previsto') return 'badge badge-green'
  if (cl === 'Acima do Previsto') return 'badge badge-red'
  if (cl === 'Dentro do Previsto') return 'badge badge-blue'
  return 'badge badge-gray'
}
</script>

<template>
  <div class="table-card">
    <div class="table-header">
      <div class="table-title">Dados Detalhados</div>
    </div>
    <div class="table-responsive">
      <table>
        <thead>
          <tr>
            <th>Ano</th>
            <th>Vitimas Reais</th>
            <th>Previsao</th>
            <th>Classificacao</th>
            <th>Margem Erro</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in tabela" :key="item.ano">
            <td><strong>{{ item.ano }}</strong></td>
            <td>{{ item.total_vitimas_ano ?? '—' }}</td>
            <td>{{ item.previsao_homicidios.toFixed(1) }}</td>
            <td>
              <span :class="badgeClass(item.classificacao)">{{ item.classificacao }}</span>
            </td>
            <td>{{ item.margem_erro_k?.toFixed(2) ?? '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.table-card {
  background: #fff; border-radius: 12px; padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 32px;
  border: 1px solid rgba(0,0,0,0.04);
}
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.table-title { font-size: 16px; font-weight: 600; color: #1a1a2e; }
.table-responsive { overflow-x: auto; border-radius: 8px; border: 1px solid #eef0f4; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
thead { background: #f8f9fc; }
th { padding: 12px 16px; text-align: left; font-weight: 600; color: #4a4d5e; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #eef0f4; }
td { padding: 12px 16px; border-bottom: 1px solid #f0f2f5; color: #1a1a2e; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #f8f9fc; }
.badge {
  display: inline-block; padding: 3px 10px; border-radius: 20px;
  font-size: 11px; font-weight: 600; letter-spacing: 0.2px;
}
.badge-green { background: #dcfce7; color: #166534; }
.badge-red { background: #fee2e2; color: #991b1b; }
.badge-blue { background: #dbeafe; color: #1e40af; }
.badge-gray { background: #f3f4f6; color: #4b5563; }
</style>
