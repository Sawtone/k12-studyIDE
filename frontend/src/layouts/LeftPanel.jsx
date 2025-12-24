import { useState } from 'react'
import { Sparkles, ChevronDown } from 'lucide-react'
import { FileTree } from '../features/FileTree/FileTree'
import { AIChat } from '../features/AIChat/AIChat'

export const LeftPanel = ({ width, chatMessage }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="bg-white border-r border-gray-200 flex flex-col overflow-hidden" style={{ width }}>
      {/* File Explorer - 自动压缩 */}
      <div 
        className={`flex flex-col overflow-hidden border-b border-gray-100 transition-all duration-500 ease-out ${
          isExpanded ? 'flex-[1]' : 'flex-[2]'
        }`}
      >
        <FileTree />
      </div>
      
      {/* AI Chat Panel */}
      <div 
        className={`flex flex-col overflow-hidden transition-all duration-500 ease-out ${
          isExpanded ? 'flex-[1.3]' : 'flex-none'
        }`}
      >
        {isExpanded && (
          <>
            {/* 标题栏 */}
            <div 
              onClick={() => setIsExpanded(false)}
              className="px-3 py-2 flex items-center justify-between cursor-pointer
                         border-b border-gray-100 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Sparkles size={14} className="text-indigo-500" />
                <span className="text-[10px] font-bold text-gray-400 tracking-wider uppercase">
                  小思 AI
                </span>
              </div>
              <ChevronDown size={14} className="text-gray-400 hover:text-gray-600" />
            </div>
            
            {/* 聊天区域 */}
            <div className="flex-1 overflow-hidden p-2 animate-fadeIn">
              <AIChat externalMessage={chatMessage} />
            </div>
          </>
        )}
      </div>

      {/* 收起状态：底部按钮 - 素雅但扎眼 */}
      {!isExpanded && (
        <div className="px-2 pb-2">
          <button
            onClick={() => setIsExpanded(true)}
            className="w-full px-3 py-2.5 
                       bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50
                       border border-indigo-200/60 rounded-lg
                       flex items-center justify-center gap-2
                       hover:from-indigo-100 hover:via-purple-100 hover:to-pink-100
                       hover:border-indigo-300/80 hover:shadow-sm
                       active:scale-[0.98]
                       transition-all duration-200"
          >
            <Sparkles size={14} className="text-indigo-500" />
            <span className="text-xs font-semibold text-indigo-600/80 tracking-wide">
              问问小思 AI
            </span>
          </button>
        </div>
      )}
    </div>
  )
}
