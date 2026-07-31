import { createRouter, createWebHistory } from 'vue-router'
import WaferListView from '../views/WaferListView.vue'
import WaferManagementView from '../views/WaferManagementView.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
