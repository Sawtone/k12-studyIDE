import React from 'react'
import { FileText } from 'lucide-react'
import { ModeToggle } from '../components/ModeToggle'
import { Editor } from '../features/Editor/Editor'

export const EditorPanel = ({ isIDEMode, onModeToggle, content, setContent, sentenceCount }) => {
  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-white mx-0.5 rounded-t-xl shadow-sm border border-gray-200 border-b-0 mt-2">
      <div className="h-12 border-b border-gray-100 flex items-center justify-between px-4 bg-gray-50/50 rounded-t-xl">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <FileText size={16} className="text-indigo-500" />
          <span className="font-medium">AI伦理.md</span>
          <span className="text-gray-400">·</span>
          <span className="text-gray-400">{sentenceCount} 句</span>
        </div>
        
        <ModeToggle isIDEMode={isIDEMode} onToggle={onModeToggle} />
      </div>
      
      <div className="flex-1 overflow-hidden">
        <Editor isIDEMode={isIDEMode} content={content} setContent={setContent} />
      </div>
    </div>
  )
}
