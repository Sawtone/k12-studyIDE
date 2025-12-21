import React, { useState, useCallback, useRef } from 'react'
import { motion } from 'framer-motion'
import {
  FileText, Bot, FolderOpen, File, ChevronRight, ChevronDown, Send,
  AlertCircle, CheckCircle, Lightbulb, PenTool, Code2, GitBranch,
  Clock, Save, Tag, Sparkles
} from 'lucide-react'

// 文件树组件
const FileTree = () => {
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

// AI聊天组件
const AIChat = () => {
  const [input, setInput] = useState('')
  const messages = [
    { role: 'ai', content: '👋 你好！我是写作助手，随时为你服务。' },
    { role: 'ai', content: '💡 第二段存在逻辑跳跃，需要帮你修复吗？' },
    { role: 'user', content: '好的，请帮我看看' },
    { role: 'ai', content: '✨ 建议添加过渡句说明为什么需要谨慎。' },
  ]

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] px-3 py-2 rounded-2xl text-sm ${
              msg.role === 'user'
                ? 'bg-indigo-500 text-white rounded-br-sm'
                : 'bg-gray-100 text-gray-700 rounded-bl-sm'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-3 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入问题..."
          className="flex-1 px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-300 transition-all"
        />
        <button className="p-2 bg-indigo-500 text-white rounded-xl hover:bg-indigo-600 transition-colors">
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}


// 滑动式模式切换
const ModeToggle = ({ isIDEMode, onToggle }) => {
  return (
    <div className="relative flex items-center bg-gray-100 p-1 rounded-full">
      {/* 滑动背景 */}
      <motion.div
        className="absolute h-8 bg-white rounded-full shadow-sm"
        layout
        transition={{ type: "spring", stiffness: 500, damping: 35 }}
        style={{
          width: 'calc(50% - 4px)',
          left: isIDEMode ? 'calc(50% + 2px)' : '4px',
        }}
      />
      
      <button
        onClick={() => onToggle(false)}
        className={`relative z-10 flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
          !isIDEMode ? 'text-indigo-600' : 'text-gray-500'
        }`}
      >
        <PenTool size={14} />
        写作
      </button>
      <button
        onClick={() => onToggle(true)}
        className={`relative z-10 flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
          isIDEMode ? 'text-indigo-600' : 'text-gray-500'
        }`}
      >
        <Code2 size={14} />
        IDE
      </button>
    </div>
  )
}

// 结构树组件
const StructureTree = () => {
  const nodes = [
    { label: '引言', status: 'ok', desc: '结构完整' },
    { label: '论点一', status: 'warning', desc: '缺少论据' },
    { label: '论点二', status: 'ok', desc: '逻辑清晰' },
    { label: '结论', status: 'ok', desc: '呼应主题' },
  ]

  return (
    <div className="relative">
      {/* 连接线 */}
      <div className="absolute left-[15px] top-6 bottom-6 w-0.5 bg-gray-200" />
      
      <div className="space-y-3">
        {nodes.map((node, i) => (
          <div key={i} className="flex items-start gap-3 relative">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 z-10 ${
              node.status === 'ok' ? 'bg-green-100' : 'bg-rose-100'
            }`}>
              {node.status === 'ok' 
                ? <CheckCircle size={16} className="text-green-600" />
                : <AlertCircle size={16} className="text-rose-500" />
              }
            </div>
            <div className={`flex-1 p-3 rounded-xl ${
              node.status === 'ok' ? 'bg-green-50 border border-green-100' : 'bg-rose-50 border border-rose-100'
            }`}>
              <div className={`font-medium text-sm ${
                node.status === 'ok' ? 'text-green-700' : 'text-rose-600'
              }`}>{node.label}</div>
              <div className={`text-xs mt-0.5 ${
                node.status === 'ok' ? 'text-green-600/70' : 'text-rose-500/70'
              }`}>{node.desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// 健康检查组件
const HealthCheck = () => {
  const metrics = [
    { label: '词汇丰富度', value: 72, color: 'bg-indigo-500' },
    { label: '逻辑连贯性', value: 58, color: 'bg-orange-400' },
    { label: '论证强度', value: 85, color: 'bg-green-500' },
  ]

  return (
    <div className="space-y-4">
      {metrics.map((m, i) => (
        <div key={i}>
          <div className="flex justify-between text-sm mb-1.5">
            <span className="text-gray-600">{m.label}</span>
            <span className="font-medium text-gray-700">{m.value}%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${m.value}%` }}
              transition={{ duration: 0.8, delay: i * 0.15 }}
              className={`h-full ${m.color} rounded-full`}
            />
          </div>
        </div>
      ))}
    </div>
  )
}


