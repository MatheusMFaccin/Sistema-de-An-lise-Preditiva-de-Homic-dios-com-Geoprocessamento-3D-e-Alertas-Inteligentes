import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('@/views/MapView.vue') },
    { path: '/municipio/:slug', component: () => import('@/views/MunicipioView.vue') },
  ],
})

export default router
