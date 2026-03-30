import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以添加 token 等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api

// API 方法
export const pluginsApi = {
  list: () => api.get('/plugins'),
  get: (id: string) => api.get(`/plugins/${id}`),
  install: (id: string) => api.post(`/plugins/${id}/install`),
  uninstall: (id: string) => api.post(`/plugins/${id}/uninstall`),
  enable: (id: string) => api.post(`/plugins/${id}/enable`),
  disable: (id: string) => api.post(`/plugins/${id}/disable`),
  getConfig: (id: string) => api.get(`/plugins/${id}/config`),
  updateConfig: (id: string, config: any) => api.put(`/plugins/${id}/config`, config),
  execute: (id: string, data: any) => api.post(`/plugins/${id}/execute`, data)
}

export const tasksApi = {
  list: () => api.get('/tasks'),
  get: (id: string) => api.get(`/tasks/${id}`),
  create: (data: any) => api.post('/tasks', data),
  cancel: (id: string) => api.delete(`/tasks/${id}`),
  getResult: (id: string) => api.get(`/tasks/${id}/result`)
}

export const filesApi = {
  list: () => api.get('/files'),
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  download: (id: string) => api.get(`/files/${id}/download`),
  delete: (id: string) => api.delete(`/files/${id}`)
}
