<template>
  <div class="wafer-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>外延片检测大表</h2>
          <el-button type="primary" @click="loadData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column type="index" label="序号" width="80" align="center" />
        
        <el-table-column prop="wafer_no" label="晶片号" min-width="150" align="center" />
        
        <el-table-column prop="avg_thickness" label="平均厚度 (μm)" min-width="150" align="center">
          <template #default="{ row }">
            {{ row.avg_thickness !== null ? formatThickness(row.avg_thickness) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="avg_concentration" label="平均浓度 (atoms/cm³)" min-width="200" align="center">
          <template #default="{ row }">
            {{ row.avg_concentration !== null ? formatConcentration(row.avg_concentration) : '-' }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { waferAPI } from '../api'

// 状态
const tableData = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 方法
const loadData = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const response = await waferAPI.getWafers(skip, pageSize.value)
    tableData.value = response.items
    total.value = response.total
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadData()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadData()
}

// 格式化浓度显示（科学计数法）
const formatConcentration = (value) => {
  if (value === null || value === undefined) return '-'
  // 转换为科学计数法，例如: 1.50×10^15
  const exponential = value.toExponential(2)
  const [mantissa, exponent] = exponential.split('e+')
  return `${mantissa}×10^${exponent}`
}

// 格式化厚度显示（科学计数法）
const formatThickness = (value) => {
  if (value === null || value === undefined) return '-'
  // 转换为科学计数法，例如: 1.00×10^1
  const exponential = value.toExponential(2)
  const [mantissa, exponent] = exponential.split('e+')
  return `${mantissa}×10^${exponent}`
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.wafer-list {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
}
</style>
