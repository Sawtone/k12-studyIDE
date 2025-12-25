import { useState, useCallback, useEffect, useRef } from 'react'
import { Header } from './layouts/Header'
import { LeftPanel } from './layouts/LeftPanel'
import { RightPanel } from './layouts/RightPanel'
import { EditorPanel } from './layouts/EditorPanel'
import { ResizeHandle } from './components/ResizeHandle'
import { useResizable } from './hooks/useResizable'
import { calculateWordCount, calculateSentenceCount, calculateReadingTime } from './utils/textUtils'
import { getSession, syncEditor, getEditorHistory } from './api'

const DEFAULT_CONTENT = '开始写作...'

function App() {
  const [isIDEMode, setIsIDEMode] = useState(false)
  const [content, setContent] = useState(DEFAULT_CONTENT)
  const [currentSession, setCurrentSession] = useState(null)
  const [syncing, setSyncing] = useState(false)
  const [lastSaved, setLastSaved] = useState(null)

  const { leftWidth, rightWidth, containerRef, handleMouseDown } = useResizable()

  // 防抖同步的定时器
  const syncTimeoutRef = useRef(null)
  // 记录上次同步的内容，避免重复同步
  const lastSyncedContentRef = useRef('')

  const sessionId = currentSession?.id || currentSession?.session_id

  const wordCount = calculateWordCount(content)
  const sentenceCount = calculateSentenceCount(content)
  const readingTime = calculateReadingTime(wordCount)

  // 同步内容到后端（带防抖）
  const syncContent = useCallback(
    async (newContent) => {
      if (!sessionId) return
      if (newContent === lastSyncedContentRef.current) return

      // 清除之前的定时器
      if (syncTimeoutRef.current) {
        clearTimeout(syncTimeoutRef.current)
      }

      // 防抖：1.5秒后同步
      syncTimeoutRef.current = setTimeout(async () => {
        setSyncing(true)
        try {
          await syncEditor(sessionId, { content: newContent })
          lastSyncedContentRef.current = newContent
          setLastSaved(new Date())
        } catch (err) {
          console.error('同步失败:', err)
        } finally {
          setSyncing(false)
        }
      }, 1500)
    },
    [sessionId]
  )

  // 内容变化时触发同步
  const handleContentChange = useCallback(
    (newContent) => {
      setContent(newContent)
      syncContent(newContent)
    },
    [syncContent]
  )

  // 选择会话时加载详情
  const handleSessionSelect = useCallback(async (session) => {
    const id = session.id || session.session_id

    // 清除待执行的同步
    if (syncTimeoutRef.current) {
      clearTimeout(syncTimeoutRef.current)
    }

    try {
      // 获取会话详情
      const detail = await getSession(id)
      setCurrentSession(detail)

      // 根据会话模式切换编辑器模式
      if (detail.mode === 'science') {
        setIsIDEMode(true)
      } else if (detail.mode === 'literature') {
        setIsIDEMode(false)
      }

      // 尝试获取最新的编辑器内容
      let sessionContent = ''
      try {
        const historyResult = await getEditorHistory(id, { limit: 1 })
        if (historyResult.history && historyResult.history.length > 0) {
          sessionContent = historyResult.history[0].content || ''
        }
      } catch (historyErr) {
        console.log('获取编辑历史失败，使用空内容:', historyErr)
      }

      setContent(sessionContent || DEFAULT_CONTENT)
      lastSyncedContentRef.current = sessionContent || ''
      setLastSaved(detail.updated_at ? new Date(detail.updated_at) : null)
    } catch (err) {
      console.error('加载会话详情失败:', err)
      // 即使加载详情失败，也设置基本信息
      setCurrentSession(session)
      setContent(DEFAULT_CONTENT)
      lastSyncedContentRef.current = ''
    }
  }, [])

  // 组件卸载时清理定时器
  useEffect(() => {
    return () => {
      if (syncTimeoutRef.current) {
        clearTimeout(syncTimeoutRef.current)
      }
    }
  }, [])

  return (
    <div ref={containerRef} className="h-screen bg-gray-50 flex flex-col overflow-hidden">
      <Header
        wordCount={wordCount}
        sentenceCount={sentenceCount}
        readingTime={readingTime}
        syncing={syncing}
        lastSaved={lastSaved}
        sessionTitle={currentSession?.title}
      />

      <div className="flex-1 flex overflow-hidden">
        <LeftPanel
          width={leftWidth}
          onSessionSelect={handleSessionSelect}
          activeSessionId={sessionId}
        />
        <ResizeHandle onMouseDown={handleMouseDown('left')} />
        <EditorPanel
          isIDEMode={isIDEMode}
          onModeToggle={setIsIDEMode}
          content={content}
          setContent={handleContentChange}
          sentenceCount={sentenceCount}
          sessionId={sessionId}
          sessionTitle={currentSession?.title}
        />
        <ResizeHandle onMouseDown={handleMouseDown('right')} />
        <RightPanel width={rightWidth} sessionId={sessionId} content={content} />
      </div>
    </div>
  )
}

export default App