// 编辑器组件
const Editor = ({ isIDEMode, content, setContent }) => {
  const sentences = content.split(/(?<=[。！？])/g).filter(s => s.trim())

  const handleIDEChange = (index, newValue) => {
    const newSentences = [...sentences]
    newSentences[index] = newValue
    setContent(newSentences.join(''))
  }

  // 写作模式 - 纸张纹理背景
  if (!isIDEMode) {
    return (
      <div 
        className="h-full p-8"
        style={{
          backgroundColor: '#fdfbf7',
          backgroundImage: 'radial-gradient(#e5e7eb 1px, transparent 1px)',
          backgroundSize: '20px 20px',
        }}
      >
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full h-full font-serif text-lg text-gray-700 bg-transparent resize-none focus:outline-none leading-relaxed"
          placeholder="开始写作..."
          style={{ lineHeight: '2.2' }}
        />
      </div>
    )
  }

  // IDE模式
  return (
    <div className="h-full bg-gray-50 overflow-auto p-4">
      <div className="space-y-1">
        {sentences.map((sentence, i) => (
          <div key={i} className="flex items-start group">
            {/* 行号 */}
            <div className="w-10 flex-shrink-0 text-right pr-3 text-gray-400 text-sm font-mono select-none pt-2">
              {i + 1}
            </div>
            
            {/* 代码行 */}
            <div className="flex-1 flex items-center gap-2 py-1.5 px-3 rounded-lg hover:bg-white border border-transparent hover:border-gray-200 transition-all">
              {/* 标签 */}
              {i === 0 && (
                <span className="flex-shrink-0 px-2 py-0.5 bg-green-50 text-green-700 text-xs font-medium rounded border border-green-200">
                  主题句
                </span>
              )}
              {i === 1 && (
                <span className="flex-shrink-0 px-2 py-0.5 bg-orange-50 text-orange-700 text-xs font-medium rounded border border-orange-200">
                  论据
                </span>
              )}
              {i === 2 && (
                <span className="flex-shrink-0 px-2 py-0.5 bg-rose-50 text-rose-600 text-xs font-medium rounded border border-rose-200">
                  ⚠️ 过渡
                </span>
              )}
              
              <input
                type="text"
                value={sentence}
                onChange={(e) => handleIDEChange(i, e.target.value)}
                className="flex-1 font-mono text-sm text-gray-700 bg-transparent focus:outline-none"
              />
            </div>
          </div>
        ))}
        
        <div className="flex items-center text-gray-300 text-sm font-mono">
          <div className="w-10 text-right pr-3">{sentences.length + 1}</div>
          <span className="italic pl-3">继续写作...</span>
        </div>
      </div>
    </div>
  )
}

// 可拖拽分隔条
const ResizeHandle = ({ onMouseDown }) => {
  return (
    <div
      onMouseDown={onMouseDown}
      className="w-1 flex-shrink-0 cursor-col-resize hover:bg-indigo-200 active:bg-indigo-300 transition-colors group flex items-center justify-center"
    >
      <div className="w-0.5 h-12 bg-gray-300 group-hover:bg-indigo-400 rounded-full transition-colors" />
    </div>
  )
}


