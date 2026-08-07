<template>
  <div id="app">
    <el-container style="height: 100vh;">
      <!-- 左侧菜单栏 -->
      <el-aside width="200px" class="sidebar">
        <div class="logo">
          <h2>WaferQC</h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409eff"
        >
          <el-menu-item index="/">
            <el-icon><DataAnalysis /></el-icon>
            <span>外延片检测大表</span>
          </el-menu-item>
          <el-menu-item index="/wafers">
            <el-icon><Grid /></el-icon>
            <span>晶片列表</span>
          </el-menu-item>
          <el-menu-item index="/dashboard">
            <el-icon><TrendCharts /></el-icon>
            <span>可视化看板</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧主内容区 -->
      <el-container>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { DataAnalysis, Grid, TrendCharts } from '@element-plus/icons-vue'

const route = useRoute()

// 计算当前激活的菜单项
const activeMenu = computed(() => {
  return route.path
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.sidebar {
  background-color: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4d;
  color: #fff;
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.el-menu {
  border-right: none;
}

.el-menu-item {
  height: 50px;
  line-height: 50px;
}

.el-menu-item:hover {
  background-color: #263445 !important;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
