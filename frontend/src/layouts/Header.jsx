import { Cloud, Loader2, Maximize2, Minimize2, Play, Pause, RotateCcw } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'

// 格式化保存时间
const formatSaveTime = (date) => {
  if (!date) return null
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '已保存'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 自定义毛笔图标
const BrushIcon = ({ size = 16, className = '' }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M18 2l-4 4" />
    <path d="M14 6l-10 10v4h4l10-10" />
    <path d="M10 16l-2 2" />
  </svg>
)

// 番茄钟预设时长（分钟）
const FOCUS_PRESETS = [15, 25, 45, 60]

// 奖牌配置
const getMedalEmoji = (minutes) => {
  if (minutes >= 60) return '🏅'
  if (minutes >= 45) return '🥈'
  if (minutes >= 25) return '🥉'
  return '⭐'
}

export const Header = ({ syncing = false, lastSaved }) => {
  const saveTimeText = formatSaveTime(lastSaved)
  const [isZenMode, setIsZenMode] = useState(false)

  // 番茄钟状态
  const [focusGoal, setFocusGoal] = useState(25)
  const [timeLeft, setTimeLeft] = useState(25 * 60)
  const [isRunning, setIsRunning] = useState(false)
  const [showPicker, setShowPicker] = useState(false)
  const timerRef = useRef(null)
  const pickerRef = useRef(null)

  // 计时器逻辑
  useEffect(() => {
    if (isRunning && timeLeft > 0) {
      timerRef.current = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            clearInterval(timerRef.current)
            setIsRunning(false)
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }
    return () => clearInterval(timerRef.current)
  }, [isRunning])

  // 开始/暂停
  const toggleTimer = () => {
    if (timeLeft === 0) {
      setTimeLeft(focusGoal * 60)
    }
    setIsRunning(!isRunning)
  }

  // 重置
  const resetTimer = () => {
    setIsRunning(false)
    setTimeLeft(focusGoal * 60)
  }

  // 选择时长
  const selectDuration = (mins) => {
    if (isRunning) return
    setFocusGoal(mins)
    setTimeLeft(mins * 60)
    setShowPicker(false)
  }

  // 点击外部关闭选择器
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (pickerRef.current && !pickerRef.current.contains(e.target)) {
        setShowPicker(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // 格式化时间显示
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const progress = ((focusGoal * 60 - timeLeft) / (focusGoal * 60)) * 100

  // 禅模式
  const toggleZenMode = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
      setIsZenMode(true)
    } else {
      document.exitFullscreen()
      setIsZenMode(false)
    }
  }

  useEffect(() => {
    const handleFullscreenChange = () => setIsZenMode(!!document.fullscreenElement)
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }, [])

  return (
    <header className="header-aurora h-11 backdrop-blur-sm flex items-center justify-between pl-4 flex-shrink-0 shadow-sm">
      {/* 左侧：Logo */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-sm shadow-indigo-200">
            <BrushIcon size={14} className="text-white" />
          </div>
          <span className="text-sm font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            游刃 IDE
          </span>
        </div>

        <div className="h-4 w-px bg-gray-200" />
        <span className="text-xs text-gray-400">K12 写作学习平台</span>
      </div>

      {/* 右侧 */}
      <div className="flex items-center h-full">
        {/* 主要内容区 */}
        <div className="flex items-center gap-3 pr-3">
          {/* 番茄钟 */}
          <div className="relative flex items-center" ref={pickerRef}>
            {/* 横向滑出的时长选择器 - 运行中禁用 */}
            <div
              className={`flex items-center gap-1 overflow-hidden transition-all duration-300 ease-out ${
                showPicker && !isRunning ? 'max-w-[200px] opacity-100 mr-2' : 'max-w-0 opacity-0'
              }`}
            >
              {FOCUS_PRESETS.map((mins) => (
                <button
                  key={mins}
                  onClick={() => selectDuration(mins)}
                  disabled={isRunning}
                  className={`flex items-center gap-1 px-2 py-1 rounded-full text-[11px] whitespace-nowrap transition-all ${
                    focusGoal === mins
                      ? 'bg-indigo-100 text-indigo-700 border border-indigo-200'
                      : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-gray-100'
                  }`}
                >
                  <span>{getMedalEmoji(mins)}</span>
                  <span>{mins}</span>
                </button>
              ))}
            </div>

            {/* 时间显示 + 进度 - 专注中有七彩流光边框 */}
            <button
              onClick={() => !isRunning && setShowPicker(!showPicker)}
              className={`relative flex items-center gap-2 px-2.5 py-1 rounded-full transition-all ${
                isRunning
                  ? 'bg-white cursor-default rainbow-border'
                  : showPicker
                    ? 'bg-indigo-50 border border-indigo-200'
                    : 'bg-gray-50 border border-gray-200 hover:border-gray-300'
              }`}
            >
              {/* 迷你进度环 */}
              <div className="relative w-4 h-4">
                <svg className="w-4 h-4 -rotate-90">
                  <circle cx="8" cy="8" r="6" fill="none" stroke="#e5e7eb" strokeWidth="2" />
                  <circle
                    cx="8"
                    cy="8"
                    r="6"
                    fill="none"
                    stroke={isRunning ? '#10b981' : '#6366f1'}
                    strokeWidth="2"
                    strokeDasharray={`${(progress / 100) * 37.7} 37.7`}
                    className="transition-all duration-1000"
                  />
                </svg>
                {isRunning && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-1 h-1 rounded-full bg-emerald-500 animate-pulse" />
                  </div>
                )}
              </div>

              <span className={`text-xs font-mono font-medium ${isRunning ? 'text-emerald-600' : 'text-gray-600'}`}>
                {formatTime(timeLeft)}
              </span>
            </button>

            {/* 控制按钮 */}
            <button
              onClick={toggleTimer}
              className={`ml-1.5 p-1.5 rounded-lg transition-all ${
                isRunning
                  ? 'bg-emerald-100 text-emerald-600 hover:bg-emerald-200'
                  : 'bg-indigo-100 text-indigo-600 hover:bg-indigo-200'
              }`}
              title={isRunning ? '暂停' : '开始专注'}
            >
              {isRunning ? <Pause size={12} /> : <Play size={12} />}
            </button>

            {/* 非运行中且有进度：重置按钮 */}
            {!isRunning && timeLeft !== focusGoal * 60 && (
              <button
                onClick={resetTimer}
                className="ml-1 p-1.5 rounded-lg bg-gray-100 text-gray-500 hover:bg-gray-200 transition-all"
                title="重置"
              >
                <RotateCcw size={12} />
              </button>
            )}
          </div>

          {/* 专注状态 */}
          <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full border ${
            isRunning 
              ? 'bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-100/50'
              : 'bg-gradient-to-r from-amber-50 to-yellow-50 border-amber-100/50'
          }`}>
            {isRunning ? (
              <>
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[10px] text-emerald-600 font-medium">专注中</span>
              </>
            ) : (
              <>
                <div className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                <span className="text-[10px] text-amber-600">待专注</span>
              </>
            )}
          </div>

          {/* 同步状态 */}
          <div className="flex items-center gap-1.5 text-xs">
            {syncing ? (
              <div className="flex items-center gap-1 text-indigo-500">
                <Loader2 size={12} className="animate-spin" />
                <span>保存中</span>
              </div>
            ) : saveTimeText ? (
              <div className="flex items-center gap-1 text-emerald-600">
                <Cloud size={12} />
                <span>{saveTimeText}</span>
              </div>
            ) : (
              <div className="flex items-center gap-1 text-gray-400">
                <div className="w-1.5 h-1.5 rounded-full bg-gray-300" />
                <span>未保存</span>
              </div>
            )}
          </div>
        </div>

        {/* 右侧边栏对齐区域 */}
        <div className="w-11 h-full flex items-center justify-center border-l border-gray-200 bg-slate-50/50">
          <button
            onClick={toggleZenMode}
            className={`p-1.5 rounded-lg transition-all ${
              isZenMode ? 'bg-indigo-100 text-indigo-600' : 'hover:bg-gray-200 text-gray-400 hover:text-gray-600'
            }`}
            title={isZenMode ? '退出专注模式' : '进入专注模式'}
          >
            {isZenMode ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
        </div>
      </div>
    </header>
  )
}
