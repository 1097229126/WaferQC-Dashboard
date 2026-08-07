import { createRouter, createWebHistory } from 'vue-router'
import WaferListView from '../views/WaferListView.vue'
import WaferManagementView from '../views/WaferManagementView.vue'
import DashboardView from '../views/DashboardView.vue'

const routes = [
  {
    path: '/',
    name: 'WaferList',
    component: WaferListView,
    meta: { title: '外延片检测大表' }
  },
  {
    path: '/wafers',
    name: 'WaferManagement',
    component: WaferManagementView,
    meta: { title: '晶片列表' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { title: '可视化看板' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
