<template>
  <div class="dashboard-container">
    <el-card class="header-card">
      <h2>📊 可视化看板</h2>
      <p class="subtitle">半导体外延片质量监控数据分析</p>
    </el-card>

    <!-- 饼图区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>浓度等级分布</span>
            </div>
          </template>
          <div ref="concGradeChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>厚度等级分布</span>
            </div>
          </template>
          <div ref="thickGradeChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>综合等级分布</span>
            </div>
          </template>
          <div ref="overallGradeChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 折线图区域 - 点位一致性 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>浓度点位一致性分析</span>
              <div class="pagination-controls">
                <el-button 
                  size="small" 
                  @click="prevConcConsistencyPage"
                  :disabled="concConsistencyCurrentPage <= 1"
                >
                  上一页
                </el-button>
                <span class="page-info">
                  第 {{ concConsistencyCurrentPage }} / {{ concConsistencyTotalPages }} 页
                </span>
                <el-button 
                  size="small" 
                  @click="nextConcConsistencyPage"
                  :disabled="concConsistencyCurrentPage >= concConsistencyTotalPages"
                >
                  下一页
                </el-button>
              </div>
            </div>
          </template>
          <div ref="concConsistencyChart" class="chart-container-large"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>厚度点位一致性分析</span>
              <div class="pagination-controls">
                <el-button 
                  size="small" 
                  @click="prevThickConsistencyPage"
                  :disabled="thickConsistencyCurrentPage <= 1"
                >
                  上一页
                </el-button>
                <span class="page-info">
                  第 {{ thickConsistencyCurrentPage }} / {{ thickConsistencyTotalPages }} 页
                </span>
                <el-button 
                  size="small" 
                  @click="nextThickConsistencyPage"
                  :disabled="thickConsistencyCurrentPage >= thickConsistencyTotalPages"
                >
                  下一页
                </el-button>
              </div>
            </div>
          </template>
          <div ref="thickConsistencyChart" class="chart-container-large"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 折线图区域 - 均匀性 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>浓度均匀性分析</span>
              <div class="pagination-controls">
                <el-button 
                  size="small" 
                  @click="prevConcUniformityPage"
                  :disabled="concUniformityCurrentPage <= 1"
                >
                  上一页
                </el-button>
                <span class="page-info">
                  第 {{ concUniformityCurrentPage }} / {{ concUniformityTotalPages }} 页
                </span>
                <el-button 
                  size="small" 
                  @click="nextConcUniformityPage"
                  :disabled="concUniformityCurrentPage >= concUniformityTotalPages"
                >
                  下一页
                </el-button>
              </div>
            </div>
          </template>
          <div ref="concUniformityChart" class="chart-container-large"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>厚度均匀性分析</span>
              <div class="pagination-controls">
                <el-button 
                  size="small" 
                  @click="prevThickUniformityPage"
                  :disabled="thickUniformityCurrentPage <= 1"
                >
                  上一页
                </el-button>
                <span class="page-info">
                  第 {{ thickUniformityCurrentPage }} / {{ thickUniformityTotalPages }} 页
                </span>
                <el-button 
                  size="small" 
                  @click="nextThickUniformityPage"
                  :disabled="thickUniformityCurrentPage >= thickUniformityTotalPages"
                >
                  下一页
                </el-button>
              </div>
            </div>
          </template>
          <div ref="thickUniformityChart" class="chart-container-large"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

// 图表引用
const concGradeChart = ref(null)
const thickGradeChart = ref(null)
const overallGradeChart = ref(null)
const concConsistencyChart = ref(null)
const thickConsistencyChart = ref(null)
const concUniformityChart = ref(null)
const thickUniformityChart = ref(null)

// 图表实例
let concGradeChartInstance = null
let thickGradeChartInstance = null
let overallGradeChartInstance = null
let concConsistencyChartInstance = null
let thickConsistencyChartInstance = null
let concUniformityChartInstance = null
let thickUniformityChartInstance = null

// 分页状态
const concConsistencyCurrentPage = ref(1)
const concConsistencyTotalPages = ref(1)
const thickConsistencyCurrentPage = ref(1)
const thickConsistencyTotalPages = ref(1)
const concUniformityCurrentPage = ref(1)
const concUniformityTotalPages = ref(1)
const thickUniformityCurrentPage = ref(1)
const thickUniformityTotalPages = ref(1)

// 数据缓存
let allWaferDetails = []

// 格式化科学计数法
const formatScientific = (value) => {
  if (value === null || value === undefined) return '-'
  if (value === 0) return '0'
  
  const exponent = Math.floor(Math.log10(Math.abs(value)))
  const mantissa = value / Math.pow(10, exponent)
  
  return `${mantissa.toFixed(2)}×10^${exponent}`
}

