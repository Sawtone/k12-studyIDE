import { useState } from 'react'
import { Sparkles, ChevronLeft, ChevronRight, X, FolderOpen } from 'lucide-react'
import { FileTree } from '../features/FileTree/FileTree'
import { AIChat } from '../features/AIChat/AIChat'

export const LeftPanel = ({ width, onSessionSelect, activeSessionId, editorContent }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(false)

  return (
    <div className="flex h-full">
      {/* 垂直工具栏 - 折叠时显示 */}
      <div
        className={`bg-slate-50 border-r border-gray-200 flex flex-col items-center py-2 gap-1 transition-all duration-300 ${
          isCollapsed ? 'w-11' : 'w-0 overflow-hidden'
        }`}
      >
        {/* 展开按钮 */}
        <button
          onClick={() => setIsCollapsed(false)}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 
                   hover:bg-gray-200 hover:text-gray-600 transition-all mb-2"
          title="展开面板"
        >
          <ChevronRight size={16} />
        </button>

        {/* 会话图标 */}
        <button
          onClick={() => setIsCollapsed(false)}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-indigo-500 
                   bg-indigo-100 hover:bg-indigo-200 transition-all"
          title="会话列表"
        >
          <FolderOpen size={16} />
        </button>

        {/* AI 助手图标 */}
        <button
          onClick={() => {
            setIsCollapsed(false)
            setTimeout(() => setIsExpanded(true), 300)
          }}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-purple-500 
                   bg-purple-100 hover:bg-purple-200 transition-all"
          title="AI 助手"
        >
          <Sparkles size={16} />
        </button>

        <div className="flex-1" />

        {/* 底部装饰 */}
        <div className="w-6 h-px bg-gray-200 mb-2" />
        <div className="flex flex-col gap-1">
          <div className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
          <div className="w-1.5 h-1.5 rounded-full bg-gray-200" />
        </div>
      </div>

      {/* 主内容面板 */}
      <div
        className={`bg-white border-r border-gray-200 flex flex-col overflow-hidden relative transition-all duration-300 ease-out ${
          isCollapsed ? 'w-0 opacity-0' : 'opacity-100'
        }`}
        style={{ width: isCollapsed ? 0 : width }}
      >
        {/* File Explorer */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <FileTree
            onSessionSelect={onSessionSelect}
            activeSessionId={activeSessionId}
            onCollapse={() => setIsCollapsed(true)}
          />
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
            <span className="text-xs font-semibold text-indigo-600/80 tracking-wide">问问小思 AI</span>
          </button>
        </div>

        {/* 浮动聊天窗口 */}
        {isExpanded && (
          <>
            {/* 遮罩 */}
            <div className="fixed inset-0 bg-black/5 z-40" onClick={() => setIsExpanded(false)} />

            {/* 聊天面板 */}
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
                  <div
                    className="w-6 h-6 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 
                                flex items-center justify-center"
                  >
                    <Sparkles size={12} className="text-white" />
                  </div>
                  <span className="text-sm font-semibold text-gray-700">小思 AI</span>
                </div>
                <button onClick={() => setIsExpanded(false)} className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
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
    </div>
  )
}
