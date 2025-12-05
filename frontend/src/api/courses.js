import request from '@/utils/request'

// ================== 分类管理 ==================

export function getCategories() {
  return request({
    url: '/courses/categories/',
    method: 'get'
  })
}

export function createCategory(data) {
  return request({
    url: '/courses/categories/',
    method: 'post',
    data
  })
}

export function updateCategory(id, data) {
  return request({
    url: `/courses/categories/${id}/`,
    method: 'put',
    data
  })
}

export function deleteCategory(id) {
  return request({
    url: `/courses/categories/${id}/`,
    method: 'delete'
  })
}

// ================== 课程管理 ==================

export function getCourses(params) {
  return request({
    url: '/courses/admin/list/',
    method: 'get',
    params
  })
}

export function createCourse(data) {
  return request({
    url: '/courses/admin/list/',
    method: 'post',
    data
  })
}

export function updateCourse(id, data) {
  return request({
    url: `/courses/admin/list/${id}/`,
    method: 'put',
    data
  })
}

export function deleteCourse(id) {
  return request({
    url: `/courses/admin/list/${id}/`,
    method: 'delete'
  })
}

// ================== 章节管理 ==================

export function getChapters(params) {
  return request({
    url: '/courses/chapters/',
    method: 'get',
    params
  })
}

export function createChapter(data) {
  return request({
    url: '/courses/chapters/',
    method: 'post',
    data
  })
}

export function updateChapter(id, data) {
  return request({
    url: `/courses/chapters/${id}/`,
    method: 'put',
    data
  })
}

export function deleteChapter(id) {
  return request({
    url: `/courses/chapters/${id}/`,
    method: 'delete'
  })
}

// ================== 课时管理 ==================

export function createLesson(data) {
  return request({
    url: '/courses/lessons/',
    method: 'post',
    data
  })
}

export function updateLesson(id, data) {
  return request({
    url: `/courses/lessons/${id}/`,
    method: 'put',
    data
  })
}

export function deleteLesson(id) {
  return request({
    url: `/courses/lessons/${id}/`,
    method: 'delete'
  })
}

// ================== 客户端API ==================

export function getClientCourseList(params) {
  return request({
    url: '/courses/list/',
    method: 'get',
    params
  })
}

export function getClientCourseDetail(id) {
  return request({
    url: `/courses/${id}/detail/`,
    method: 'get'
  })
}

export function getLessonPlayAuth(id) {
  return request({
    url: `/courses/lessons/${id}/auth/`,
    method: 'get'
  })
}
