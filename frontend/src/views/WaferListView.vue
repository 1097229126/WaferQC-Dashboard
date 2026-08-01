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
        @sort-change="handleSortChange"
      >
        <el-table-column type="index" label="序号" width="80" align="center" />
        
        <el-table-column 
          prop="wafer_no" 
          label="晶片号" 
          min-width="150" 
          align="center"
          sortable="custom"
        />
        
        <!-- 浓度相关指标 -->
        <el-table-column label="浓度指标" min-width="600">
          <el-table-column 
            prop="conc_mean" 
            label="浓度均值 (atoms/cm³)" 
            min-width="180" 
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">
              {{ row.conc_mean !== null ? formatConcentration(row.conc_mean) : '-' }}
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="conc_max" 
            label="浓度最大值 (atoms/cm³)" 
            min-width="180" 
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">
              {{ row.conc_max !== null ? formatConcentration(row.conc_max) : '-' }}
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="conc_min" 
            label="浓度最小值 (atoms/cm³)" 
            min-width="180" 
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">
              {{ row.conc_min !== null ? formatConcentration(row.conc_min) : '-' }}
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="conc_uniformity" 
            label="浓度均匀性 (%)" 
            min-width="140" 
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">
              {{ row.conc_uniformity !== null ? row.conc_uniformity.toFixed(2) + '%' : '-' }}
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="conc_tolerance" 
            label="浓度 Tolerance%" 
            min-width="140" 
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">
              {{ row.conc_tolerance !== null ? row.conc_tolerance.toFixed(2) + '%' : '-' }}
            </template>
          </el-table-column>
        </el-table-column>
        
        <!-- 厚度相关指标 -->
        <el-table-column label="厚度指标" min-width="600">
          <el-table-column 
            prop="thick_mean" 
            label="厚度均值 (μm)" 
            min-width="150" 
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">
              {{ row.thick_mean !== null ? formatThickness(row.thick_mean) : '-' }}
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="thick_max" 
            label="厚度最大值 (μm)" 
            min-width="150" 
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">
              {{ row.thick_max !== null ? formatThickness(row.thick_max) : '-' }}
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="thick_min" 
            label="厚度最小值 (μm)" 
            min-width="150" 
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">
              {{ row.thick_min !== null ? formatThickness(row.thick_min) : '-' }}
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="thick_uniformity" 
            label="厚度均匀性 (%)" 
            min-width="140" 
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">
              {{ row.thick_uniformity !== null ? row.thick_uniformity.toFixed(2) + '%' : '-' }}
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="thick_tolerance" 
            label="厚度 Tolerance%" 
            min-width="140" 
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">
              {{ row.thick_tolerance !== null ? row.thick_tolerance.toFixed(2) + '%' : '-' }}
            </template>
          </el-table-column>
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
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { waferAPI } from '../api/index.js'

// 状态
const tableData = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 排序状态管理
const sortState = ref({
  prop: null,      // 当前排序字段
  order: null      // 排序方向: 'ascending' (正序), 'descending' (倒序), null (不排序)
})

// 计算属性：根据排序状态返回排序后的数据
const sortedTableData = computed(() => {
  if (!sortState.value.prop || !sortState.value.order) {
    return tableData.value
  }
  
  const { prop, order } = sortState.value
  const sorted = [...tableData.value]
  
  // 自然排序函数：正确处理包含数字的字符串（如 TK1, TK2, TK10, TK100）
  const naturalCompare = (a, b) => {
    if (typeof a !== 'string' || typeof b !== 'string') {
      return 0
    }
    
    // 提取字符串中的数字部分和非数字部分
    const regex = /(\d+)|(\D+)/g
    const partsA = a.match(regex) || []
    const partsB = b.match(regex) || []
    
    // 逐段比较
    for (let i = 0; i < Math.max(partsA.length, partsB.length); i++) {
      const partA = partsA[i] || ''
      const partB = partsB[i] || ''
      
      // 如果都是数字，按数值比较
      if (/^\d+$/.test(partA) && /^\d+$/.test(partB)) {
        const numA = parseInt(partA, 10)
        const numB = parseInt(partB, 10)
        if (numA !== numB) {
          return numA - numB
        }
      } else {
        // 否则按字符串比较
        const cmp = partA.localeCompare(partB, 'zh-CN')
        if (cmp !== 0) {
          return cmp
        }
      }
    }
    
    return 0
  }
  
  sorted.sort((a, b) => {
    const valA = a[prop]
    const valB = b[prop]
    
    // 处理null值，null值排在最后
    if (valA === null && valB === null) return 0
    if (valA === null) return 1
    if (valB === null) return -1
    
    let result = 0
    if (typeof valA === 'string') {
      // 使用自然排序处理包含数字的字符串
      result = naturalCompare(valA, valB)
    } else {
      // 数值比较
      result = valA - valB
    }
    
    // 根据排序方向返回结果
    return order === 'ascending' ? result : -result
  })
  
  return sorted
})

// 方法
const loadData = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    
    // 转换排序参数
    let sortBy = null
    let sortOrder = null
    if (sortState.value.prop && sortState.value.order) {
      sortBy = sortState.value.prop
      sortOrder = sortState.value.order === 'ascending' ? 'asc' : 'desc'
    }
    
    const response = await waferAPI.getWafers(skip, pageSize.value, sortBy, sortOrder)
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

// 处理表头排序点击
const handleSortChange = ({ prop, order }) => {
  // 如果点击的是同一个字段，则在三种模式间切换：正序 -> 倒序 -> 不排序
  if (sortState.value.prop === prop) {
    if (sortState.value.order === 'ascending') {
      sortState.value.order = 'descending'
    } else if (sortState.value.order === 'descending') {
      sortState.value.order = null
      sortState.value.prop = null
    } else {
      sortState.value.order = 'ascending'
    }
  } else {
    // 点击新字段，默认正序
    sortState.value.prop = prop
    sortState.value.order = 'ascending'
  }
  
  console.log('排序状态:', sortState.value)
  
  // 重置到第一页并重新加载数据
  currentPage.value = 1
  loadData()
}

// 格式化浓度显示（科学计数法，使用上标）
const formatConcentration = (value) => {
  if (value === null || value === undefined) return '-'
  
  // 将数值转换为科学计数法字符串
  const str = value.toExponential(2) // 保留两位小数
  // 格式: "3.06e+28" -> "3.06×10²⁸"
  const [mantissa, exponent] = str.split('e')
  const expNum = parseInt(exponent.replace('+', ''))
  
  // 上标数字映射
  const superscripts = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '-': '⁻'
  }
  
  // 将指数转换为上标
  const expStr = expNum.toString().split('').map(char => superscripts[char] || char).join('')
  
  return `${mantissa}×10${expStr}`
}

// 格式化厚度显示（普通小数）
const formatThickness = (value) => {
  if (value === null || value === undefined) return '-'
  
  // 厚度值通常较小，直接使用toFixed格式化
  return value.toFixed(3)
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
