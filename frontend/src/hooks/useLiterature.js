import { useState, useCallback } from 'react'
import * as literatureApi from '../api/literatureApi'

/**
 * 文科模式 Hook
 * 提供语法检查、文本润色、结构分析、健康度评估等功能
 */
export function useLiterature(sessionId) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // 语法检查结果
  const [grammarIssues, setGrammarIssues] = useState([])

  // 润色结果
  const [polishResults, setPolishResults] = useState([])

  // 文章结构
  const [structure, setStructure] = useState(null)

  // 健康度评分
  const [healthScore, setHealthScore] = useState(null)

  // 语法检查
  const checkGrammar = useCallback(
    async (content) => {
      if (!sessionId || !content) return
      setLoading(true)
      setError(null)
      try {
        const result = await literatureApi.checkGrammar({ session_id: sessionId, content })
        setGrammarIssues(result.issues || result.errors || [])
        return result
      } catch (err) {
        setError(err.message)
        throw err
      } finally {
        setLoading(false)
      }
    },
    [sessionId]
  )

  // 文本润色
  const polishText = useCallback(
    async (content, style) => {
      if (!sessionId || !content) return
      setLoading(true)
      setError(null)
      try {
        const result = await literatureApi.polishText({ session_id: sessionId, content, style })
        setPolishResults(result.versions || result.suggestions || [])
        return result
      } catch (err) {
        setError(err.message)
        throw err
      } finally {
        setLoading(false)
      }
    },
    [sessionId]
  )

  // 获取文章结构（缓存）
  const fetchStructure = useCallback(async () => {
    if (!sessionId) return
    setLoading(true)
    setError(null)
    try {
      const result = await literatureApi.getStructure(sessionId)
      setStructure(result)
      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [sessionId])

  // 重新分析文章结构
  const analyzeStructure = useCallback(
    async (content) => {
      if (!sessionId || !content) return
      setLoading(true)
      setError(null)
      try {
        const result = await literatureApi.analyzeStructure({ session_id: sessionId, content })
        setStructure(result)
        return result
      } catch (err) {
        setError(err.message)
        throw err
      } finally {
        setLoading(false)
      }
    },
    [sessionId]
  )

  // 获取健康度（缓存）
  const fetchHealthScore = useCallback(async () => {
    if (!sessionId) return
    setLoading(true)
    setError(null)
    try {
      const result = await literatureApi.getHealthScore(sessionId)
      setHealthScore(result)
      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [sessionId])

  // 重新评估健康度
  const analyzeHealth = useCallback(
    async (content) => {
      if (!sessionId || !content) return
      setLoading(true)
      setError(null)
      try {
        const result = await literatureApi.analyzeHealth({ session_id: sessionId, content })
        setHealthScore(result)
        return result
      } catch (err) {
        setError(err.message)
        throw err
      } finally {
        setLoading(false)
      }
    },
    [sessionId]
  )

  return {
    loading,
    error,
    grammarIssues,
    polishResults,
    structure,
    healthScore,
    checkGrammar,
    polishText,
    fetchStructure,
    analyzeStructure,
    fetchHealthScore,
    analyzeHealth,
  }
}
