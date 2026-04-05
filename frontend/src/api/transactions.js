import client from './client'
export const getTransactions = (params) => client.get('/transactions/', { params }).then(r => r.data)
export const createTransaction = (data) => client.post('/transactions/', data).then(r => r.data)
export const deleteTransaction = (id) => client.delete(`/transactions/${id}`)
