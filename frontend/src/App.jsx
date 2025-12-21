import React, { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText, Bot, Sparkles, GitBranch, FolderOpen, File,
  ChevronRight, ChevronDown, Send, AlertCircle, CheckCircle,
  Lightbulb, PenTool, Code2, GripVertical
} from 'lucide-react'

// 文件树组件
const FileTree = () => {
  const [expanded, setExpanded] = useState({ project: true, essays: true })

  const toggle = (key) => setExpanded(prev => ({ ...prev, [key]: !prev[key] }))

  return (
    <div className="text-sm">
      <div
        className="flex items-center gap-2 py-1.5 px-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        onClick={() => toggle('project')}
      >
        {expanded.project ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        <FolderOpen size={16} className="text-primary" />
        <span className="font-medium text-gray-700">我的项目</span>
      </div>
      
      <AnimatePresence>
        {expanded.project && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="ml-4 overflow-hidden"
          >
            <div
              className="flex items-center gap-2 py-1.5 px-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => toggle('essays')}
            >
              {expanded.essays ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              <FolderOpen size={16} className="text-orange-400" />
              <span className="text-gray-600">作文集</span>
            </div>
            
            {expanded.essays && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                className="ml-4"
              >
                <div className="flex items-center gap-2 py-1.5 px-2 rounded-lg bg-primary/5 border border-primary/20 cursor-pointer">
                  <FileText size={16} className="text-primary" />
                  <span className="text-primary font-medium">人工智能.md</span>
                </div>
                <div className="flex items-center gap-2 py-1.5 px-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                  <File size={16} className="text-gray-400" />
                  <span className="text-gray-500">读书笔记.md</span>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// AI聊天组件
const AIChat = () => {
  const [input, setInput] = useState('')
  const messages = [
    { role: 'ai', content: '👋 你好！我是你的写作助手。有什么我可以帮助你的吗？' },
    { role: 'ai', content: '💡 我注意到第二段存在逻辑跳跃，需要我帮你修复吗？' },
    { role: 'user', content: '好的，请帮我看看' },
    { role: 'ai', content: '✨ 建议在"帮助我们学习"和"必须小心"之间添加过渡句，说明为什么需要谨慎。' },
  ]

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto space-y-3 p-1">
        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] px-3 py-2 rounded-2xl text-sm ${
                msg.role === 'user'
                  ? 'bg-primary text-white rounded-br-md'
                  : 'bg-gray-100 text-gray-700 rounded-bl-md'
              }`}
            >
              {msg.content}
            </div>
          </motion.div>
        ))}
      </div>
      
      <div className="mt-3 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入问题..."
          className="flex-1 px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
        />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="p-2 bg-primary text-white rounded-xl hover:bg-primary/90 transition-colors"
        >
          <Send size={18} />
        </motion.button>
      </div>
    </div>
  )
}


// 模式切换开关
const ModeToggle = ({ isIDEMode, onToggle }) => {
  return (
    <div className="flex items-center gap-3 bg-gray-100 p-1 rounded-xl">
      <motion.button
        onClick={() => onToggle(false)}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
          !isIDEMode ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'
        }`}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <PenTool size={16} />
        写作模式
      </motion.button>
      <motion.button
        onClick={() => onToggle(true)}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
          isIDEMode ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'
        }`}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <Code2 size={16} />
        IDE模式
      </motion.button>
    </div>
  )
}

// 结构树组件
const StructureTree = () => {
  const structure = [
    { label: '引言', status: 'connected', icon: CheckCircle, color: 'green' },
    { label: '论点一', status: 'missing', icon: AlertCircle, color: 'rose' },
    { label: '论点二', status: 'connected', icon: CheckCircle, color: 'green' },
    { label: '结论', status: 'connected', icon: CheckCircle, color: 'green' },
  ]

  return (
    <div className="space-y-2">
      {structure.map((item, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.1 }}
          className={`flex items-center gap-3 p-3 rounded-xl ${
            item.color === 'green' ? 'bg-green-50' : 'bg-rose-50'
          }`}
        >
          <item.icon
            size={18}
            className={item.color === 'green' ? 'text-green-600' : 'text-rose-500'}
          />
          <div className="flex-1">
            <div className={`font-medium text-sm ${
              item.color === 'green' ? 'text-green-700' : 'text-rose-600'
            }`}>
              {item.label}
            </div>
            <div className={`text-xs ${
              item.color === 'green' ? 'text-green-600/70' : 'text-rose-500/70'
            }`}>
              {item.status === 'connected' ? '结构完整' : '缺少论据'}
            </div>
          </div>
          <GitBranch size={14} className={
            item.color === 'green' ? 'text-green-400' : 'text-rose-400'
          } />
        </motion.div>
      ))}
    </div>
  )
}

// 健康检查组件
const HealthCheck = () => {
  const metrics = [
    { label: '词汇丰富度', value: 72, color: 'bg-primary' },
    { label: '逻辑连贯性', value: 58, color: 'bg-orange-400' },
    { label: '论证强度', value: 85, color: 'bg-green-500' },
  ]

  return (
    <div className="space-y-4">
      {metrics.map((metric, i) => (
        <div key={i} className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">{metric.label}</span>
            <span className="font-medium text-gray-700">{metric.value}%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${metric.value}%` }}
              transition={{ duration: 1, delay: i * 0.2 }}
              className={`h-full ${metric.color} rounded-full`}
            />
          </div>
        </div>
      ))}
    </div>
  )
}


