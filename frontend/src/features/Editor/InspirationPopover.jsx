import { useState, useRef, useEffect } from 'react'
import { Sparkles, X, Loader2, RefreshCw, Copy, Check, Send, ArrowLeft } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { sendChatMessage } from '../../api/chatApi'

// 预设主题 - 更紧凑
const presetTopics = [
  { icon: '🌟', label: '梦想', prompt: '请给我一个关于"我的梦想"的写作开头，要有画面感，适合中学生，大约50-80字' },
  { icon: '🏠', label: '家乡', prompt: '请给我一个关于"我的家"或"家乡"的写作开头，温馨感人，适合中学生，大约50-80字' },
  { icon: '📚', label: '读书', prompt: '请给我一个关于"一本影响我的书"的写作开头，要引人入胜，适合中学生，大约50-80字' },
  { icon: '🎯', label: '挑战', prompt: '请给我一个关于"克服困难"或"一次挑战"的写作开头，要有悬念，适合中学生，大约50-80字' },
  { icon: '🌈', label: '时光', prompt: '请给我一个关于"美好的一天"或"难忘的时光"的写作开头，要有情感，适合中学生，大约50-80字' },
  { icon: '💡', label: '发现', prompt: '请给我一个关于"一个有趣的发现"或"我的思考"的写作开头，要有启发性，适合中学生，大约50-80字' },
]

// 灵感触发按钮
export const InspirationButton = ({ onClick, disabled }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className="flex items-center gap-1.5 px-2.5 py-1.5 bg-gradient-to-r from-indigo-50 to-purple-50 hover:from-indigo-100 hover:to-purple-100 border border-indigo-200/50 rounded-lg text-xs font-medium text-indigo-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
  >
    <Sparkles size={12} />
    <span>写作灵感</span>
  </button>
)

