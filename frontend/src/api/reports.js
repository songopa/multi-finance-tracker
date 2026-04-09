import client from './client'
export const getReport = (params) => client.get('/reports/', { params }).then(r => r.data)
