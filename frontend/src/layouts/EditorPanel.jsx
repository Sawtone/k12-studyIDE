import { useState, useRef } from 'react'
import { FileText, FileCode, Plus, Sparkles } from 'lucide-react'
import { ModeToggle } from '../components/ModeToggle'
import { Editor } from '../features/Editor/Editor'
import { InspirationButton, InspirationPopover } from '../features/Editor/InspirationPopover'
import { motion } from 'framer-motion'

// 无会话时的引导状态
const NoSessionState = () => (
  <div
    className="h-full overflow-auto flex items-center justify-center"
    style={{
      backgroundColor: '#fdfbf7',
      backgroundImage: 'radial-gradient(circle, #e5e7eb 1px, transparent 1px)',
      backgroundSize: '24px 24px',
    }}
  >
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="text-center max-w-md px-8"
    >
      <div className="relative inline-block mb-6">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center">
          <FileText size={36} className="text-indigo-400" />
        </div>
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3, type: 'spring' }}
          className="absolute -right-2 -bottom-2 w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 to-orange-400 flex items-center justify-center shadow-lg"
        >
          <Sparkles size={16} className="text-white" />
        </motion.div>
      </div>

      <h2 className="text-xl font-semibold text-gray-800 mb-2">开始你的写作之旅</h2>
      <p className="text-sm text-gray-500 mb-6 leading-relaxed">
        从左侧面板创建一个新会话，<br />
        或选择已有的会话继续写作
      </p>

      <div className="flex items-center justify-center gap-3 text-xs text-gray-400">
        <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white rounded-full border border-gray-100">
          <div className="w-5 h-5 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-medium text-[10px]">
            1
          </div>
          <span>点击左侧</span>
          <Plus size={12} className="text-indigo-500" />
        </div>
        <span className="text-gray-300">→</span>
        <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white rounded-full border border-gray-100">
          <div className="w-5 h-5 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-medium text-[10px]">
            2
          </div>
          <span>开始写作</span>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="mt-8 p-4 bg-white/80 rounded-xl border border-indigo-100"
      >
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center flex-shrink-0">
            <Sparkles size={14} className="text-white" />
          </div>
          <div className="text-left">
            <div className="text-xs font-medium text-gray-700">AI 写作助手</div>
            <div className="text-[11px] text-gray-500 mt-0.5">
              写作过程中，点击"写作灵感"获取 AI 建议
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  </div>
)

export const EditorPanel = ({
  isIDEMode,
  onModeToggle,
  content,
  setContent,
  sentenceCount,
  sessionId,
  sessionTitle,
  inspiration,
  setInspiration,
}) => {
  const [showInspiration, setShowInspiration] = useState(false)
  const inspirationBtnRef = useRef(null)

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-white mx-0.5 rounded-t-xl shadow-sm border border-gray-200 border-b-0 mt-2">
      {/* Header */}
      <div className="h-12 border-b border-gray-100 flex items-center justify-between px-4 bg-gray-50/50 rounded-t-xl">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          {isIDEMode ? (
            <FileCode size={16} className="text-amber-500" />
          ) : (
            <FileText size={16} className="text-indigo-500" />
          )}
          <span className="font-medium truncate max-w-[200px]">
            {sessionTitle || '未选择会话'}
          </span>
          {sessionId && (
            <>
              <span className="text-gray-400">·</span>
              <span className="text-gray-400">{sentenceCount} 句</span>
            </>
          )}
        </div>

        <div className="flex items-center gap-2 relative">
          {/* 写作灵感按钮 - 仅在文学模式且有会话时显示 */}
          {!isIDEMode && sessionId && (
            <div ref={inspirationBtnRef}>
              <InspirationButton
                onClick={() => setShowInspiration(!showInspiration)}
                disabled={!sessionId}
              />
            </div>
          )}

          <ModeToggle isIDEMode={isIDEMode} onToggle={onModeToggle} />

          {/* 灵感弹出面板 */}
          <InspirationPopover
            isOpen={showInspiration}
            onClose={() => setShowInspiration(false)}
            sessionId={sessionId}
            anchorRef={inspirationBtnRef}
          />
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-hidden">
        {sessionId ? (
          <Editor
            isIDEMode={isIDEMode}
            content={content}
            setContent={setContent}
            sessionId={sessionId}
            inspiration={inspiration}
            setInspiration={setInspiration}
          />
        ) : (
          <NoSessionState />
        )}
      </div>
    </div>
  )
}
