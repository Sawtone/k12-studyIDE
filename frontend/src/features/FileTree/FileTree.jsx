import { useState, useEffect, useRef, forwardRef } from 'react'
import {
  FileCode,
  FileType,
  Trash2,
  Pencil,
  Tag,
  Plus,
  Loader2,
  RefreshCw,
  ChevronLeft
} from 'lucide-react'
import { useSession } from '../../hooks/useSession'

const USER_ID = 'user-001'

const categories = [
  { id: 'all', label: '全部' },
  { id: 'literature', label: '文学' },
  { id: 'science', label: '理科' },
]

// 格式化时间
const formatTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// 生成有趣的默认会话名称
const generateSessionTitle = () => {
  const prefixes = ['我的', '新', '']
  const subjects = [
    '随笔', '日记', '故事', '感想', '札记', '小记',
    '作文', '文章', '创作', '灵感', '思绪', '手记'
  ]
  const timeLabels = () => {
    const now = new Date()
    const hour = now.getHours()
    if (hour < 6) return '深夜'
    if (hour < 9) return '清晨'
    if (hour < 12) return '上午'
    if (hour < 14) return '午后'
    if (hour < 18) return '下午'
    if (hour < 21) return '傍晚'
    return '夜间'
  }
  
  const random = Math.random()
  if (random < 0.4) {
    // 时间 + 主题
    return `${timeLabels()}${subjects[Math.floor(Math.random() * subjects.length)]}`
  } else if (random < 0.7) {
    // 前缀 + 主题
    return `${prefixes[Math.floor(Math.random() * prefixes.length)]}${subjects[Math.floor(Math.random() * subjects.length)]}`
  } else {
    // 日期格式
    const now = new Date()
    const month = now.getMonth() + 1
    const day = now.getDate()
    return `${month}月${day}日随笔`
  }
}

const getModeConfig = (mode) => {
  switch (mode) {
    case 'science':
      return {
        icon: FileCode,
        color: 'text-amber-500',
        bg: 'bg-amber-50',
        border: 'border-amber-100',
        label: '理科',
      }
    case 'literature':
      return {
        icon: FileType,
        color: 'text-violet-500',
        bg: 'bg-violet-50',
        border: 'border-violet-100',
        label: '文学',
      }
    default:
      return {
        icon: FileType,
        color: 'text-gray-400',
        bg: 'bg-gray-50',
        border: 'border-gray-100',
        label: '其他',
      }
  }
}

// 右键菜单
const ContextMenu = forwardRef(({ x, y, onAction, currentMode }, ref) => (
  <div
    ref={ref}
    className="fixed bg-white/95 backdrop-blur-sm shadow-lg rounded-lg border border-gray-200/60 py-1 z-50 min-w-[120px]"
    style={{ left: x, top: y }}
  >
    <button
      onClick={() => onAction('rename')}
      className="w-full px-3 py-1.5 text-xs flex items-center gap-2 hover:bg-gray-50 text-gray-600 transition-colors"
    >
      <Pencil size={12} />
      <span>重命名</span>
    </button>
    <button
      onClick={() => onAction('changeMode')}
      className="w-full px-3 py-1.5 text-xs flex items-center gap-2 hover:bg-gray-50 text-gray-600 transition-colors"
    >
      <Tag size={12} />
      <span>切换为{currentMode === 'literature' ? '理科' : '文学'}</span>
    </button>
    <div className="my-1 border-t border-gray-100" />
    <button
      onClick={() => onAction('delete')}
      className="w-full px-3 py-1.5 text-xs flex items-center gap-2 hover:bg-red-50 text-red-500 transition-colors"
    >
      <Trash2 size={12} />
      <span>删除</span>
    </button>
  </div>
))
ContextMenu.displayName = 'ContextMenu'


