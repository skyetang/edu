import request from '@/utils/request'

export function sendCode(data) {
  return request.post('/auth/send_code', data)
}

export function loginWithCode(data) {
  return request.post('/auth/login/code', data)
}

export function loginWithPassword(data) {
  return request.post('/auth/login/password', data)
}

export function register(data) {
  return request.post('/auth/register', data)
}

export function getProfile() {
  return request.get('/auth/profile')
}

export function updateProfile(data) {
  return request.patch('/auth/profile', data)
}

export function changePassword(data) {
  return request.post('/auth/password/change', data)
}

export function verifyOldPhone(data) {
  return request.post('/auth/phone/verify-old', data)
}

export function changeNewPhone(data) {
  return request.post('/auth/phone/change-new', data)
}

export function uploadAvatar(data) {
  return request.post('/auth/profile/avatar', data)
}
