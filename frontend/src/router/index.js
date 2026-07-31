import { createRouter, createWebHistory } from 'vue-router'
import WaferListView from '../views/WaferListView.vue'

const routes = [
  {
    path: '/',
    name: 'WaferList',
    component: WaferListView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
