import { useState, useCallback } from 'react'
import { Header } from './layouts/Header'
import { LeftPanel } from './layouts/LeftPanel'
import { RightPanel } from './layouts/RightPanel'
import { EditorPanel } from './layouts/EditorPanel'
import { ResizeHandle } from './components/ResizeHandle'
import { useResizable } from './hooks/useResizable'
import { calculateWordCount, calculateSentenceCount, calculateReadingTime } from './utils/textUtils'
import { getSession } from './api'

function App() {
  const [isIDEMode, setIsIDEMode] = useState(false)
  const [content, setContent] = useState(
    '人工智能正在改变世界。它帮助我们更快地学习新知识。然而，我们必须谨慎对待它的发展。'
  )
  const [currentSession, setCurrentSession] = useState(null)
  
  const { leftWidth, rightWidth, containerRef, handleMouseDown } = useResizable()

  const wordCount = calculateWordCount(content)
  const sentenceCount = calculateSentenceCount(content)
  const readingTime = calculateReadingTime(wordCount)

  // 选择会话时加载详情
  const handleSessionSelect = useCallback(async (session) => {
    const sessionId = session.id || session.session_id
    try {
      const detail = await getSession(sessionId)
      setCurrentSession(detail)
      // 如果会话有内容，加载到编辑器
      if (detail.content) {
        setContent(detail.content)
      }
      // 根据会话模式切换编辑器模式 (science -> IDE模式, literature -> 写作模式)
      if (detail.mode === 'science') {
        setIsIDEMode(true)
      } else if (detail.mode === 'literature') {
        setIsIDEMode(false)
      }
    } catch (err) {
      console.error('加载会话详情失败:', err)
      // 即使加载详情失败，也设置基本信息
      setCurrentSession(session)
    }
  }, [])

  return (
    <div ref={containerRef} className="h-screen bg-gray-50 flex flex-col overflow-hidden">
      <Header wordCount={wordCount} sentenceCount={sentenceCount} readingTime={readingTime} />

      <div className="flex-1 flex overflow-hidden">
        <LeftPanel 
          width={leftWidth} 
          onSessionSelect={handleSessionSelect}
          activeSessionId={currentSession?.id || currentSession?.session_id}
        />
        <ResizeHandle onMouseDown={handleMouseDown('left')} />
        <EditorPanel 
          isIDEMode={isIDEMode} 
          onModeToggle={setIsIDEMode}
          content={content}
          setContent={setContent}
          sentenceCount={sentenceCount}
          sessionId={currentSession?.id || currentSession?.session_id}
        />
        <ResizeHandle onMouseDown={handleMouseDown('right')} />
        <RightPanel width={rightWidth} />
      </div>
    </div>
  )
}

export default App
