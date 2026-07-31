<template>
  <div id="app">
    <el-container style="height: 100vh;">
      <!-- 左侧菜单 -->
      <el-aside width="220px" style="background-color: #304156;">
        <div class="logo">
          <h2>WaferQC</h2>
        </div>
        <el-menu
          :default-active="$route.path"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409eff"
          router
        >
          <el-menu-item index="/">
            <el-icon><DataAnalysis /></el-icon>
            <span>外延片检测大表</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { DataAnalysis } from '@element-plus/icons-vue'
</script>

<style scoped>
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  border-bottom: 1px solid #1f2d3d;
}

.logo h2 {
  margin: 0;
  font-size: 20px;
}

.el-aside {
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
}

.el-main {
  padding: 20px;
  background-color: #f0f2f5;
}
</style>
