import { useState, useCallback } from 'react'
import * as sessionApi from '../api/sessionApi'

/**
 * 会话管理 Hook
 * 提供会话的 CRUD 操作和状态管理
 */
export function useSession() {
  const [session, setSession] = useState(null)
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // 创建会话
  const createSession = useCallback(async (data) => {
    setLoading(true)
    setError(null)
    try {
      const result = await sessionApi.createSession(data)
      setSession(result)
      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  // 获取会话列表
  const fetchSessions = useCallback(async (params) => {
    setLoading(true)
    setError(null)
    try {
      const result = await sessionApi.getSessionList(params)
      setSessions(result.sessions || result.data || [])
      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  // 获取会话详情
  const fetchSession = useCallback(async (sessionId) => {
    setLoading(true)
    setError(null)
    try {
      const result = await sessionApi.getSession(sessionId)
      setSession(result)
      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])


  // 更新会话
  const updateSession = useCallback(async (sessionId, data) => {
    setLoading(true)
    setError(null)
    try {
      const result = await sessionApi.updateSession(sessionId, data)
      setSession(result)
      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  // 删除会话
  const deleteSession = useCallback(async (sessionId) => {
    setLoading(true)
    setError(null)
    try {
      await sessionApi.deleteSession(sessionId)
      setSessions(prev => prev.filter(s => s.id !== sessionId))
      if (session?.id === sessionId) setSession(null)
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [session])

  return {
    session,
    sessions,
    loading,
    error,
    createSession,
    fetchSessions,
    fetchSession,
    updateSession,
    deleteSession,
    setSession,
  }
}
