import client from './client'
export const getEntities = () => client.get('/entities/').then(r => r.data)
export const createEntity = (data) => client.post('/entities/', data).then(r => r.data)
export const updateEntity = (id, data) => client.put(`/entities/${id}`, data).then(r => r.data)
export const deleteEntity = (id) => client.delete(`/entities/${id}`)
