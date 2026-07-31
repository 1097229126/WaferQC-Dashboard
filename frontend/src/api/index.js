import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API 错误:', error.message)
    return Promise.reject(error)
  }
)

// 晶圆 API 调用
export const waferAPI = {
  // 获取晶圆列表（带统计信息）
  getWafers: (skip = 0, limit = 100) => 
    apiClient.get('/wafers/', { params: { skip, limit } }),
  
  // 获取单个晶圆详情
  getWaferByNo: (waferNo) => 
    apiClient.get(`/wafers/${waferNo}`),
  
  // 创建晶圆
  createWafer: (waferData) => 
    apiClient.post('/wafers/', waferData),
  
  // 删除晶圆
  deleteWafer: (waferNo) => 
    apiClient.delete(`/wafers/${waferNo}`),
  
  // 批量创建晶圆和测量数据
  createWaferWithMeasurements: (waferNo, measurements) => 
    apiClient.post('/wafers/bulk-create', measurements, {
      params: { wafer_no: waferNo }
    })
}

// 测量数据 API 调用
export const measurementAPI = {
  // 创建测量数据
  createMeasurement: (measurementData) => 
    apiClient.post('/measurements/', measurementData),
  
  // 获取晶圆的测量数据
  getWaferMeasurements: (waferNo) => 
    apiClient.get(`/wafers/${waferNo}/measurements`)
}

export default apiClient