// 会话卡片
const SessionCard = ({ session, isActive, isRenaming, onSelect, onContext, onRenameConfirm, onRenameCancel }) => {
  const sessionId = session.id || session.session_id
  const config = getModeConfig(session.mode)
  const Icon = config.icon
  const [renameValue, setRenameValue] = useState(session.title || '未命名')
  const inputRef = useRef(null)

  useEffect(() => {
    if (isRenaming) {
      inputRef.current?.focus()
      inputRef.current?.select()
    }
  }, [isRenaming])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') onRenameConfirm(renameValue.trim() || session.title)
    else if (e.key === 'Escape') onRenameCancel()
  }

  // 根据模式获取选中状态的样式
  const getActiveStyles = () => {
    if (!isActive) return 'bg-white hover:bg-gray-50/80 border-gray-100 hover:border-gray-200 hover:shadow-sm'
    if (session.mode === 'science') return 'bg-gradient-to-br from-amber-50 to-white border-amber-200 shadow-sm'
    return 'bg-gradient-to-br from-violet-50 to-white border-violet-200 shadow-sm'
  }

  const getIndicatorColor = () => {
    if (session.mode === 'science') return 'bg-amber-500'
    return 'bg-violet-500'
  }

  return (
    <div
      onClick={() => !isRenaming && onSelect(session)}
      onContextMenu={(e) => onContext(e, sessionId, session.mode)}
      className={`
        group relative mx-2 mb-2 p-2.5 rounded-xl cursor-pointer
        transition-all duration-200 ease-out border
        ${getActiveStyles()}
      `}
    >
      {/* 顶部：图标 + 标题 + Tag */}
      <div className="flex items-start gap-2">
        <div className={`p-1.5 rounded-lg ${config.bg} ${config.border} border flex-shrink-0`}>
          <Icon size={14} className={config.color} />
        </div>
        <div className="flex-1 min-w-0">
          {isRenaming ? (
            <input
              ref={inputRef}
              value={renameValue}
              onChange={(e) => setRenameValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={() => onRenameConfirm(renameValue.trim() || session.title)}
              className="w-full px-1.5 py-0.5 text-xs font-medium border border-indigo-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400 bg-white"
            />
          ) : (
            <h4 className={`text-xs font-medium truncate leading-tight ${isActive ? 'text-gray-800' : 'text-gray-700'}`}>
              {session.title || '未命名'}
            </h4>
          )}
          <div className="flex items-center gap-1.5 mt-1">
            <span className={`text-[9px] px-1.5 py-0.5 rounded-full ${config.bg} ${config.color} font-medium`}>
              {config.label}
            </span>
            <span className="text-[9px] text-gray-400">
              {formatTime(session.updated_at || session.created_at)}
            </span>
          </div>
        </div>
      </div>

      {/* 预览文字 */}
      {session.preview && (
        <p className="mt-2 text-[10px] text-gray-400 line-clamp-2 leading-relaxed pl-8">
          {session.preview}
        </p>
      )}

      {/* 选中指示器 */}
      {isActive && (
        <div className={`absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 rounded-r-full ${getIndicatorColor()}`} />
      )}
    </div>
  )
}


