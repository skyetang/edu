import request from '@/utils/request'

// ================== 工作流分类管理 ==================

export function getWorkflowCategories() {
  return request({
    url: '/workflows/categories/',
    method: 'get'
  })
}

export function createWorkflowCategory(data) {
  return request({
    url: '/workflows/categories/',
    method: 'post',
    data
  })
}

export function updateWorkflowCategory(id, data) {
  return request({
    url: `/workflows/categories/${id}/`,
    method: 'put',
    data
  })
}

export function deleteWorkflowCategory(id) {
  return request({
    url: `/workflows/categories/${id}/`,
    method: 'delete'
  })
}

// ================== 工作流管理 ==================

export function getWorkflows(params) {
  return request({
    url: '/workflows/list/',
    method: 'get',
    params
  })
}

export function createWorkflow(data) {
  return request({
    url: '/workflows/list/',
    method: 'post',
    data
  })
}

export function updateWorkflow(id, data) {
  return request({
    url: `/workflows/list/${id}/`,
    method: 'put',
    data
  })
}

export function deleteWorkflow(id) {
  return request({
    url: `/workflows/list/${id}/`,
    method: 'delete'
  })
}
