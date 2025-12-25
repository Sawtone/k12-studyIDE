import { useState } from 'react'
import { Sparkles, ChevronDown, X } from 'lucide-react'
import { FileTree } from '../features/FileTree/FileTree'
import { AIChat } from '../features/AIChat/AIChat'

export const LeftPanel = ({ width, onSessionSelect, activeSessionId, editorContent }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="bg-white border-r border-gray-200 flex flex-col overflow-hidden relative" style={{ width }}>
      {/* File Explorer - 始终占满 */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <FileTree onSessionSelect={onSessionSelect} activeSessionId={activeSessionId} />
      </div>

      {/* 底部按钮 */}
      <div className="px-2 pb-2 pt-1 border-t border-gray-100">
        <button
          onClick={() => setIsExpanded(true)}
          className={`w-full px-3 py-2.5 
                     bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50
                     border border-indigo-200/60 rounded-lg
                     flex items-center justify-center gap-2
                     hover:from-indigo-100 hover:via-purple-100 hover:to-pink-100
                     hover:border-indigo-300/80 hover:shadow-sm
                     active:scale-[0.98]
                     transition-all duration-200 ${isExpanded ? 'opacity-0 pointer-events-none' : ''}`}
        >
          <Sparkles size={14} className="text-indigo-500" />
          <span className="text-xs font-semibold text-indigo-600/80 tracking-wide">
            问问小小思 AI
          </span>
        </button>
      </div>

      {/* 浮动聊天窗口 */}
      {isExpanded && (
        <>
          {/* 遮罩 */}
          <div 
            className="fixed inset-0 bg-black/5 z-40"
            onClick={() => setIsExpanded(false)}
          />
          
          {/* 聊天面板 - 浮动在左侧 */}
          <div 
            className="absolute left-2 right-2 bottom-2 z-50 
                       bg-white rounded-xl shadow-xl border border-gray-200
                       flex flex-col animate-slideUp"
            style={{ 
              height: 'calc(100% - 56px)',
              minWidth: '260px'
            }}
          >
            {/* 标题栏 */}
            <div className="px-3 py-2.5 flex items-center justify-between border-b border-gray-100 flex-shrink-0">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 
                              flex items-center justify-center">
                  <Sparkles size={12} className="text-white" />
                </div>
                <span className="text-sm font-semibold text-gray-700">
                  小小思 AI
                </span>
              </div>
              <button
                onClick={() => setIsExpanded(false)}
                className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X size={14} className="text-gray-400" />
              </button>
            </div>
            
            {/* 聊天区域 */}
            <div className="flex-1 overflow-hidden">
              <AIChat sessionId={activeSessionId} editorContent={editorContent} />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
