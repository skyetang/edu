import request from '@/utils/request'

export function getPlans() {
  return request.get('/membership/plans/')
}

export function createPlan(data) {
  return request.post('/membership/plans/', data)
}

export function updatePlan(data) {
  return request.patch('/membership/plans/', data)
}

export function deletePlan(id) {
  return request.delete('/membership/plans/', { params: { id } })
}

export function createOrder(planId) {
  return request.post('/membership/orders/create/', { plan_id: planId })
}

export function getOrderDetail(orderNo) {
  return request.get('/membership/orders/detail/', { params: { order_no: orderNo } })
}

export function payOrder(orderNo, paymentMethod) {
  return request.post('/membership/orders/pay/', { order_no: orderNo, payment_method: paymentMethod })
}

export function getOrders(params) {
  return request.get('/membership/orders/list/', { params })
}

export function cancelOrder(orderNo) {
  return request.post('/membership/orders/action/', { order_no: orderNo, action: 'cancel' })
}

export function refundOrder(orderNo) {
  return request.post('/membership/orders/action/', { order_no: orderNo, action: 'refund' })
}