// 灵感弹出面板
export const InspirationPopover = ({ isOpen, onClose, sessionId, anchorRef }) => {
  const [customInput, setCustomInput] = useState('')
  const [activeTopic, setActiveTopic] = useState(null) // { label, prompt }
  const [loading, setLoading] = useState(false)
  const [inspiration, setInspiration] = useState(null)
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(false)
  const panelRef = useRef(null)
  const inputRef = useRef(null)

  // 点击外部关闭
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        panelRef.current &&
        !panelRef.current.contains(e.target) &&
        anchorRef?.current &&
        !anchorRef.current.contains(e.target)
      ) {
        onClose()
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen, onClose, anchorRef])

  // 关闭时重置状态
  useEffect(() => {
    if (!isOpen) {
      setActiveTopic(null)
      setInspiration(null)
      setError(null)
      setCustomInput('')
    }
  }, [isOpen])

  const generateInspiration = async (topic) => {
    if (!sessionId) return

    setActiveTopic(topic)
    setLoading(true)
    setError(null)
    setInspiration(null)

    try {
      const result = await sendChatMessage({
        session_id: sessionId,
        message: topic.prompt,
      })
      setInspiration({
        content: result.content,
        actionItems: result.action_items || [],
      })
    } catch (err) {
      setError('生成失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  const handleCustomSubmit = () => {
    if (!customInput.trim()) return
    const topic = {
      label: '自定义',
      prompt: `请给我一个关于"${customInput.trim()}"的写作开头，要有画面感和情感，适合中学生，大约50-80字`,
    }
    generateInspiration(topic)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleCustomSubmit()
    }
  }

  const handleCopy = async () => {
    if (!inspiration?.content) return
    try {
      await navigator.clipboard.writeText(inspiration.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('复制失败:', err)
    }
  }

  const handleBack = () => {
    setActiveTopic(null)
    setInspiration(null)
    setError(null)
  }

  if (!isOpen) return null

  // 结果视图
  const ResultView = () => (
    <div className="p-3">
      {/* 返回按钮 */}
      <button
        onClick={handleBack}
        className="flex items-center gap-1 text-xs text-gray-500 hover:text-indigo-600 mb-2"
      >
        <ArrowLeft size={12} />
        <span>返回</span>
      </button>

      {loading ? (
        <div className="py-6 text-center">
          <Loader2 size={20} className="animate-spin text-indigo-400 mx-auto mb-2" />
          <p className="text-xs text-gray-500">AI 正在构思...</p>
        </div>
      ) : error ? (
        <div className="py-4 text-center">
          <p className="text-xs text-red-500 mb-2">{error}</p>
          <button
            onClick={() => generateInspiration(activeTopic)}
            className="text-xs text-indigo-600 hover:underline"
          >
            重试
          </button>
        </div>
      ) : inspiration ? (
        <>
          <p className="text-sm text-gray-700 leading-relaxed mb-3">{inspiration.content}</p>

          {inspiration.actionItems?.length > 0 && (
            <div className="p-2 bg-amber-50 rounded-lg mb-3 border border-amber-100">
              <div className="text-[10px] text-amber-700 font-medium mb-1">💡 建议</div>
              <ul className="text-[11px] text-gray-600 space-y-0.5">
                {inspiration.actionItems.slice(0, 3).map((item, i) => (
                  <li key={i} className="flex items-start gap-1">
                    <span className="text-amber-500">•</span>
                    <span className="line-clamp-1">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="flex-1 flex items-center justify-center gap-1 py-1.5 bg-indigo-500 text-white text-xs rounded-lg hover:bg-indigo-600 transition-colors"
            >
              {copied ? <Check size={12} /> : <Copy size={12} />}
              <span>{copied ? '已复制' : '复制'}</span>
            </button>
            <button
              onClick={() => generateInspiration(activeTopic)}
              className="p-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-500"
              title="换一个"
            >
              <RefreshCw size={14} />
            </button>
          </div>
        </>
      ) : null}
    </div>
  )

  // 选择视图
  const SelectView = () => (
    <div className="p-3">
      {/* 自定义输入 */}
      <div className="relative mb-3">
        <input
          ref={inputRef}
          type="text"
          value={customInput}
          onChange={(e) => setCustomInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入你想写的主题..."
          className="w-full pl-3 pr-8 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-indigo-300 focus:bg-white transition-colors"
          maxLength={20}
        />
        <button
          onClick={handleCustomSubmit}
          disabled={!customInput.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-indigo-500 disabled:opacity-30 disabled:hover:text-gray-400"
        >
          <Send size={14} />
        </button>
      </div>

      {/* 分隔线 */}
      <div className="flex items-center gap-2 mb-2">
        <div className="flex-1 h-px bg-gray-100" />
        <span className="text-[10px] text-gray-400">或选择主题</span>
        <div className="flex-1 h-px bg-gray-100" />
      </div>

      {/* 预设主题网格 */}
      <div className="grid grid-cols-3 gap-1.5">
        {presetTopics.map((topic) => (
          <button
            key={topic.label}
            onClick={() => generateInspiration(topic)}
            className="flex flex-col items-center gap-1 p-2 rounded-lg hover:bg-indigo-50 transition-colors group"
          >
            <span className="text-lg">{topic.icon}</span>
            <span className="text-[11px] text-gray-600 group-hover:text-indigo-600">
              {topic.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  )

  return (
    <AnimatePresence>
      <motion.div
        ref={panelRef}
        initial={{ opacity: 0, y: -8, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -8, scale: 0.96 }}
        transition={{ duration: 0.15 }}
        className="absolute right-0 top-full mt-2 w-72 bg-white rounded-xl shadow-lg border border-gray-200 z-50 overflow-hidden"
      >
        {/* Header - 更紧凑 */}
        <div className="px-3 py-2 bg-gradient-to-r from-indigo-50/80 to-purple-50/80 border-b border-gray-100 flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Sparkles size={12} className="text-indigo-500" />
            <span className="text-xs font-medium text-gray-700">写作灵感</span>
          </div>
          <button onClick={onClose} className="p-0.5 hover:bg-white/60 rounded text-gray-400">
            <X size={12} />
          </button>
        </div>

        {/* Content */}
        {activeTopic ? <ResultView /> : <SelectView />}
      </motion.div>
    </AnimatePresence>
  )
}
