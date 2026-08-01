<template>
  <div class="wafer-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>晶片列表</h2>
          <div>
            <el-button type="success" @click="showCreateDialog">
              <el-icon><Plus /></el-icon>
              新建晶片
            </el-button>
            <el-button type="warning" @click="showImportDialog">
              <el-icon><Upload /></el-icon>
              导入Excel
            </el-button>
            <el-button 
              type="danger" 
              :disabled="selectedRows.length === 0"
              @click="handleBatchDelete"
            >
              <el-icon><Delete /></el-icon>
              批量删除 ({{ selectedRows.length }})
            </el-button>
            <el-button type="info" plain @click="downloadTemplate">
              <el-icon><Download /></el-icon>
              下载模板
            </el-button>
            <el-button type="primary" @click="loadData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column type="index" label="序号" width="80" align="center" />
        
        <el-table-column prop="wafer_no" label="晶片号" min-width="150" align="center" />
        
        <el-table-column prop="original_grade" label="原始等级" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getGradeType(row.original_grade)">
              {{ row.original_grade || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="concentration_target" label="浓度目标值 (atoms/cm³)" min-width="200" align="center">
          <template #default="{ row }">
            {{ row.concentration_target !== null ? formatConcentration(row.concentration_target) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="thickness_target" label="厚度目标值 (μm)" min-width="180" align="center">
          <template #default="{ row }">
            {{ row.thickness_target !== null ? formatThickness(row.thickness_target) : '-' }}
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
        
        <el-table-column prop="created_at" label="创建时间" min-width="180" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(row)"
            >
              删除
            </el-button>
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
            <el-card 
              shadow="hover" 
              class="stat-card"
              :class="{ 'active-card': activeTab === 'all' }"
              @click="activeTab = 'all'"
              style="cursor: pointer;"
            >
              <div class="stat-item">
                <div class="stat-label">总测量次数</div>
                <div class="stat-value">{{ measurements.length }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card 
              shadow="hover" 
              class="stat-card"
              :class="{ 'active-card': activeTab === 'concentration' }"
              @click="activeTab = 'concentration'"
              style="cursor: pointer;"
            >
              <div class="stat-item">
                <div class="stat-label">浓度测量</div>
                <div class="stat-value">{{ concentrationCount }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card 
              shadow="hover" 
              class="stat-card"
              :class="{ 'active-card': activeTab === 'thickness' }"
              @click="activeTab = 'thickness'"
              style="cursor: pointer;"
            >
              <div class="stat-item">
                <div class="stat-label">厚度测量</div>
                <div class="stat-value">{{ thicknessCount }}</div>
              </div>
            </el-card>
          </el-col>
        </el-row>


        <!-- 操作按钮区 -->
        <div class="measure-actions">
          <el-button type="success" @click="showCreateMeasurementDialog">
            <el-icon><Plus /></el-icon>
            新建测量
          </el-button>
        </div>

        <!-- 测量数据表格 -->
        <el-table
          :data="filteredMeasurements"
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
          
          <el-table-column prop="point_number" label="测量点位" width="120" align="center">
            <template #default="{ row }">
              <span v-if="row.point_number">
                {{ row.measurement_type === 1 ? `P${row.point_number}` : `T${row.point_number}` }}
              </span>
              <span v-else>-</span>
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
          
          <el-table-column prop="measurement_equipment" label="测量设备" width="120" align="center">
            <template #default="{ row }">
              <el-tag type="info">{{ row.measurement_equipment || 1 }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-drawer>

    <!-- 新建测量对话框 -->
    <el-dialog
      v-model="createMeasurementDialogVisible"
      title="新建测量数据"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createMeasureFormRef"
        :model="createMeasureForm"
        :rules="createMeasureRules"
        label-width="120px"
      >
        <el-form-item label="晶片号" prop="wafer_no">
          <el-input
            v-model="createMeasureForm.wafer_no"
            disabled
          />
        </el-form-item>
        <el-form-item label="测量类型" prop="measurement_type">
          <el-select
            v-model="createMeasureForm.measurement_type"
            placeholder="请选择测量类型"
            style="width: 100%;"
          >
            <el-option label="浓度" :value="1">
              <span>浓度</span>
              <span style="color: #8492a6; font-size: 13px; margin-left: 8px;">atoms/cm³</span>
            </el-option>
            <el-option label="厚度" :value="2">
              <span>厚度</span>
              <span style="color: #8492a6; font-size: 13px; margin-left: 8px;">μm</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="测量点位" prop="point_number">
          <el-input-number
            v-model="createMeasureForm.point_number"
            :min="1"
            :max="25"
            :step="1"
            placeholder="请输入测量点位 (1-25)"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="测量设备" prop="measurement_equipment">
          <el-input-number
            v-model="createMeasureForm.measurement_equipment"
            :min="1"
            :step="1"
            placeholder="请输入测量设备编号"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="测量值" prop="value">
          <el-input
            v-model="createMeasureForm.value"
            placeholder="请输入测量值"
            clearable
          >
            <template #append>{{ measurementUnit }}</template>
          </el-input>
        </el-form-item>
        <el-form-item label="测量时间" prop="measured_at">
          <el-date-picker
            v-model="createMeasureForm.measured_at"
            type="datetime"
            placeholder="选择测量时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createMeasurementDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateMeasurement" :loading="createMeasurementLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 新建晶片对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="新建晶片"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="130px"
      >
        <el-form-item label="晶片号" prop="wafer_no">
          <el-input
            v-model="createForm.wafer_no"
            placeholder="请输入晶片号，如 WAFER-2024-001"
            clearable
          />
        </el-form-item>
        <el-form-item label="原始等级" prop="original_grade">
          <el-select
            v-model="createForm.original_grade"
            placeholder="请选择原始等级"
            clearable
            style="width: 100%;"
          >
            <el-option label="D" value="D" />
            <el-option label="NG" value="NG" />
          </el-select>
        </el-form-item>
        <el-form-item label="浓度目标值" prop="concentration_target">
          <el-input
            v-model="createForm.concentration_target"
            placeholder="请输入浓度目标值，如 1.5e15"
            clearable
          >
            <template #append>atoms/cm³</template>
          </el-input>
        </el-form-item>
        <el-form-item label="厚度目标值" prop="thickness_target">
          <el-input
            v-model="createForm.thickness_target"
            placeholder="请输入厚度目标值，如 10.0"
            clearable
          >
            <template #append>μm</template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="createLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入Excel对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入Excel数据"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="导入说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <p><strong>1. 下载模板：</strong>点击"下载模板"按钮获取标准Excel模板</p>
        <p><strong>2. 文件格式：</strong>仅支持 .xlsx 格式，包含"数据1"和"数据2"两个Sheet</p>
        <p><strong>3. 列名说明：</strong></p>
        <p>&nbsp;&nbsp;- 晶片号/Wafer ID：同一概念，任选其一</p>
        <p>&nbsp;&nbsp;- 原始等级/衬底级别：同一概念，表示晶片质量等级（D或NG）</p>
        <p>&nbsp;&nbsp;- 浓度目标、厚度目标：必须填写</p>
        <p><strong>4. 数据处理：</strong>相同晶片号会自动合并两台设备的测量数据</p>
      </el-alert>
      
      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".xlsx"
        style="width: 100%;"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 .xlsx 文件
          </div>
        </template>
      </el-upload>
      
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleImport" 
          :loading="importLoading"
          :disabled="!selectedFile"
        >
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Delete, Upload, UploadFilled } from '@element-plus/icons-vue'
import { waferAPI, measurementAPI } from '../api/index.js'

// 状态
const tableData = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedRows = ref([]) // 选中的行数据

// 抽屉相关状态
const drawerVisible = ref(false)
const currentWaferNo = ref('')
const measurements = ref([])
const detailLoading = ref(false)
const activeTab = ref('all') // 当前激活的tab

// 新建晶片对话框相关状态
const createDialogVisible = ref(false)
const createFormRef = ref(null)
const createLoading = ref(false)
const createForm = ref({
  wafer_no: '',
  original_grade: '',
  concentration_target: null,
  thickness_target: null
})

// 导入Excel对话框相关状态
const importDialogVisible = ref(false)
const importLoading = ref(false)
const selectedFile = ref(null)
const uploadRef = ref(null)

// 测量明细对话框相关状态
const createMeasurementDialogVisible = ref(false)
const createMeasurementLoading = ref(false)
const createMeasureFormRef = ref(null)
const createMeasureForm = ref({
  wafer_no: '',
  measurement_type: null,
  point_number: null,
  value: null,
  measurement_equipment: 1,
  measured_at: new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).replace(/\//g, '-')
})

// 新建晶片表单验证规则
const createRules = {
  wafer_no: [
    { required: true, message: '请输入晶片号', trigger: 'blur' },
    { min: 3, max: 50, message: '晶片号长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  concentration_target: [
    {
      validator: (rule, value, callback) => {
        if (value === null || value === '' || value === undefined) {
          callback()
          return
        }
        if (isNaN(Number(value))) {
          callback(new Error('请输入有效的数字'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  thickness_target: [
    {
      validator: (rule, value, callback) => {
        if (value === null || value === '' || value === undefined) {
          callback()
          return
        }
        if (isNaN(Number(value))) {
          callback(new Error('请输入有效的数字'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 新建测量表单验证规则
const createMeasureRules = {
  wafer_no: [
    { required: true, message: '晶片号不能为空', trigger: 'blur' }
  ],
  measurement_type: [
    { required: true, message: '请选择测量类型', trigger: 'change' }
  ],
  point_number: [
    { required: true, message: '请输入测量点位', trigger: 'blur' },
    { type: 'number', min: 1, max: 25, message: '测量点位必须在1-25之间', trigger: 'blur' }
  ],
  measurement_equipment: [
    { required: true, message: '请输入测量设备编号', trigger: 'blur' },
    { type: 'number', min: 1, message: '测量设备编号必须大于等于1', trigger: 'blur' }
  ],
  value: [
    { required: true, message: '请输入测量值', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value === null || value === '' || value === undefined) {
          callback(new Error('请输入测量值'))
          return
        }
        if (isNaN(Number(value))) {
          callback(new Error('请输入有效的数字'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  measured_at: [
    { required: true, message: '请选择测量时间', trigger: 'change' }
  ]
}

// 计算属性
const concentrationCount = computed(() => {
  return measurements.value.filter(m => m.measurement_type === 1).length
})

const thicknessCount = computed(() => {
  return measurements.value.filter(m => m.measurement_type === 2).length
})

// 测量数据（根据activeTab过滤）
const filteredMeasurements = computed(() => {
  if (activeTab.value === 'all') {
    return measurements.value
  } else if (activeTab.value === 'concentration') {
    return measurements.value.filter(m => m.measurement_type === 1)
  } else if (activeTab.value === 'thickness') {
    return measurements.value.filter(m => m.measurement_type === 2)
  }
  return measurements.value
})

const measurementUnit = computed(() => {
  if (createMeasureForm.value.measurement_type === 1) {
    return 'atoms/cm³'
  } else if (createMeasureForm.value.measurement_type === 2) {
    return 'μm'
  }
  return ''
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

// 处理表格选择变化
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
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

// 删除晶圆
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除晶片 "${row.wafer_no}" 吗？此操作不可恢复！`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await waferAPI.deleteWafer(row.wafer_no)
      ElMessage.success('删除成功')
      loadData() // 重新加载数据
    } catch (error) {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 批量删除晶圆
const handleBatchDelete = () => {
  if (selectedRows.value.length === 0) return

  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedRows.value.length} 个晶片吗？此操作不可恢复！`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const waferNos = selectedRows.value.map(row => row.wafer_no)
      await waferAPI.batchDeleteWafers(waferNos)
      ElMessage.success('批量删除成功')
      selectedRows.value = [] // 清空选中项
      loadData() // 重新加载数据
    } catch (error) {
      if (error.response && error.response.data && error.response.data.detail) {
        ElMessage.error(error.response.data.detail)
      } else {
        ElMessage.error('批量删除失败')
      }
      console.error(error)
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 显示导入对话框
const showImportDialog = () => {
  importDialogVisible.value = true
  selectedFile.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 处理文件选择
const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

// 执行导入
const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  importLoading.value = true
  
  try {
    const result = await waferAPI.importWafersFromExcel(selectedFile.value)
    
    ElMessage.success({
      message: `${result.message}（跳过已存在的 ${result.skipped_wafers} 个晶片）`,
      duration: 5000
    })
    
    importDialogVisible.value = false
    selectedFile.value = null
    loadData() // 重新加载数据
  } catch (error) {
    if (error.response && error.response.data && error.response.data.detail) {
      ElMessage.error(`导入失败: ${error.response.data.detail}`)
    } else {
      ElMessage.error('导入失败，请检查文件格式是否正确')
    }
    console.error(error)
  } finally {
    importLoading.value = false
  }
}

// 下载导入模板
const downloadTemplate = async () => {
  try {
    const response = await api.downloadImportTemplate()
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '晶片数据导入模板.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('模板下载成功')
  } catch (error) {
    ElMessage.error('模板下载失败')
    console.error(error)
  }
}

// 显示新建晶片对话框
const showCreateDialog = () => {
  createDialogVisible.value = true
  // 重置表单
  createForm.value = {
    wafer_no: '',
    original_grade: '',
    concentration_target: null,
    thickness_target: null
  }
  // 清除验证状态
  setTimeout(() => {
    if (createFormRef.value) {
      createFormRef.value.clearValidate()
    }
  }, 0)
}

// 显示新建测量对话框
const showCreateMeasurementDialog = () => {
  createMeasurementDialogVisible.value = true
  // 设置晶片号并重置表单
  createMeasureForm.value = {
    wafer_no: currentWaferNo.value,
    measurement_type: null,
    point_number: null,
    value: null,
    measurement_equipment: 1,
    measured_at: new Date().toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).replace(/\//g, '-')
  }
  // 清除验证状态
  setTimeout(() => {
    if (createMeasureFormRef.value) {
      createMeasureFormRef.value.clearValidate()
    }
  }, 0)
}

// 提交新建晶片
const handleCreate = () => {
  if (!createFormRef.value) return
  createFormRef.value.validate(async (valid) => {
    if (!valid) return
    createLoading.value = true
    try {
      const data = {
        wafer_no: createForm.value.wafer_no,
        original_grade: createForm.value.original_grade || null,
        concentration_target: createForm.value.concentration_target
          ? Number(createForm.value.concentration_target)
          : null,
        thickness_target: createForm.value.thickness_target
          ? Number(createForm.value.thickness_target)
          : null
      }
      await waferAPI.createWafer(data)
      ElMessage.success('新建晶片成功，初始测量次数为 0')
      createDialogVisible.value = false
      loadData() // 重新加载数据
    } catch (error) {
      if (error.response && error.response.data && error.response.data.detail) {
        ElMessage.error(error.response.data.detail)
      } else {
        ElMessage.error('新建晶片失败')
      }
      console.error(error)
    } finally {
      createLoading.value = false
    }
  })
}

// 提交新建测量数据
const handleCreateMeasurement = () => {
  if (!createMeasureFormRef.value) return
  createMeasureFormRef.value.validate(async (valid) => {
    if (!valid) return
    createMeasurementLoading.value = true
    try {
      const data = {
        wafer_no: createMeasureForm.value.wafer_no,
        measurement_type: createMeasureForm.value.measurement_type,
        point_number: createMeasureForm.value.point_number,
        value: Number(createMeasureForm.value.value),
        measured_at: createMeasureForm.value.measured_at,
        measurement_equipment: createMeasureForm.value.measurement_equipment
      }
      await measurementAPI.createMeasurement(data)
      ElMessage.success('新建测量数据成功')
      createMeasurementDialogVisible.value = false
      // 刷新测量明细
      showMeasurementDetail({ wafer_no: currentWaferNo.value })
    } catch (error) {
      if (error.response && error.response.data && error.response.data.detail) {
        ElMessage.error(error.response.data.detail)
      } else {
        ElMessage.error('新建测量数据失败')
      }
      console.error(error)
    } finally {
      createMeasurementLoading.value = false
    }
  })
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

// 格式化测量值
const formatValue = (row) => {
  if (row.value === null || row.value === undefined) return '-'
  
  if (row.measurement_type === 1) {
    // 浓度：科学计数法 1.50×10^15 atoms/cm³
    const exponential = row.value.toExponential(2)
    const [mantissa, exponent] = exponential.split('e+')
    return `${mantissa}×10^${exponent} atoms/cm³`
  } else {
    // 厚度：科学计数法 1.00×10^1 μm
    const exponential = row.value.toExponential(2)
    const [mantissa, exponent] = exponential.split('e+')
    return `${mantissa}×10^${exponent} μm`
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

// 获取等级标签类型
const getGradeType = (grade) => {
  const gradeMap = {
    'D': 'warning',
    'NG': 'danger'
  }
  return gradeMap[grade] || 'info'
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

.measure-actions {
  margin-top: 15px;
  margin-bottom: 10px;
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

/* 统计卡片样式 */
.stat-card {
  transition: all 0.3s ease;
  border-radius: 8px;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.active-card {
  background-color: #ecf5ff !important;
  border-color: #b3d8ff !important;
  color: #409eff !important;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2) !important;
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