// 获取等级分布数据
const fetchGradeDistribution = async () => {
  try {
    const response = await axios.get('/api/v1/dashboard/grade-distribution')
    renderPieCharts(response.data)
  } catch (error) {
    console.error('获取等级分布数据失败:', error)
  }
}

// 渲染饼图
const renderPieCharts = (data) => {
  // 浓度等级饼图
  const concData = [
    { value: data.conc_grade_distribution.A || 0, name: 'A级' },
    { value: data.conc_grade_distribution.B || 0, name: 'B级' },
    { value: data.conc_grade_distribution['不合格'] || 0, name: '不合格' }
  ]
  
  concGradeChartInstance = echarts.init(concGradeChart.value)
  concGradeChartInstance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        data: concData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          formatter: '{b}: {c}\n({d}%)'
        }
      }
    ],
    color: ['#67C23A', '#E6A23C', '#F56C6C']
  })

  // 厚度等级饼图
  const thickData = [
    { value: data.thick_grade_distribution.A || 0, name: 'A级' },
    { value: data.thick_grade_distribution.B || 0, name: 'B级' },
    { value: data.thick_grade_distribution['不合格'] || 0, name: '不合格' }
  ]
  
  thickGradeChartInstance = echarts.init(thickGradeChart.value)
  thickGradeChartInstance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        data: thickData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          formatter: '{b}: {c}\n({d}%)'
        }
      }
    ],
    color: ['#67C23A', '#E6A23C', '#F56C6C']
  })

  // 综合等级饼图
  const overallData = [
    { value: data.overall_grade_distribution.A || 0, name: 'A级' },
    { value: data.overall_grade_distribution.B || 0, name: 'B级' },
    { value: data.overall_grade_distribution['不合格'] || 0, name: '不合格' }
  ]
  
  overallGradeChartInstance = echarts.init(overallGradeChart.value)
  overallGradeChartInstance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        data: overallData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          formatter: '{b}: {c}\n({d}%)'
        }
      }
    ],
    color: ['#67C23A', '#E6A23C', '#F56C6C']
  })
}

// 获取晶片详细数据
const fetchWaferDetails = async (page = 1) => {
  try {
    const skip = (page - 1) * 50
    const response = await axios.get('/api/v1/dashboard/wafer-details', {
      params: { skip, limit: 50 }
    })
    
    allWaferDetails = response.data.items
    
    // 更新分页信息
    concConsistencyTotalPages.value = response.data.total_pages
    thickConsistencyTotalPages.value = response.data.total_pages
    concUniformityTotalPages.value = response.data.total_pages
    thickUniformityTotalPages.value = response.data.total_pages
    
    // 渲染所有折线图
    renderConsistencyCharts()
    renderUniformityCharts()
  } catch (error) {
    console.error('获取晶片详细数据失败:', error)
  }
}