// 主应用组件
function App() {
  const [isIDEMode, setIsIDEMode] = useState(false)
  const [content, setContent] = useState(
    '人工智能正在改变世界。它帮助我们更快地学习新知识。然而，我们必须谨慎对待它的发展。'
  )
  const [leftWidth, setLeftWidth] = useState(240)
  const [rightWidth, setRightWidth] = useState(280)
  const containerRef = useRef(null)
  const draggingRef = useRef(null)

  const handleMouseDown = useCallback((side) => (e) => {
    e.preventDefault()
    draggingRef.current = side
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }, [])

  const handleMouseMove = useCallback((e) => {
    if (!draggingRef.current || !containerRef.current) return
    
    const rect = containerRef.current.getBoundingClientRect()
    
    if (draggingRef.current === 'left') {
      const newWidth = Math.max(180, Math.min(400, e.clientX - rect.left))
      setLeftWidth(newWidth)
    } else if (draggingRef.current === 'right') {
      const newWidth = Math.max(200, Math.min(400, rect.right - e.clientX))
      setRightWidth(newWidth)
    }
  }, [])

  const handleMouseUp = useCallback(() => {
    draggingRef.current = null
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }, [])

  React.useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [handleMouseMove, handleMouseUp])

  const wordCount = content.length
  const sentenceCount = content.split(/(?<=[。！？])/g).filter(s => s.trim()).length
  const readingTime = Math.max(1, Math.ceil(wordCount / 300))

  return (
    <div ref={containerRef} className="h-screen bg-gray-50 flex flex-col overflow-hidden">
      {/* 顶部全局上下文栏 */}
      <header className="h-12 bg-white border-b border-gray-200 flex items-center justify-between px-4 flex-shrink-0">
        {/* 左侧：Logo + 面包屑 */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center">
              <Sparkles size={14} className="text-white" />
            </div>
            <span className="font-semibold text-gray-800">认知IDE</span>
          </div>
          
          <div className="h-4 w-px bg-gray-200" />
          
          {/* 面包屑 */}
          <div className="flex items-center gap-1.5 text-sm text-gray-500">
            <span className="hover:text-gray-700 cursor-pointer">我的项目</span>
            <ChevronRight size={14} />
            <span className="hover:text-gray-700 cursor-pointer">作文集</span>
            <ChevronRight size={14} />
            <span className="text-gray-700 font-medium">AI伦理.md</span>
          </div>
          
          {/* 标签 */}
          <span className="px-2 py-0.5 bg-blue-50 text-blue-600 text-xs font-medium rounded-full flex items-center gap-1">
            <Tag size={10} />
            语文
          </span>
        </div>
        
        {/* 右侧：元数据 */}
        <div className="flex items-center gap-4 text-sm text-gray-500">
          <div className="flex items-center gap-1.5">
            <FileText size={14} />
            <span>{wordCount} 字</span>
          </div>
          <div className="h-3 w-px bg-gray-200" />
          <div className="flex items-center gap-1.5">
            <Clock size={14} />
            <span>约 {readingTime} 分钟</span>
          </div>
          <div className="h-3 w-px bg-gray-200" />
          <div className="flex items-center gap-1.5 text-green-600">
            <Save size={14} />
            <span>已自动保存</span>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 左侧面板 */}
        <div className="bg-white border-r border-gray-200 flex flex-col overflow-hidden" style={{ width: leftWidth }}>
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

        <ResizeHandle onMouseDown={handleMouseDown('left')} />

        {/* 中间编辑器面板 */}
        <div className="flex-1 flex flex-col overflow-hidden bg-white mx-0.5 rounded-t-xl shadow-sm border border-gray-200 border-b-0 mt-2">
          {/* 编辑器工具栏 */}
          <div className="h-12 border-b border-gray-100 flex items-center justify-between px-4 bg-gray-50/50 rounded-t-xl">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <FileText size={16} className="text-indigo-500" />
              <span className="font-medium">AI伦理.md</span>
              <span className="text-gray-400">·</span>
              <span className="text-gray-400">{sentenceCount} 句</span>
            </div>
            
            <ModeToggle isIDEMode={isIDEMode} onToggle={setIsIDEMode} />
          </div>
          
          {/* 编辑器内容 */}
          <div className="flex-1 overflow-hidden">
            <Editor isIDEMode={isIDEMode} content={content} setContent={setContent} />
          </div>
        </div>

        <ResizeHandle onMouseDown={handleMouseDown('right')} />

        {/* 右侧面板 */}
        <div className="bg-white border-l border-gray-200 flex flex-col overflow-hidden" style={{ width: rightWidth }}>
          <div className="flex-1 p-4 border-b border-gray-100 overflow-auto">
            <div className="flex items-center gap-2 mb-4 text-gray-700">
              <GitBranch size={16} className="text-indigo-500" />
              <span className="font-semibold text-sm">结构分析</span>
            </div>
            <StructureTree />
          </div>
          
          <div className="flex-1 p-4 overflow-auto">
            <div className="flex items-center gap-2 mb-4 text-gray-700">
              <Lightbulb size={16} className="text-indigo-500" />
              <span className="font-semibold text-sm">写作健康度</span>
            </div>
            <HealthCheck />
            
            {/* 建议卡片 */}
            <div className="mt-5 p-3 bg-orange-50 rounded-xl border border-orange-100">
              <div className="flex items-start gap-2">
                <AlertCircle size={16} className="text-orange-500 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-orange-700 text-sm">改进建议</div>
                  <div className="text-xs text-orange-600/80 mt-1 leading-relaxed">
                    第二句和第三句之间缺少逻辑过渡，建议添加连接词。
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
