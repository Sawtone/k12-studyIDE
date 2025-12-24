import { forwardRef } from 'react'
import { WritingMode } from './WritingMode.jsx'
import { IDEMode } from './IDEMode.jsx'

export const Editor = forwardRef(({ isIDEMode, content, setContent, onAnalysisDataChange }, ref) => {
  if (isIDEMode) {
    return <IDEMode ref={ref} content={content} onContentChange={setContent} onAnalysisDataChange={onAnalysisDataChange} />
  }
  
  return <WritingMode content={content} onContentChange={setContent} />
})

Editor.displayName = 'Editor'
