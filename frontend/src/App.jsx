import React, { useState } from 'react'
import { Header } from './layouts/Header'
import { LeftPanel } from './layouts/LeftPanel'
import { RightPanel } from './layouts/RightPanel'
import { EditorPanel } from './layouts/EditorPanel'
import { ResizeHandle } from './components/ResizeHandle'
import { useResizable } from './hooks/useResizable'
import { calculateWordCount, calculateSentenceCount, calculateReadingTime } from './utils/textUtils'

import { useRef } from 'react'

function App() {
  const [isIDEMode, setIsIDEMode] = useState(false)
  const [content, setContent] = useState(
    '人工智能正在改变世界。它帮助我们更快地学习新知识。然而，我们必须谨慎对待它的发展。'
  )
  const [analysisData, setAnalysisData] = useState(null)
  const [chatMessage, setChatMessage] = useState(null)
  const editorRef = useRef(null)
  
  const { leftWidth, rightWidth, containerRef, handleMouseDown } = useResizable()

  const wordCount = calculateWordCount(content)
  const sentenceCount = calculateSentenceCount(content)
  const readingTime = calculateReadingTime(wordCount)

  return (
    <div ref={containerRef} className="h-screen bg-gray-50 flex flex-col overflow-hidden">
      <Header wordCount={wordCount} sentenceCount={sentenceCount} readingTime={readingTime} />

      <div className="flex-1 flex overflow-hidden">
        <LeftPanel width={leftWidth} chatMessage={chatMessage} />
        <ResizeHandle onMouseDown={handleMouseDown('left')} />
        <EditorPanel 
          isIDEMode={isIDEMode} 
          onModeToggle={setIsIDEMode}
          content={content}
          setContent={setContent}
          sentenceCount={sentenceCount}
          onAnalysisDataChange={setAnalysisData}
          editorRef={editorRef}
        />
        <ResizeHandle onMouseDown={handleMouseDown('right')} />
        <RightPanel 
          width={rightWidth} 
          analysisData={analysisData} 
          content={content}
          editorRef={editorRef}
          onSendToChat={(message) => {
            setChatMessage(message)
            // 清除消息，以便下次可以再次发送
            setTimeout(() => setChatMessage(null), 100)
          }}
        />
      </div>
    </div>
  )
}

export default App
