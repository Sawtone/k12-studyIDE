import React, { useState } from 'react'
import { Header } from './layouts/Header'
import { LeftPanel } from './layouts/LeftPanel'
import { RightPanel } from './layouts/RightPanel'
import { EditorPanel } from './layouts/EditorPanel'
import { ResizeHandle } from './components/ResizeHandle'
import { useResizable } from './hooks/useResizable'
import { calculateWordCount, calculateSentenceCount, calculateReadingTime } from './utils/textUtils'

function App() {
  const [isIDEMode, setIsIDEMode] = useState(false)
  const [content, setContent] = useState(
    '人工智能正在改变世界。它帮助我们更快地学习新知识。然而，我们必须谨慎对待它的发展。'
  )
  
  const { leftWidth, rightWidth, containerRef, handleMouseDown } = useResizable()

  const wordCount = calculateWordCount(content)
  const sentenceCount = calculateSentenceCount(content)
  const readingTime = calculateReadingTime(wordCount)

  return (
    <div ref={containerRef} className="h-screen bg-gray-50 flex flex-col overflow-hidden">
      <Header wordCount={wordCount} sentenceCount={sentenceCount} readingTime={readingTime} />

      <div className="flex-1 flex overflow-hidden">
        <LeftPanel width={leftWidth} />
        <ResizeHandle onMouseDown={handleMouseDown('left')} />
        <EditorPanel 
          isIDEMode={isIDEMode} 
          onModeToggle={setIsIDEMode}
          content={content}
          setContent={setContent}
          sentenceCount={sentenceCount}
        />
        <ResizeHandle onMouseDown={handleMouseDown('right')} />
        <RightPanel width={rightWidth} />
      </div>
    </div>
  )
}

export default App
