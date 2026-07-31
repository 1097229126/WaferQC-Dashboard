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
            {{ row.avg_thickness !== null ? row.avg_thickness.toFixed(4) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="avg_concentration" label="平均浓度 (atoms/cm³)" min-width="200" align="center">
          <template #default="{ row }">
            {{ row.avg_concentration !== null ? formatConcentration(row.avg_concentration) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="测量次数" width="120" align="center">
          <template #default="{ row }">
            <el-tag 
              type="info" 
              @click="showMeasurementDetail(row)"
              style="cursor: pointer;"
            >
              {{ row.measurement_count || 0 }}
            </el-tag>
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

    <!-- 测量明细抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="`测量明细 - ${currentWaferNo}`"
      size="70%"
      direction="rtl"
    >
      <div class="measurement-detail">
        <!-- 统计卡片 -->
        <el-row :gutter="20" class="stats-row">
          <el-col :span="8">
            <el-card shadow="hover">
              <div class="stat-item">
                <div class="stat-label">总测量次数</div>
                <div class="stat-value">{{ measurements.length }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <div class="stat-item">
                <div class="stat-label">浓度测量</div>
                <div class="stat-value">{{ concentrationCount }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <div class="stat-item">
                <div class="stat-label">厚度测量</div>
                <div class="stat-value">{{ thicknessCount }}</div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 测量数据表格 -->
        <el-table
          :data="measurements"
          v-loading="detailLoading"
          stripe
          border
          max-height="500"
          style="margin-top: 20px;"
        >
          <el-table-column type="index" label="序号" width="80" align="center" />
          
          <el-table-column prop="measurement_type" label="测量类型" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="row.measurement_type === 1 ? 'success' : 'warning'">
                {{ row.measurement_type === 1 ? '浓度' : '厚度' }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="value" label="测量值" min-width="200" align="center">
            <template #default="{ row }">
              {{ formatValue(row) }}
            </template>
          </el-table-column>
          
          <el-table-column prop="measured_at" label="测量时间" min-width="180" align="center">
            <template #default="{ row }">
              {{ formatDate(row.measured_at) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { waferAPI, measurementAPI } from '../api'

// 状态
const tableData = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 抽屉相关状态
const drawerVisible = ref(false)
const currentWaferNo = ref('')
const measurements = ref([])
const detailLoading = ref(false)

// 计算属性
const concentrationCount = computed(() => {
  return measurements.value.filter(m => m.measurement_type === 1).length
})

const thicknessCount = computed(() => {
  return measurements.value.filter(m => m.measurement_type === 2).length
})

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

// 显示测量明细
const showMeasurementDetail = async (row) => {
  currentWaferNo.value = row.wafer_no
  drawerVisible.value = true
  detailLoading.value = true
  
  try {
    const data = await measurementAPI.getWaferMeasurements(row.wafer_no)
    measurements.value = data
  } catch (error) {
    ElMessage.error('加载测量明细失败')
    console.error(error)
  } finally {
    detailLoading.value = false
  }
}

// 格式化浓度显示（科学计数法）
const formatConcentration = (value) => {
  if (value === null || value === undefined) return '-'
  // 转换为科学计数法，例如: 1.50×10^15
  const exponential = value.toExponential(2)
  const [mantissa, exponent] = exponential.split('e+')
  return `${mantissa}×10^${exponent}`
}

// 格式化测量值
const formatValue = (row) => {
  if (row.value === null || row.value === undefined) return '-'
  
  console.log('formatValue called:', row) // 调试日志
  
  if (row.measurement_type === 1) {
    // 浓度：科学计数法 1.50×10^15 atoms/cm³
    const exponential = row.value.toExponential(2)
    const [mantissa, exponent] = exponential.split('e+')
    const result = `${mantissa}×10^${exponent} atoms/cm³`
    console.log('浓度格式化结果:', result) // 调试日志
    return result
  } else {
    // 厚度：保留4位小数
    const result = row.value.toFixed(4) + ' μm'
    console.log('厚度格式化结果:', result) // 调试日志
    return result
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
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

/* 测量明细样式 */
.measurement-detail {
  padding: 10px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}

/* 可点击的标签样式 */
:deep(.el-tag) {
  transition: all 0.3s;
}

:deep(.el-tag:hover) {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
</style>
