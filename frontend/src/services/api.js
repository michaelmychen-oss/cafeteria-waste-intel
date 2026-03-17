import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

// Schools
export const getSchools = () => api.get('/schools/')
export const createSchool = (data) => api.post('/schools/', data)

// Reports
export const uploadReport = (formData) =>
  api.post('/reports/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
export const getReports = (schoolId) =>
  api.get('/reports/', { params: schoolId ? { school_id: schoolId } : {} })
export const getReport = (id) => api.get(`/reports/${id}`)

// Dashboard
export const getDashboardStats = () => api.get('/dashboard/stats')
export const getSchoolTrend = (schoolId) => api.get(`/dashboard/school/${schoolId}/trend`)
export const getWasteRecords = (schoolId) =>
  api.get('/dashboard/waste-records', { params: schoolId ? { school_id: schoolId } : {} })

export default api
