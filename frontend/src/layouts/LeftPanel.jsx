import React from 'react'
import { FolderOpen, Bot } from 'lucide-react'
import { FileTree } from '../features/FileTree/FileTree'
import { AIChat } from '../features/AIChat/AIChat'

export const LeftPanel = ({ width }) => {
  return (
    <div className="bg-white border-r border-gray-200 flex flex-col overflow-hidden" style={{ width }}>
      <div className="flex-1 p-4 border-b border-gray-100 overflow-auto">
        <div className="flex items-center gap-2 mb-3 text-gray-700">
          <FolderOpen size={16} className="text-indigo-500" />
          <span className="font-semibold text-sm">项目文件</span>
        </div>
        <FileTree />
      </div>
      
      <div className="flex-1 p-4 overflow-hidden flex flex-col">
        <div className="flex items-center gap-2 mb-3 text-gray-700">
          <Bot size={16} className="text-indigo-500" />
          <span className="font-semibold text-sm">AI助手</span>
        </div>
        <div className="flex-1 overflow-hidden">
          <AIChat />
        </div>
      </div>
    </div>
  )
}
