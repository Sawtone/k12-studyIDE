import { useState, useMemo } from 'react'
import {
  GitBranch,
  Lightbulb,
  SpellCheck,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  FileText,
  Clock,
  Type,
  Quote
} from 'lucide-react'
import { StructureTree } from '../features/StructureTree/StructureTree'
import { HealthCheck } from '../features/HealthCheck/HealthCheck'
import { GrammarCheck } from '../features/GrammarCheck/GrammarCheck'
import { TextPolish } from '../features/TextPolish/TextPolish'

const tools = [
  { id: 'structure', label: '结构', icon: GitBranch, color: 'indigo' },
  { id: 'health', label: '健康度', icon: Lightbulb, color: 'amber' },
  { id: 'grammar', label: '语法', icon: SpellCheck, color: 'emerald' },
  { id: 'polish', label: '润色', icon: Sparkles, color: 'violet' }
]

const colorMap = {
  indigo: {
    active: 'bg-indigo-500 text-white shadow-lg shadow-indigo-200',
    hover: 'hover:bg-indigo-50 hover:text-indigo-600',
    text: 'text-indigo-500',
    dot: 'bg-indigo-500'
  },
  amber: {
    active: 'bg-amber-500 text-white shadow-lg shadow-amber-200',
    hover: 'hover:bg-amber-50 hover:text-amber-600',
    text: 'text-amber-500',
    dot: 'bg-amber-500'
  },
  emerald: {
    active: 'bg-emerald-500 text-white shadow-lg shadow-emerald-200',
    hover: 'hover:bg-emerald-50 hover:text-emerald-600',
    text: 'text-emerald-500',
    dot: 'bg-emerald-500'
  },
  violet: {
    active: 'bg-violet-500 text-white shadow-lg shadow-violet-200',
    hover: 'hover:bg-violet-50 hover:text-violet-600',
    text: 'text-violet-500',
    dot: 'bg-violet-500'
  }
}

// 写作小贴士
const writingTips = [
  '好文章是改出来的，多读几遍自己的作品',
  '开头要抓人，结尾要有力',
  '少用"的"字，句子更简洁',
  '具体的细节比抽象的描述更动人',
  '写完后大声朗读，不通顺的地方一听就知道',
  '每段只说一个主要意思',
  '用短句增强节奏感',
  '删掉不必要的词，精简是美德'
]

