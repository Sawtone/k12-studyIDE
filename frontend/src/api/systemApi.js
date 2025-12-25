/**
 * 系统基础 API
 */

const API_BASE = '/api/v1'

/**
 * 健康检查
 * GET /health
 * @returns {Promise<Object>}
 */
export async function healthCheck() {
  const response = await fetch('/health')
  if (!response.ok) throw new Error(`健康检查失败: ${response.status}`)
  return response.json()
}

/**
 * 根路径
 * GET /
 * @returns {Promise<Object>}
 */
export async function getRoot() {
  const response = await fetch('/')
  if (!response.ok) throw new Error(`获取根路径失败: ${response.status}`)
  return response.json()
}

/**
 * 获取系统能力
 * GET /api/v1/system/capabilities
 * @returns {Promise<Object>}
 */
export async function getCapabilities() {
  const response = await fetch(`${API_BASE}/system/capabilities`)
  if (!response.ok) throw new Error(`获取系统能力失败: ${response.status}`)
  return response.json()
}
