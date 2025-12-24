import { useState, useCallback, useRef } from 'react'
import { syncEditor, getEditorHistory, restoreSession } from '../api/sessionApi'

/**
 * 编辑器同步 Hook
 * 处理编辑器内容同步、历史记录和版本恢复
 */
export function useEditorSync(sessionId) {
  const [syncing, setSyncing] = useState(false)
  const [history, setHistory] = useState([])
  const [error, setError] = useState(null)
  const syncTimeoutRef = useRef(null)

  // 同步编辑器状态 (带防抖)
  const sync = useCallback(async (data, debounceMs = 1000) => {
    if (!sessionId) return

    // 清除之前的定时器
    if (syncTimeoutRef.current) {
      clearTimeout(syncTimeoutRef.current)
    }

    // 防抖处理
    syncTimeoutRef.current = setTimeout(async () => {
      setSyncing(true)
      setError(null)
      try {
        const result = await syncEditor(sessionId, data)
        return result
      } catch (err) {
        setError(err.message)
        throw err
      } finally {
        setSyncing(false)
      }
    }, debounceMs)
  }, [sessionId])

  // 立即同步 (不防抖)
  const syncImmediate = useCallback(async (data) => {
    if (!sessionId) return
    
    if (syncTimeoutRef.current) {
      clearTimeout(syncTimeoutRef.current)
    }

    setSyncing(true)
    setError(null)
    try {
      return await syncEditor(sessionId, data)
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setSyncing(false)
    }
  }, [sessionId])

  // 获取编辑历史
  const fetchHistory = useCallback(async (params = {}) => {
    if (!sessionId) return
    
    setError(null)
    try {
      const result = await getEditorHistory(sessionId, params)
      setHistory(result.history || result.data || [])
      return result
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [sessionId])

  // 恢复到指定版本
  const restore = useCallback(async (data) => {
    if (!sessionId) return
    
    setSyncing(true)
    setError(null)
    try {
      return await restoreSession(sessionId, data)
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setSyncing(false)
    }
  }, [sessionId])

  return {
    syncing,
    history,
    error,
    sync,
    syncImmediate,
    fetchHistory,
    restore,
  }
}
