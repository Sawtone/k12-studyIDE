import { useState } from 'react'
import { Sparkles, PenLine, Lightbulb, BookOpen, Rocket, Wand2, Loader2 } from 'lucide-react'
import { motion } from 'framer-motion'
import { sendChatMessage } from '../../api/chatApi'

// 写作主题
const topics = [
  { icon: '🌟', title: '我的梦想', prompt: '请给我一个关于"我的梦想"的写作开头，要有画面感，适合中学生，大约50-80字' },
  { icon: '🏠', title: '我的家', prompt: '请给我一个关于"我的家"或"家乡"的写作开头，温馨感人，适合中学生，大约50-80字' },
  { icon: '📚', title: '一本好书', prompt: '请给我一个关于"一本影响我的书"的写作开头，要引人入胜，适合中学生，大约50-80字' },
  { icon: '🎯', title: '一次挑战', prompt: '请给我一个关于"克服困难"或"一次挑战"的写作开头，要有悬念，适合中学生，大约50-80字' },
  { icon: '🌈', title: '美好时光', prompt: '请给我一个关于"美好的一天"或"难忘的时光"的写作开头，要有情感，适合中学生，大约50-80字' },
  { icon: '💡', title: '我的发现', prompt: '请给我一个关于"一个有趣的发现"或"我的思考"的写作开头，要有启发性，适合中学生，大约50-80字' },
]

// 主题卡片
const TopicCard = ({ topic, onClick, loading, delay }) => (
  <motion.button
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay }}
    onClick={() => onClick(topic)}
    disabled={loading}
    className="group p-3 bg-white rounded-xl border border-gray-100 hover:border-indigo-200 hover:shadow-md transition-all duration-200 text-left w-full disabled:opacity-60"
  >
    <div className="flex items-center gap-3">
      <span className="text-2xl">{topic.icon}</span>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-gray-700 group-hover:text-indigo-600 transition-colors">
          {topic.title}
        </div>
        <div className="text-[10px] text-gray-400 mt-0.5 flex items-center gap-1">
          <Wand2 size={9} />
          AI 生成写作灵感
        </div>
      </div>
      <Sparkles size={14} className="text-gray-300 group-hover:text-indigo-400 transition-colors" />
    </div>
  </motion.button>
)

export const WelcomeScreen = ({ sessionId, onStartWriting }) => {
  const [loading, setLoading] = useState(false)
  const [loadingTopic, setLoadingTopic] = useState(null)
  const [hoveredTip, setHoveredTip] = useState(null)

  const tips = [
    { icon: Wand2, text: '选择主题获取 AI 灵感' },
    { icon: Lightbulb, text: '右侧可以检查语法和润色' },
    { icon: BookOpen, text: '写完后可以分析文章结构' },
  ]

  // 选择主题并生成灵感
  const handleSelectTopic = async (topic) => {
    if (!sessionId) {
      // 没有 sessionId 直接进入编辑器
      onStartWriting({ topic, inspiration: null })
      return
    }

    setLoading(true)
    setLoadingTopic(topic)

    try {
      const result = await sendChatMessage({
        session_id: sessionId,
        message: topic.prompt,
      })
      onStartWriting({
        topic,
        inspiration: {
          content: result.content,
          actionItems: result.action_items || [],
        },
      })
    } catch (err) {
      console.error('生成灵感失败:', err)
      // 即使失败也进入编辑器
      onStartWriting({ topic, inspiration: null })
    } finally {
      setLoading(false)
      setLoadingTopic(null)
    }
  }

  // 自由写作
  const handleFreeWrite = () => {
    onStartWriting({ topic: null, inspiration: null })
  }

  return (
    <div
      className="h-full overflow-auto"
      style={{
        backgroundColor: '#fdfbf7',
        backgroundImage: 'radial-gradient(circle, #e5e7eb 1px, transparent 1px)',
        backgroundSize: '24px 24px',
      }}
    >
      <div className="max-w-2xl mx-auto py-8 px-8">
        {/* 欢迎区域 */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-6"
        >
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-100 to-purple-100 mb-3">
            <Sparkles className="w-7 h-7 text-indigo-500" />
          </div>
          <h2 className="text-lg font-semibold text-gray-800 mb-1">准备好开始写作了吗？</h2>
          <p className="text-sm text-gray-500">选择一个主题，AI 会为你生成写作灵感</p>
        </motion.div>

        {/* 加载提示 */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-4 p-3 bg-indigo-50 rounded-xl border border-indigo-100 flex items-center gap-3"
          >
            <Loader2 size={16} className="animate-spin text-indigo-500" />
            <div>
              <div className="text-sm font-medium text-indigo-700">
                {loadingTopic?.icon} 正在为「{loadingTopic?.title}」生成灵感...
              </div>
              <div className="text-xs text-indigo-500">马上就好，请稍候</div>
            </div>
          </motion.div>
        )}

        {/* 主题卡片网格 */}
        <div className="grid grid-cols-2 gap-3 mb-6">
          {topics.map((topic, i) => (
            <TopicCard
              key={topic.title}
              topic={topic}
              onClick={handleSelectTopic}
              loading={loading}
              delay={0.1 + i * 0.05}
            />
          ))}
        </div>

        {/* 自由写作按钮 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-center"
        >
          <div className="relative inline-block">
            <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl blur-lg opacity-30" />
            <button
              onClick={handleFreeWrite}
              disabled={loading}
              className="relative inline-flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-medium rounded-xl hover:from-indigo-600 hover:to-purple-600 transition-all duration-200 disabled:opacity-60"
            >
              <Rocket size={16} />
              自由写作
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2">跳过灵感，直接开始创作</p>
        </motion.div>

        {/* 使用提示 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-8 pt-6 border-t border-gray-100"
        >
          <div className="flex justify-center gap-6">
            {tips.map((tip, i) => {
              const Icon = tip.icon
              return (
                <div
                  key={i}
                  className="flex items-center gap-1.5 text-xs text-gray-400 cursor-default"
                  onMouseEnter={() => setHoveredTip(i)}
                  onMouseLeave={() => setHoveredTip(null)}
                >
                  <Icon
                    size={12}
                    className={`transition-colors ${hoveredTip === i ? 'text-indigo-400' : ''}`}
                  />
                  <span className={`transition-colors ${hoveredTip === i ? 'text-gray-600' : ''}`}>
                    {tip.text}
                  </span>
                </div>
              )
            })}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
