import axios from 'axios'

// 统一的axios实例:所有组件共用这个baseURL,后端换端口只改这一处
const API = axios.create({
  baseURL: 'http://127.0.0.1:8000/api'
})

// 响应拦截:后端报错时统一在这里弹出提示,组件里就不用重复try/catch
API.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const msg = error.response?.data?.detail || '网络错误,请检查后端是否启动'
    alert(typeof msg === 'string' ? msg : '请求失败')
    return Promise.reject(error)
  }
)

export default API