// 编辑器组件
const Editor = ({ isIDEMode, content, setContent }) => {
  // 将内容按句子分割
  const sentences = content.split(/(?<=[。！？])/g).filter(s => s.trim())

  const handleWriterChange = (e) => {
    setContent(e.target.value)
  }

  const handleIDEChange = (index, newValue) => {
    const newSentences = [...sentences]
    newSentences[index] = newValue
    setContent(newSentences.join(''))
  }

  return (
    <div className="h-full relative">
      <AnimatePresence mode="wait">
        {!isIDEMode ? (
          // 写作模式
          <motion.div
            key="writer"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="h-full"
          >
            <textarea
              value={content}
              onChange={handleWriterChange}
              className="w-full h-full p-8 font-serif text-lg leading-relaxed text-gray-700 bg-transparent resize-none focus:outline-none"
              placeholder="开始写作..."
              style={{ lineHeight: '2' }}
            />
          </motion.div>
        ) : (
          // IDE模式
          <motion.div
            key="ide"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="h-full overflow-auto"
            style={{
              backgroundImage: 'linear-gradient(to right, transparent 48px, #F3F4F6 48px, #F3F4F6 49px, transparent 49px)',
              backgroundSize: '100% 100%',
            }}
          >
            <div className="p-4 space-y-1">
              {sentences.map((sentence, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="flex items-start group"
                >
                  {/* 行号 */}
                  <div className="w-10 flex-shrink-0 text-right pr-4 text-gray-400 text-sm font-mono select-none pt-2">
                    {i + 1}
                  </div>
                  
                  {/* 代码行 */}
                  <div className="flex-1 flex items-start gap-2 py-1.5 px-3 rounded-lg hover:bg-gray-50 transition-colors">
                    {/* 标签 */}
                    {i === 0 && (
                      <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="flex-shrink-0 px-2 py-0.5 bg-green-50 text-green-700 text-xs font-medium rounded-md border border-green-200"
                      >
                        主题句
                      </motion.span>
                    )}
                    {i === 1 && (
                      <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="flex-shrink-0 px-2 py-0.5 bg-orange-50 text-orange-700 text-xs font-medium rounded-md border border-orange-200"
                      >
                        论据
                      </motion.span>
                    )}
                    {i === 2 && (
                      <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="flex-shrink-0 px-2 py-0.5 bg-rose-50 text-rose-600 text-xs font-medium rounded-md border border-rose-200"
                      >
                        ⚠️ 需要过渡
                      </motion.span>
                    )}
                    
                    {/* 句子内容 */}
                    <input
                      type="text"
                      value={sentence}
                      onChange={(e) => handleIDEChange(i, e.target.value)}
                      className="flex-1 font-mono text-sm text-gray-700 bg-transparent focus:outline-none focus:bg-primary/5 rounded px-1 transition-colors"
                    />
                  </div>
                </motion.div>
              ))}
              
              {/* 添加新行提示 */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="flex items-center text-gray-300 text-sm font-mono pl-10 pt-2"
              >
                <span className="w-10 text-right pr-4">{sentences.length + 1}</span>
                <span className="italic">继续写作...</span>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}


// 可调整大小的分隔条
const ResizeHandle = ({ onDrag }) => {
  const [isDragging, setIsDragging] = useState(false)

  const handleMouseDown = (e) => {
    setIsDragging(true)
    e.preventDefault()
  }

  React.useEffect(() => {
    const handleMouseMove = (e) => {
      if (isDragging) {
        onDrag(e.clientX)
      }
    }
    const handleMouseUp = () => setIsDragging(false)

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging, onDrag])

  return (
    <div
      onMouseDown={handleMouseDown}
      className={`w-1 flex-shrink-0 cursor-col-resize group flex items-center justify-center transition-colors ${
        isDragging ? 'bg-primary/30' : 'hover:bg-primary/20'
      }`}
    >
      <div className={`w-1 h-8 rounded-full transition-colors ${
        isDragging ? 'bg-primary' : 'bg-gray-300 group-hover:bg-primary/50'
      }`} />
    </div>
  )
}

// 主应用组件
function App() {
  const [isIDEMode, setIsIDEMode] = useState(false)
  const [content, setContent] = useState(
    '人工智能正在改变世界。它帮助我们更快地学习新知识。然而，我们必须谨慎对待它的发展。'
  )
  const [leftWidth, setLeftWidth] = useState(20)
  const [rightWidth, setRightWidth] = useState(20)

  const handleLeftResize = useCallback((clientX) => {
    const newWidth = (clientX / window.innerWidth) * 100
    if (newWidth >= 15 && newWidth <= 35) {
      setLeftWidth(newWidth)
    }
  }, [])

  const handleRightResize = useCallback((clientX) => {
    const newWidth = ((window.innerWidth - clientX) / window.innerWidth) * 100
    if (newWidth >= 15 && newWidth <= 35) {
      setRightWidth(newWidth)
    }
  }, [])

  return (
    <div className="h-screen bg-background flex flex-col overflow-hidden">
      {/* 顶部栏 */}
      <header className="h-14 bg-white border-b border-border flex items-center justify-between px-6 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-primary to-purple-500 rounded-xl flex items-center justify-center">
            <Sparkles size={18} className="text-white" />
          </div>
          <span className="font-semibold text-gray-800">认知IDE</span>
          <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">Beta</span>
        </div>
        
        <ModeToggle isIDEMode={isIDEMode} onToggle={setIsIDEMode} />
        
        <div className="flex items-center gap-2">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
          >
            保存
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-4 py-2 text-sm font-medium text-white bg-primary hover:bg-primary/90 rounded-lg transition-colors"
          >
            发布
          </motion.button>
        </div>
      </header>

      {/* 主内容区 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 左侧面板 - Hub */}
        <motion.div
          className="bg-white border-r border-border flex flex-col overflow-hidden"
          style={{ width: `${leftWidth}%` }}
          layout
        >
          {/* 文件浏览器 */}
          <div className="flex-1 p-4 border-b border-border overflow-auto">
            <div className="flex items-center gap-2 mb-4">
              <FolderOpen size={18} className="text-primary" />
              <span className="font-semibold text-gray-700">项目文件</span>
            </div>
            <FileTree />
          </div>
          
          {/* AI助手 */}
          <div className="flex-1 p-4 overflow-hidden flex flex-col">
            <div className="flex items-center gap-2 mb-4">
              <Bot size={18} className="text-primary" />
              <span className="font-semibold text-gray-700">AI助手</span>
            </div>
            <div className="flex-1 overflow-hidden">
              <AIChat />
            </div>
          </div>
        </motion.div>

        <ResizeHandle onDrag={handleLeftResize} />

        {/* 中间面板 - Canvas */}
        <motion.div
          className="flex-1 bg-white flex flex-col overflow-hidden"
          layout
        >
          {/* 编辑器标签栏 */}
          <div className="h-10 border-b border-border flex items-center px-4 bg-gray-50/50">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-white rounded-t-lg border border-b-0 border-border -mb-px">
              <FileText size={14} className="text-primary" />
              <span className="text-sm font-medium text-gray-700">人工智能.md</span>
              <button className="ml-2 text-gray-400 hover:text-gray-600 text-xs">×</button>
            </div>
          </div>
          
          {/* 编辑器内容 */}
          <div className="flex-1 overflow-hidden">
            <Editor isIDEMode={isIDEMode} content={content} setContent={setContent} />
          </div>
          
          {/* 状态栏 */}
          <div className="h-6 bg-gray-50 border-t border-border flex items-center justify-between px-4 text-xs text-gray-500">
            <div className="flex items-center gap-4">
              <span>字数: {content.length}</span>
              <span>句子: {content.split(/(?<=[。！？])/g).filter(s => s.trim()).length}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full"></span>
              <span>已保存</span>
            </div>
          </div>
        </motion.div>

        <ResizeHandle onDrag={handleRightResize} />

        {/* 右侧面板 - Inspector */}
        <motion.div
          className="bg-white border-l border-border flex flex-col overflow-hidden"
          style={{ width: `${rightWidth}%` }}
          layout
        >
          {/* 结构图 */}
          <div className="flex-1 p-4 border-b border-border overflow-auto">
            <div className="flex items-center gap-2 mb-4">
              <GitBranch size={18} className="text-primary" />
              <span className="font-semibold text-gray-700">结构分析</span>
            </div>
            <StructureTree />
          </div>
          
          {/* 健康检查 */}
          <div className="flex-1 p-4 overflow-auto">
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb size={18} className="text-primary" />
              <span className="font-semibold text-gray-700">写作健康度</span>
            </div>
            <HealthCheck />
            
            {/* 建议卡片 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="mt-6 p-4 bg-orange-50 rounded-xl border border-orange-200"
            >
              <div className="flex items-start gap-3">
                <AlertCircle size={18} className="text-orange-600 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-orange-700 text-sm">改进建议</div>
                  <div className="text-xs text-orange-600/80 mt-1">
                    第二句和第三句之间缺少逻辑过渡，建议添加连接词或过渡句。
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default App