// 渲染点位一致性图表
const renderConsistencyCharts = () => {
  // 准备浓度点位一致性数据
  const concSeries = []
  const concXAxis = Array.from({ length: 25 }, (_, i) => `P${i + 1}`)
  
  allWaferDetails.forEach((wafer, index) => {
    const eq1Data = {}
    const eq2Data = {}
    
    wafer.measurements.forEach(m => {
      if (m.measurement_type === 1 && m.point_number) {
        if (m.measurement_equipment === 1) {
          eq1Data[m.point_number] = m.value
        } else if (m.measurement_equipment === 2) {
          eq2Data[m.point_number] = m.value
        }
      }
    })
    
    const consistencyData = []
    for (let i = 1; i <= 25; i++) {
      if (eq1Data[i] !== undefined && eq2Data[i] !== undefined) {
        const val1 = eq1Data[i]
        const val2 = eq2Data[i]
        const consistency = ((val1 - val2) - 1) * 100
        consistencyData.push(consistency)
      } else {
        consistencyData.push(null)
      }
    }
    
    concSeries.push({
      name: wafer.wafer_no,
      type: 'line',
      data: consistencyData,
      showSymbol: false,
      lineStyle: { width: 1 }
    })
  })
  
  // 渲染浓度点位一致性图
  if (concConsistencyChart.value) {
    concConsistencyChartInstance = echarts.init(concConsistencyChart.value)
    concConsistencyChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          let result = params[0].axisValue + '<br/>'
          params.forEach(param => {
            if (param.value !== null && param.value !== undefined) {
              result += `${param.seriesName}: ${param.value.toFixed(2)}%<br/>`
            }
          })
          return result
        }
      },
      legend: {
        type: 'scroll',
        bottom: 0
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: concXAxis,
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        name: '差值率 (%)',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: concSeries
    })
  }

  // 准备厚度点位一致性数据
  const thickSeries = []
  const thickXAxis = Array.from({ length: 25 }, (_, i) => `T${i + 1}`)
  
  allWaferDetails.forEach((wafer, index) => {
    const eq1Data = {}
    const eq2Data = {}
    
    wafer.measurements.forEach(m => {
      if (m.measurement_type === 2 && m.point_number) {
        if (m.measurement_equipment === 1) {
          eq1Data[m.point_number] = m.value
        } else if (m.measurement_equipment === 2) {
          eq2Data[m.point_number] = m.value
        }
      }
    })
    
    const consistencyData = []
    for (let i = 1; i <= 25; i++) {
      if (eq1Data[i] !== undefined && eq2Data[i] !== undefined) {
        const val1 = eq1Data[i]
        const val2 = eq2Data[i]
        const consistency = ((val1 - val2) - 1) * 100
        consistencyData.push(consistency)
      } else {
        consistencyData.push(null)
      }
    }
    
    thickSeries.push({
      name: wafer.wafer_no,
      type: 'line',
      data: consistencyData,
      showSymbol: false,
      lineStyle: { width: 1 }
    })
  })
  
  // 渲染厚度点位一致性图
  if (thickConsistencyChart.value) {
    thickConsistencyChartInstance = echarts.init(thickConsistencyChart.value)
    thickConsistencyChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          let result = params[0].axisValue + '<br/>'
          params.forEach(param => {
            if (param.value !== null && param.value !== undefined) {
              result += `${param.seriesName}: ${param.value.toFixed(2)}%<br/>`
            }
          })
          return result
        }
      },
      legend: {
        type: 'scroll',
        bottom: 0
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: thickXAxis,
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        name: '差值率 (%)',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: thickSeries
    })
  }
}

// 渲染均匀性图表
const renderUniformityCharts = () => {
  // 准备浓度均匀性数据
  const concEq1Series = []
  const concEq2Series = []
  const concXAxis = Array.from({ length: 25 }, (_, i) => `P${i + 1}`)
  
  allWaferDetails.forEach((wafer, index) => {
    const eq1Data = new Array(25).fill(null)
    const eq2Data = new Array(25).fill(null)
    
    wafer.measurements.forEach(m => {
      if (m.measurement_type === 1 && m.point_number) {
        const idx = m.point_number - 1
        if (idx >= 0 && idx < 25) {
          if (m.measurement_equipment === 1) {
            eq1Data[idx] = m.value
          } else if (m.measurement_equipment === 2) {
            eq2Data[idx] = m.value
          }
        }
      }
    })
    
    // 设备1数据线
    concEq1Series.push({
      name: `${wafer.wafer_no} (设备1)`,
      type: 'line',
      data: eq1Data,
      showSymbol: false,
      lineStyle: { width: 1 },
      itemStyle: { color: '#409EFF' }
    })
    
    // 设备2数据线
    concEq2Series.push({
      name: `${wafer.wafer_no} (设备2)`,
      type: 'line',
      data: eq2Data,
      showSymbol: false,
      lineStyle: { width: 1 },
      itemStyle: { color: '#E6A23C' }
    })
  })
  
  // 渲染浓度均匀性图
  if (concUniformityChart.value) {
    concUniformityChartInstance = echarts.init(concUniformityChart.value)
    concUniformityChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          let result = params[0].axisValue + '<br/>'
          params.forEach(param => {
            if (param.value !== null && param.value !== undefined) {
              result += `${param.seriesName}: ${formatScientific(param.value)}<br/>`
            }
          })
          return result
        }
      },
      legend: {
        type: 'scroll',
        bottom: 0
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: concXAxis,
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        name: '浓度 (atoms/cm³)',
        axisLabel: {
          formatter: (value) => formatScientific(value)
        }
      },
      series: [...concEq1Series, ...concEq2Series]
    })
  }

  // 准备厚度均匀性数据
  const thickEq1Series = []
  const thickEq2Series = []
  const thickXAxis = Array.from({ length: 25 }, (_, i) => `T${i + 1}`)
  
  allWaferDetails.forEach((wafer, index) => {
    const eq1Data = new Array(25).fill(null)
    const eq2Data = new Array(25).fill(null)
    
    wafer.measurements.forEach(m => {
      if (m.measurement_type === 2 && m.point_number) {
        const idx = m.point_number - 1
        if (idx >= 0 && idx < 25) {
          if (m.measurement_equipment === 1) {
            eq1Data[idx] = m.value
          } else if (m.measurement_equipment === 2) {
            eq2Data[idx] = m.value
          }
        }
      }
    })
    
    // 设备1数据线
    thickEq1Series.push({
      name: `${wafer.wafer_no} (设备1)`,
      type: 'line',
      data: eq1Data,
      showSymbol: false,
      lineStyle: { width: 1 },
      itemStyle: { color: '#409EFF' }
    })
    
    // 设备2数据线
    thickEq2Series.push({
      name: `${wafer.wafer_no} (设备2)`,
      type: 'line',
      data: eq2Data,
      showSymbol: false,
      lineStyle: { width: 1 },
      itemStyle: { color: '#E6A23C' }
    })
  })
  
  // 渲染厚度均匀性图
  if (thickUniformityChart.value) {
    thickUniformityChartInstance = echarts.init(thickUniformityChart.value)
    thickUniformityChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          let result = params[0].axisValue + '<br/>'
          params.forEach(param => {
            if (param.value !== null && param.value !== undefined) {
              result += `${param.seriesName}: ${param.value.toFixed(4)} μm<br/>`
            }
          })
          return result
        }
      },
      legend: {
        type: 'scroll',
        bottom: 0
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: thickXAxis,
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        name: '厚度 (μm)'
      },
      series: [...thickEq1Series, ...thickEq2Series]
    })
  }
}

