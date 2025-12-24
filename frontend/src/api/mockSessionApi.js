/**
 * Mock 会话 API - 用于前端开发测试
 * 使用时将 sessionApi 的导入替换为此文件即可
 */

// 模拟数据存储
let mockSessions = [
  {
    id: 'session-001',
    user_id: 'user-001',
    title: '学习笔记 - AI基础',
    mode: 'writing',
    status: 'active',
    content: '人工智能正在改变世界。',
    created_at: '2024-12-20T10:00:00Z',
    updated_at: '2024-12-23T08:30:00Z',
  },
  {
    id: 'session-002',
    user_id: 'user-001',
    title: '代码练习 - React Hooks',
    mode: 'ide',
    status: 'active',
    content: 'const [state, setState] = useState()',
    created_at: '2024-12-21T14:00:00Z',
    updated_at: '2024-12-22T16:45:00Z',
  },
]

let mockHistory = []
let versionCounter = 1

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

export async function createSession(data) {
  await delay(300)
  const newSession = {
    id: `session-${Date.now()}`,
    user_id: data.user_id || 'user-001',
    title: data.title || '新会话',
    mode: data.mode || 'writing',
    status: 'active',
    content: data.content || '',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
  mockSessions.unshift(newSession)
  console.log('[Mock] 创建会话:', newSession)
  return newSession
}

export async function getSessionList({ user_id, session_status, mode, page = 1, limit = 20 }) {
  await delay(200)
  let filtered = mockSessions.filter((s) => s.user_id === user_id)
  if (session_status) filtered = filtered.filter((s) => s.status === session_status)
  if (mode) filtered = filtered.filter((s) => s.mode === mode)

  const start = (page - 1) * limit
  const data = filtered.slice(start, start + limit)
  console.log('[Mock] 获取会话列表:', { total: filtered.length, page, data })
  return { sessions: data, total: filtered.length, page, limit }
}


export async function getSession(sessionId) {
  await delay(150)
  const session = mockSessions.find((s) => s.id === sessionId)
  if (!session) throw new Error('会话不存在')
  console.log('[Mock] 获取会话详情:', session)
  return session
}

export async function updateSession(sessionId, data) {
  await delay(200)
  const index = mockSessions.findIndex((s) => s.id === sessionId)
  if (index === -1) throw new Error('会话不存在')
  mockSessions[index] = { ...mockSessions[index], ...data, updated_at: new Date().toISOString() }
  console.log('[Mock] 更新会话:', mockSessions[index])
  return mockSessions[index]
}

export async function deleteSession(sessionId) {
  await delay(200)
  const index = mockSessions.findIndex((s) => s.id === sessionId)
  if (index === -1) throw new Error('会话不存在')
  mockSessions.splice(index, 1)
  console.log('[Mock] 删除会话:', sessionId)
}

export async function syncEditor(sessionId, data) {
  await delay(100)
  const session = mockSessions.find((s) => s.id === sessionId)
  if (!session) throw new Error('会话不存在')

  // 记录历史
  mockHistory.push({
    version: versionCounter++,
    session_id: sessionId,
    content: data.content,
    cursor_position: data.cursor_position,
    timestamp: new Date().toISOString(),
  })

  session.content = data.content || session.content
  session.updated_at = new Date().toISOString()
  console.log('[Mock] 同步编辑器:', { sessionId, version: versionCounter - 1 })
  return { success: true, version: versionCounter - 1 }
}

export async function restoreSession(sessionId, data) {
  await delay(200)
  const historyItem = mockHistory.find((h) => h.session_id === sessionId && h.version === data.version)
  if (!historyItem) throw new Error('版本不存在')

  const session = mockSessions.find((s) => s.id === sessionId)
  if (session) session.content = historyItem.content

  console.log('[Mock] 恢复会话到版本:', data.version)
  return { success: true, content: historyItem.content, version: historyItem.version }
}

export async function getEditorHistory(sessionId, { from_version, to_version, limit = 50 } = {}) {
  await delay(150)
  let history = mockHistory.filter((h) => h.session_id === sessionId)
  if (from_version != null) history = history.filter((h) => h.version >= from_version)
  if (to_version != null) history = history.filter((h) => h.version <= to_version)
  history = history.slice(-limit)
  console.log('[Mock] 获取编辑历史:', { sessionId, count: history.length })
  return { history, total: history.length }
}
