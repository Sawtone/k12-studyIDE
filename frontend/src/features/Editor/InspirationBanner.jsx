import { useState } from 'react'
import { Sparkles, X, Copy, Check, ChevronDown, ChevronUp, RefreshCw, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { sendChatMessage } from '../../api/chatApi'

export const InspirationBanner = ({ topic, inspiration, sessionId, onClose, onUpdate }) => {
  const [expanded, setExpanded] = useState(true)
  const [copied, setCopied] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

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

  const handleRefresh = async () => {
    if (!sessionId || !topic) return
    setRefreshing(true)
    try {
      const result = await sendChatMessage({
        session_id: sessionId,
        message: topic.prompt,
      })
      onUpdate?.({
        content: result.content,
        actionItems: result.action_items || [],
      })
    } catch (err) {
      console.error('刷新失败:', err)
    } finally {
      setRefreshing(false)
    }
  }

  if (!topic || !inspiration) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="mx-auto max-w-3xl px-8 pt-4"
    >
      <div className="bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 rounded-xl border border-indigo-100 overflow-hidden shadow-sm">
        {/* Header */}
        <div className="px-4 py-2 flex items-center justify-between border-b border-indigo-100/50">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded-md bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
              <Sparkles size={10} className="text-white" />
            </div>
            <span className="text-xs font-medium text-gray-700">
              {topic.icon} {topic.title} · 写作灵感
            </span>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-1 rounded hover:bg-white/50 text-gray-400 hover:text-gray-600 transition-colors"
            >
              {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
            <button
              onClick={onClose}
              className="p-1 rounded hover:bg-white/50 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X size={12} />
            </button>
          </div>
        </div>

        {/* Content */}
        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <div className="px-4 py-3">
                <p className="text-sm text-gray-700 leading-relaxed mb-2">{inspiration.content}</p>

                {inspiration.actionItems?.length > 0 && (
                  <div className="p-2 bg-white/50 rounded-lg mb-2">
                    <div className="text-[10px] text-indigo-600 font-medium mb-1">💡 写作建议</div>
                    <ul className="text-[10px] text-gray-600 space-y-0.5">
                      {inspiration.actionItems.map((item, i) => (
                        <li key={i} className="flex items-start gap-1">
                          <span className="text-indigo-400">•</span>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="flex items-center gap-2">
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1 px-2.5 py-1 bg-white rounded-lg border border-gray-200 text-[10px] text-gray-600 hover:border-indigo-300 hover:text-indigo-600 transition-colors"
                  >
                    {copied ? <Check size={10} className="text-green-500" /> : <Copy size={10} />}
                    {copied ? '已复制' : '复制'}
                  </button>
                  <button
                    onClick={handleRefresh}
                    disabled={refreshing}
                    className="flex items-center gap-1 px-2.5 py-1 bg-white rounded-lg border border-gray-200 text-[10px] text-gray-600 hover:border-indigo-300 hover:text-indigo-600 transition-colors disabled:opacity-50"
                  >
                    {refreshing ? (
                      <Loader2 size={10} className="animate-spin" />
                    ) : (
                      <RefreshCw size={10} />
                    )}
                    换一个
                  </button>
                  <span className="text-[9px] text-gray-400 ml-auto">灵感仅供参考</span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}
