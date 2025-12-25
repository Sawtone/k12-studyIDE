/**
 * 智能对话 API
 */

const API_BASE = '/api/v1'

/**
 * 发送聊天消息
 * POST /api/v1/chat/message
 * @param {Object} data
 * @param {string} data.session_id - 会话ID
 * @param {string} data.message - 用户消息
 * @returns {Promise<ChatMessageResponse>}
 */
export async function sendChatMessage({ session_id, message }) {
  const response = await fetch(`${API_BASE}/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, message }),
  })
  if (!response.ok) throw new Error(`发送消息失败: ${response.status}`)
  return response.json()
}

/**
 * 获取聊天历史
 * GET /api/v1/chat/history/{session_id}
 * @param {string} sessionId - 会话ID
 * @returns {Promise<Array>}
 */
export async function getChatHistory(sessionId) {
  const response = await fetch(`${API_BASE}/chat/history/${sessionId}`)
  if (!response.ok) throw new Error(`获取聊天历史失败: ${response.status}`)
  return response.json()
}