// 分页控制函数
const prevConcConsistencyPage = () => {
  if (concConsistencyCurrentPage.value > 1) {
    concConsistencyCurrentPage.value--
    fetchWaferDetails(concConsistencyCurrentPage.value)
  }
}

const nextConcConsistencyPage = () => {
  if (concConsistencyCurrentPage.value < concConsistencyTotalPages.value) {
    concConsistencyCurrentPage.value++
    fetchWaferDetails(concConsistencyCurrentPage.value)
  }
}

const prevThickConsistencyPage = () => {
  if (thickConsistencyCurrentPage.value > 1) {
    thickConsistencyCurrentPage.value--
    fetchWaferDetails(thickConsistencyCurrentPage.value)
  }
}

const nextThickConsistencyPage = () => {
  if (thickConsistencyCurrentPage.value < thickConsistencyTotalPages.value) {
    thickConsistencyCurrentPage.value++
    fetchWaferDetails(thickConsistencyCurrentPage.value)
  }
}

const prevConcUniformityPage = () => {
  if (concUniformityCurrentPage.value > 1) {
    concUniformityCurrentPage.value--
    fetchWaferDetails(concUniformityCurrentPage.value)
  }
}

const nextConcUniformityPage = () => {
  if (concUniformityCurrentPage.value < concUniformityTotalPages.value) {
    concUniformityCurrentPage.value++
    fetchWaferDetails(concUniformityCurrentPage.value)
  }
}

const prevThickUniformityPage = () => {
  if (thickUniformityCurrentPage.value > 1) {
    thickUniformityCurrentPage.value--
    fetchWaferDetails(thickUniformityCurrentPage.value)
  }
}

const nextThickUniformityPage = () => {
  if (thickUniformityCurrentPage.value < thickUniformityTotalPages.value) {
    thickUniformityCurrentPage.value++
    fetchWaferDetails(thickUniformityCurrentPage.value)
  }
}

// 窗口大小改变时重新渲染图表
const handleResize = () => {
  concGradeChartInstance?.resize()
  thickGradeChartInstance?.resize()
  overallGradeChartInstance?.resize()
  concConsistencyChartInstance?.resize()
  thickConsistencyChartInstance?.resize()
  concUniformityChartInstance?.resize()
  thickUniformityChartInstance?.resize()
}

onMounted(() => {
  // 获取等级分布数据
  fetchGradeDistribution()
  
  // 获取第一页的晶片详细数据
  fetchWaferDetails(1)
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  // 销毁图表实例
  concGradeChartInstance?.dispose()
  thickGradeChartInstance?.dispose()
  overallGradeChartInstance?.dispose()
  concConsistencyChartInstance?.dispose()
  thickConsistencyChartInstance?.dispose()
  concUniformityChartInstance?.dispose()
  thickUniformityChartInstance?.dispose()
  
  // 移除事件监听
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
  text-align: center;
}

.header-card h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-info {
  font-size: 14px;
  color: #606266;
}

.chart-container {
  height: 350px;
  width: 100%;
}

.chart-container-large {
  height: 500px;
  width: 100%;
}
</style>