export const FileTree = ({ onSessionSelect, activeSessionId: externalActiveId, onCollapse }) => {
  const [activeFilter, setActiveFilter] = useState('all')
  const [localActiveId, setLocalActiveId] = useState(null)
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, targetId: null, targetMode: null })
  const [renamingId, setRenamingId] = useState(null)
  const menuRef = useRef(null)

  const activeSessionId = externalActiveId || localActiveId
  const { sessions, loading, error, fetchSessions, createSession, deleteSession, updateSession } = useSession()

  useEffect(() => {
    fetchSessions({ user_id: USER_ID })
  }, [fetchSessions])

  const filtered = sessions.filter((s) => {
    if (s.status === 'deleted') return false
    if (activeFilter === 'all') return true
    return s.mode === activeFilter
  })

  useEffect(() => {
    const close = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target))
        setContextMenu({ visible: false, x: 0, y: 0, targetId: null, targetMode: null })
    }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [])

  const handleContext = (e, id, mode) => {
    e.preventDefault()
    setContextMenu({ visible: true, x: e.clientX, y: e.clientY, targetId: id, targetMode: mode })
  }

  const handleAction = async (action) => {
    const { targetId, targetMode } = contextMenu
    setContextMenu({ visible: false, x: 0, y: 0, targetId: null, targetMode: null })
    if (!targetId) return

    switch (action) {
      case 'delete':
        try {
          await deleteSession(targetId)
          if (activeSessionId === targetId) setLocalActiveId(null)
          await fetchSessions({ user_id: USER_ID })
        } catch (err) {
          console.error('删除失败:', err)
        }
        break
      case 'rename':
        setRenamingId(targetId)
        break
      case 'changeMode':
        try {
          await updateSession(targetId, { mode: targetMode === 'literature' ? 'science' : 'literature' })
          await fetchSessions({ user_id: USER_ID })
        } catch (err) {
          console.error('切换模式失败:', err)
        }
        break
    }
  }

  const handleRenameConfirm = async (newTitle) => {
    const targetId = renamingId
    setRenamingId(null)
    if (!targetId || !newTitle) return
    try {
      await updateSession(targetId, { title: newTitle })
      await fetchSessions({ user_id: USER_ID })
    } catch (err) {
      console.error('重命名失败:', err)
    }
  }

  const handleCreateSession = async () => {
    try {
      const newSession = await createSession({
        user_id: USER_ID,
        title: generateSessionTitle(),
        mode: 'literature',
      })
      const newId = newSession.id || newSession.session_id
      setLocalActiveId(newId)
      onSessionSelect?.(newSession)
      await fetchSessions({ user_id: USER_ID })
    } catch (err) {
      console.error('创建失败:', err)
    }
  }

  const handleSelectSession = (session) => {
    const id = session.id || session.session_id
    setLocalActiveId(id)
    onSessionSelect?.(session)
  }


  return (
    <div className="flex flex-col h-full bg-gray-50/30">
      {/* Header */}
      <div className="px-3 py-2.5 flex items-center justify-between bg-white border-b border-gray-100">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold text-gray-500 tracking-wider uppercase">会话</span>
          <span className="text-[9px] text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded-full">
            {filtered.length}
          </span>
        </div>
        <div className="flex items-center gap-0.5">
          <button
            onClick={handleCreateSession}
            disabled={loading}
            className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 disabled:opacity-50 transition-colors"
            title="新建会话"
          >
            <Plus size={14} />
          </button>
          <button
            onClick={() => fetchSessions({ user_id: USER_ID })}
            disabled={loading}
            className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 disabled:opacity-50 transition-colors"
            title="刷新"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          </button>
          {onCollapse && (
            <button
              onClick={onCollapse}
              className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
              title="收起面板"
            >
              <ChevronLeft size={14} />
            </button>
          )}
        </div>
      </div>

      {/* Filter Pills */}
      <div className="px-3 py-2 flex gap-1.5 bg-white border-b border-gray-100/50">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveFilter(cat.id)}
            className={`px-2.5 py-1 rounded-full text-[10px] font-medium transition-all duration-200 ${
              activeFilter === cat.id
                ? 'bg-indigo-500 text-white shadow-sm'
                : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto py-2">
        {loading && sessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400">
            <Loader2 size={20} className="animate-spin mb-2" />
            <span className="text-xs">加载中...</span>
          </div>
        ) : error ? (
          <div className="mx-3 p-3 text-xs text-red-500 bg-red-50 rounded-lg">{error}</div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400">
            <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mb-3">
              <Plus size={20} className="text-gray-300" />
            </div>
            <span className="text-xs">暂无会话</span>
            <button
              onClick={handleCreateSession}
              className="mt-2 text-[10px] text-indigo-500 hover:text-indigo-600 font-medium"
            >
              创建第一个会话
            </button>
          </div>
        ) : (
          filtered.map((session) => (
            <SessionCard
              key={session.id || session.session_id}
              session={session}
              isActive={activeSessionId === (session.id || session.session_id)}
              isRenaming={renamingId === (session.id || session.session_id)}
              onSelect={handleSelectSession}
              onContext={handleContext}
              onRenameConfirm={handleRenameConfirm}
              onRenameCancel={() => setRenamingId(null)}
            />
          ))
        )}
      </div>

      {contextMenu.visible && (
        <ContextMenu
          ref={menuRef}
          x={contextMenu.x}
          y={contextMenu.y}
          currentMode={contextMenu.targetMode}
          onAction={handleAction}
        />
      )}
    </div>
  )
}
