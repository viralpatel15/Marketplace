import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({ baseURL: API_URL })

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const getProducts = (filters: Record<string, unknown> = {}) =>
  api.get('/api/products', { params: filters }).then((r) => r.data)

export const searchProducts = (q: string, filters: Record<string, unknown> = {}) =>
  api.get('/api/products/search', { params: { q, ...filters } }).then((r) => r.data)

export const getProduct = (slug: string) =>
  api.get(`/api/products/${slug}`).then((r) => r.data.data)

export const getCompany = (slug: string) =>
  api.get(`/api/companies/${slug}`).then((r) => r.data.data)

export const getCategories = () =>
  api.get('/api/categories').then((r) => r.data.data)

export const getFeaturedProducts = () =>
  api.get('/api/products/featured').then((r) => r.data.data)
