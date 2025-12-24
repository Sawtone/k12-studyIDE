/**
 * 会话管理 API
 * 基于接口文档: /api/v1/sessions
 */

const API_BASE = '/api/v1'

/**
 * 创建新会话
 * POST /api/v1/sessions
 * @param {Object} data - CreateSessionRequest
 * @returns {Promise<SessionResponse>}
 */
export async function createSession(data) {
  const response = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error(`创建会话失败: ${response.status}`)
  return response.json()
}

/**
 * 获取会话列表
 * GET /api/v1/sessions
 * @param {Object} params - 查询参数
 * @param {string} params.user_id - 用户ID (必填)
 * @param {string} [params.session_status] - 会话状态
 * @param {string} [params.mode] - 模式
 * @param {number} [params.page=1] - 页码
 * @param {number} [params.limit=20] - 每页数量
 * @returns {Promise<SessionListResponse>}
 */
export async function getSessionList({ user_id, session_status, mode, page = 1, limit = 20 }) {
  const params = new URLSearchParams({ user_id, page: String(page), limit: String(limit) })
  if (session_status) params.append('session_status', session_status)
  if (mode) params.append('mode', mode)
  
  const response = await fetch(`${API_BASE}/sessions?${params}`)
  if (!response.ok) throw new Error(`获取会话列表失败: ${response.status}`)
  return response.json()
}

/**
 * 获取会话详情
 * GET /api/v1/sessions/{session_id}
 * @param {string} sessionId - 会话ID
 * @returns {Promise<SessionDetailResponse>}
 */
export async function getSession(sessionId) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}`)
  if (!response.ok) throw new Error(`获取会话详情失败: ${response.status}`)
  return response.json()
}


/**
 * 更新会话信息
 * PATCH /api/v1/sessions/{session_id}
 * @param {string} sessionId - 会话ID
 * @param {Object} data - UpdateSessionRequest
 * @returns {Promise<SessionDetailResponse>}
 */
export async function updateSession(sessionId, data) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error(`更新会话失败: ${response.status}`)
  return response.json()
}

/**
 * 删除会话 (软删除)
 * DELETE /api/v1/sessions/{session_id}
 * @param {string} sessionId - 会话ID
 * @returns {Promise<void>}
 */
export async function deleteSession(sessionId) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error(`删除会话失败: ${response.status}`)
  // 204 No Content
}

/**
 * 同步编辑器状态
 * POST /api/v1/sessions/{session_id}/editor/sync
 * @param {string} sessionId - 会话ID
 * @param {Object} data - SyncEditorRequest
 * @returns {Promise<EditorSyncResponse>}
 */
export async function syncEditor(sessionId, data) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/editor/sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error(`同步编辑器状态失败: ${response.status}`)
  return response.json()
}

/**
 * 恢复会话到指定版本
 * POST /api/v1/sessions/{session_id}/restore
 * @param {string} sessionId - 会话ID
 * @param {Object} data - RestoreSessionRequest
 * @returns {Promise<EditorSyncResponse>}
 */
export async function restoreSession(sessionId, data) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/restore`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error(`恢复会话失败: ${response.status}`)
  return response.json()
}

/**
 * 获取编辑历史
 * GET /api/v1/sessions/{session_id}/editor/history
 * @param {string} sessionId - 会话ID
 * @param {Object} [params] - 查询参数
 * @param {number} [params.from_version] - 起始版本
 * @param {number} [params.to_version] - 结束版本
 * @param {number} [params.limit=50] - 数量限制
 * @returns {Promise<EditorHistoryResponse>}
 */
export async function getEditorHistory(sessionId, { from_version, to_version, limit = 50 } = {}) {
  const params = new URLSearchParams({ limit: String(limit) })
  if (from_version != null) params.append('from_version', String(from_version))
  if (to_version != null) params.append('to_version', String(to_version))
  
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/editor/history?${params}`)
  if (!response.ok) throw new Error(`获取编辑历史失败: ${response.status}`)
  return response.json()
}
