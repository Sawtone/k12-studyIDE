/**
 * 文科模式 API
 * 提供语法检查、文本润色、结构分析、健康度评估等功能
 */

const API_BASE = '/api/v1'

/**
 * 语法检查
 * POST /api/v1/literature/check/grammar
 * @param {Object} data - GrammarCheckRequest
 * @param {string} data.session_id - 会话ID
 * @param {string} data.content - 待检查的文本内容
 * @returns {Promise<GrammarCheckResponse>}
 */
export async function checkGrammar(data) {
  const response = await fetch(`${API_BASE}/literature/check/grammar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error(`语法检查失败: ${response.status}`)
  return response.json()
}

/**
 * 文本润色
 * POST /api/v1/literature/polish
 * @param {Object} data - PolishRequest
 * @param {string} data.session_id - 会话ID
 * @param {string} data.text - 待润色的文本
 * @param {string} [data.style] - 润色风格
 * @returns {Promise<PolishResponse>}
 */
export async function polishText({ session_id, content, text, style }) {
  const response = await fetch(`${API_BASE}/literature/polish`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id,
      text: text || content, // 兼容 content 和 text
      style,
    }),
  })
  if (!response.ok) throw new Error(`文本润色失败: ${response.status}`)
  return response.json()
}

/**
 * 获取文章结构（已缓存）
 * GET /api/v1/literature/structure/{session_id}
 * @param {string} sessionId - 会话ID
 * @returns {Promise<StructureAnalyzeResponse>}
 */
export async function getStructure(sessionId) {
  const response = await fetch(`${API_BASE}/literature/structure/${sessionId}`)
  if (!response.ok) throw new Error(`获取文章结构失败: ${response.status}`)
  return response.json()
}

/**
 * 获取文章健康度（已缓存）
 * GET /api/v1/literature/health/{session_id}
 * @param {string} sessionId - 会话ID
 * @returns {Promise<HealthScoreResponse>}
 */
export async function getHealthScore(sessionId) {
  const response = await fetch(`${API_BASE}/literature/health/${sessionId}`)
  if (!response.ok) throw new Error(`获取健康度失败: ${response.status}`)
  return response.json()
}

/**
 * 重新分析文章结构
 * POST /api/v1/literature/structure/analyze
 * @param {Object} data - StructureAnalyzeRequest
 * @param {string} data.session_id - 会话ID
 * @param {string} data.content - 文章内容
 * @returns {Promise<StructureAnalyzeResponse>}
 */
export async function analyzeStructure(data) {
  const response = await fetch(`${API_BASE}/literature/structure/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    // 如果是唯一约束冲突（数据已存在），尝试获取缓存
    const errorText = await response.text()
    if (errorText.includes('UniqueViolation') || errorText.includes('duplicate key')) {
      // 数据已存在，尝试获取缓存的结果
      return getStructure(data.session_id)
    }
    throw new Error(`分析文章结构失败: ${response.status}`)
  }
  return response.json()
}

/**
 * 重新评估文章健康度
 * POST /api/v1/literature/health/analyze
 * @param {Object} data - HealthScoreRequest
 * @param {string} data.session_id - 会话ID
 * @param {string} data.content - 文章内容
 * @returns {Promise<HealthScoreResponse>}
 */
export async function analyzeHealth(data) {
  const response = await fetch(`${API_BASE}/literature/health/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    // 如果是唯一约束冲突（数据已存在），尝试获取缓存
    const errorText = await response.text()
    if (errorText.includes('UniqueViolation') || errorText.includes('duplicate key')) {
      return getHealthScore(data.session_id)
    }
    throw new Error(`评估健康度失败: ${response.status}`)
  }
  return response.json()
}


/**
 * 获取语法检查结果（已缓存）
 * GET /api/v1/literature/grammar/{session_id}
 * @param {string} sessionId - 会话ID
 * @returns {Promise<GrammarCheckResponse>}
 */
export async function getGrammarResult(sessionId) {
  const response = await fetch(`${API_BASE}/literature/grammar/${sessionId}`)
  if (!response.ok) throw new Error(`获取语法检查结果失败: ${response.status}`)
  return response.json()
}

/**
 * 获取润色结果（已缓存）
 * GET /api/v1/literature/polish/{session_id}
 * @param {string} sessionId - 会话ID
 * @returns {Promise<PolishResponse>}
 */
export async function getPolishResult(sessionId) {
  const response = await fetch(`${API_BASE}/literature/polish/${sessionId}`)
  if (!response.ok) throw new Error(`获取润色结果失败: ${response.status}`)
  return response.json()
}
