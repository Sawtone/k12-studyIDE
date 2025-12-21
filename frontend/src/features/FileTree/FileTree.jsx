import React, { useState } from 'react'
import { FolderOpen, File, FileText, ChevronRight, ChevronDown } from 'lucide-react'

export const FileTree = () => {
  const [expanded, setExpanded] = useState({ project: true, essays: true })
  const toggle = (key) => setExpanded(prev => ({ ...prev, [key]: !prev[key] }))

  return (
    <div className="text-sm select-none">
      <div
        className="flex items-center gap-2 py-1.5 px-2 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
        onClick={() => toggle('project')}
      >
        {expanded.project ? <ChevronDown size={14} className="text-gray-400" /> : <ChevronRight size={14} className="text-gray-400" />}
        <FolderOpen size={16} className="text-indigo-500" />
        <span className="font-medium text-gray-700">我的项目</span>
      </div>
      
      {expanded.project && (
        <div className="ml-4">
          <div
            className="flex items-center gap-2 py-1.5 px-2 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
            onClick={() => toggle('essays')}
          >
            {expanded.essays ? <ChevronDown size={14} className="text-gray-400" /> : <ChevronRight size={14} className="text-gray-400" />}
            <FolderOpen size={16} className="text-orange-400" />
            <span className="text-gray-600">作文集</span>
          </div>
          
          {expanded.essays && (
            <div className="ml-4">
              <div className="flex items-center gap-2 py-1.5 px-2 rounded-lg bg-indigo-50 border border-indigo-100 cursor-pointer">
                <FileText size={16} className="text-indigo-500" />
                <span className="text-indigo-600 font-medium">AI伦理.md</span>
              </div>
              <div className="flex items-center gap-2 py-1.5 px-2 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                <File size={16} className="text-gray-400" />
                <span className="text-gray-500">读书笔记.md</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