// 写作统计卡片
const WritingStats = ({ content }) => {
  const stats = useMemo(() => {
    if (!content || !content.trim()) {
      return { chars: 0, words: 0, paragraphs: 0, readTime: 0 }
    }
    const text = content.trim()
    const chars = text.replace(/\s/g, '').length
    // 中文按字数，英文按词数
    const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length
    const englishWords = (text.match(/[a-zA-Z]+/g) || []).length
    const words = chineseChars + englishWords
    const paragraphs = text.split(/\n\s*\n/).filter((p) => p.trim()).length || 1
    const readTime = Math.max(1, Math.ceil(words / 300))
    return { chars, words, paragraphs, readTime }
  }, [content])

  const tipIndex = useMemo(() => Math.floor(Math.random() * writingTips.length), [])

  return (
    <div className="border-t border-gray-100 bg-gray-50/50">
      {/* 统计数据 */}
      <div className="px-3 py-2.5 grid grid-cols-4 gap-1">
        <StatItem icon={Type} label="字符" value={stats.chars} color="text-blue-500" />
        <StatItem icon={FileText} label="字数" value={stats.words} color="text-emerald-500" />
        <StatItem icon={Quote} label="段落" value={stats.paragraphs} color="text-amber-500" />
        <StatItem icon={Clock} label="分钟" value={stats.readTime} color="text-violet-500" />
      </div>

      {/* 写作小贴士 */}
      <div className="px-3 pb-3">
        <div className="p-2.5 bg-gradient-to-br from-slate-50 to-gray-50 rounded-lg border border-gray-100">
          <div className="flex items-start gap-2">
            <span className="text-base">💡</span>
            <p className="text-[11px] text-gray-500 leading-relaxed">{writingTips[tipIndex]}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

const StatItem = ({ icon: Icon, label, value, color }) => (
  <div className="flex flex-col items-center py-1">
    <Icon size={12} className={`${color} mb-1`} />
    <span className="text-sm font-semibold text-gray-700">{value}</span>
    <span className="text-[9px] text-gray-400">{label}</span>
  </div>
)

export const RightPanel = ({ width, sessionId, content }) => {
  const [activeTab, setActiveTab] = useState('structure')
  const [isCollapsed, setIsCollapsed] = useState(false)

  const activeTool = tools.find((t) => t.id === activeTab)
  const activeColors = colorMap[activeTool?.color || 'indigo']

  const handleTabClick = (tabId) => {
    if (activeTab === tabId && !isCollapsed) {
      setIsCollapsed(true)
    } else {
      setActiveTab(tabId)
      setIsCollapsed(false)
    }
  }

  return (
    <div className="flex h-full">
      {/* 内容面板 */}
      <div
        className={`bg-gray-50/50 border-l border-gray-100 flex flex-col overflow-hidden transition-all duration-300 ease-out ${
          isCollapsed ? 'w-0 opacity-0' : 'opacity-100'
        }`}
        style={{ width: isCollapsed ? 0 : width - 44 }}
      >
        {/* 标题栏 - 显示当前工具名称 */}
        <div className="px-3 py-2.5 flex items-center justify-between bg-gray-50/50 border-b border-gray-100">
          <div className="flex items-center gap-2">
            {activeTool && <activeTool.icon size={14} className={activeColors.text} />}
            <span className="text-xs font-semibold text-gray-700">{activeTool?.label}</span>
          </div>
          <button
            onClick={() => setIsCollapsed(true)}
            className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
            title="收起面板"
          >
            <ChevronRight size={14} />
          </button>
        </div>

        {/* 内容区域 */}
        <div className="flex-1 overflow-hidden relative bg-gray-50/30">
          <div className={`absolute inset-0 overflow-auto p-3 ${activeTab === 'structure' ? '' : 'hidden'}`}>
            <StructureTree sessionId={sessionId} content={content} />
          </div>
          <div className={`absolute inset-0 overflow-auto p-3 ${activeTab === 'health' ? '' : 'hidden'}`}>
            <HealthCheck sessionId={sessionId} content={content} />
          </div>
          <div className={`absolute inset-0 overflow-auto p-3 ${activeTab === 'grammar' ? '' : 'hidden'}`}>
            <GrammarCheck sessionId={sessionId} content={content} />
          </div>
          <div className={`absolute inset-0 overflow-auto p-3 ${activeTab === 'polish' ? '' : 'hidden'}`}>
            <TextPolish sessionId={sessionId} content={content} />
          </div>
        </div>

        {/* 底部统计卡片 */}
        <WritingStats content={content} />
      </div>

      {/* 垂直工具栏 */}
      <div className="w-11 bg-slate-50/80 border-l border-gray-100 flex flex-col items-center py-2 gap-1">
        {/* 展开按钮（折叠时显示） */}
        {isCollapsed && (
          <button
            onClick={() => setIsCollapsed(false)}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 
                     hover:bg-gray-200 hover:text-gray-600 transition-all mb-2"
            title="展开面板"
          >
            <ChevronLeft size={16} />
          </button>
        )}

        {/* 工具按钮 */}
        {tools.map((tool) => {
          const Icon = tool.icon
          const isActive = activeTab === tool.id && !isCollapsed
          const toolColors = colorMap[tool.color]

          return (
            <button
              key={tool.id}
              onClick={() => handleTabClick(tool.id)}
              className={`relative w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-200 ${
                isActive ? toolColors.active : `text-gray-400 ${toolColors.hover}`
              }`}
              title={tool.label}
            >
              <Icon size={16} />
              {/* 选中指示点 */}
              {isActive && (
                <span className="absolute -left-1 top-1/2 -translate-y-1/2 w-1 h-4 bg-white rounded-r-full" />
              )}
            </button>
          )
        })}

        {/* 底部分隔 */}
        <div className="flex-1" />

        {/* 底部装饰 */}
        <div className="w-6 h-px bg-gray-200 mb-2" />
        <div className="flex flex-col gap-1">
          {tools.map((tool) => (
            <div
              key={tool.id}
              className={`w-1.5 h-1.5 rounded-full transition-all ${
                activeTab === tool.id && !isCollapsed ? colorMap[tool.color].dot : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
