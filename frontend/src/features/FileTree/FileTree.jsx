import { useState, useEffect, useRef, forwardRef } from 'react'
import {
  FileCode,
  FileType,
  FileText,
  MoreHorizontal,
  Trash2,
  Pencil,
  Tag,
  Plus,
  Loader2,
  RefreshCw,
} from 'lucide-react'
import { useSession } from '../../hooks/useSession'

// TODO: 替换为实际的用户ID获取逻辑
const USER_ID = 'user-001'

const categories = [
  { id: 'all', label: '全部' },
  { id: 'literature', label: '文学' },
  { id: 'science', label: '理科' },
  { id: 'active', label: '进行中' },
]

const getModeIcon = (mode) => {
  switch (mode) {
    case 'science':
      return { icon: FileCode, color: 'text-orange-500' }
    case 'literature':
      return { icon: FileType, color: 'text-indigo-500' }
    default:
      return { icon: FileText, color: 'text-emerald-500' }
  }
}

const getModeTag = (mode, status) => {
  if (status === 'active') return { className: 'bg-green-50 text-green-600', label: '进行中' }
  switch (mode) {
    case 'science':
      return { className: 'bg-orange-50 text-orange-600', label: '理科' }
    case 'literature':
      return { className: 'bg-indigo-50 text-indigo-600', label: '文学' }
    default:
      return { className: 'bg-gray-100 text-gray-500', label: '其他' }
  }
}

// 右键菜单
const ContextMenu = forwardRef(({ x, y, onAction, currentMode }, ref) => (
  <div
    ref={ref}
    className="fixed bg-white shadow-xl rounded-lg border border-gray-100 py-1 z-50 min-w-[140px]"
    style={{ left: x, top: y }}
  >
    <button
      onClick={() => onAction('rename')}
      className="w-full px-3 py-1.5 text-xs flex items-center gap-2 hover:bg-gray-50 text-gray-600"
    >
      <Pencil size={12} />
      <span>重命名</span>
    </button>
    <button
      onClick={() => onAction('changeMode')}
      className="w-full px-3 py-1.5 text-xs flex items-center gap-2 hover:bg-gray-50 text-gray-600"
    >
      <Tag size={12} />
      <span>切换为{currentMode === 'literature' ? '理科' : '文学'}</span>
    </button>
    <div className="my-1 border-t border-gray-100" />
    <button
      onClick={() => onAction('delete')}
      className="w-full px-3 py-1.5 text-xs flex items-center gap-2 hover:bg-gray-50 text-red-500"
    >
      <Trash2 size={12} />
      <span>删除</span>
    </button>
  </div>
))
ContextMenu.displayName = 'ContextMenu'


// 管理菜单
const ManageMenu = forwardRef(({ x, y, onAction }, ref) => (
  <div
    ref={ref}
    className="fixed bg-white shadow-xl rounded-lg border border-gray-100 py-1 z-50 min-w-[120px]"
    style={{ left: x, top: y }}
  >
    <button
      onClick={() => onAction('refresh')}
      className="w-full px-3 py-1.5 text-xs flex items-center gap-2 hover:bg-gray-50 text-gray-600"
    >
      <RefreshCw size={12} />
      <span>刷新列表</span>
    </button>
  </div>
))
ManageMenu.displayName = 'ManageMenu'

// 重命名输入框
const RenameInput = ({ value, onConfirm, onCancel }) => {
  const [inputValue, setInputValue] = useState(value)
  const inputRef = useRef(null)

  useEffect(() => {
    inputRef.current?.focus()
    inputRef.current?.select()
  }, [])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      onConfirm(inputValue.trim() || value)
    } else if (e.key === 'Escape') {
      onCancel()
    }
  }

  return (
    <div className="flex items-center gap-1 flex-1">
      <input
        ref={inputRef}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onBlur={() => onConfirm(inputValue.trim() || value)}
        className="flex-1 px-1 py-0.5 text-xs border border-indigo-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400"
      />
    </div>
  )
}

export const FileTree = ({ onSessionSelect, activeSessionId: externalActiveId }) => {
  const [activeFilter, setActiveFilter] = useState('all')
  const [localActiveId, setLocalActiveId] = useState(null)
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, targetId: null, targetMode: null })
  const [manageMenu, setManageMenu] = useState({ visible: false, x: 0, y: 0 })
  const [renamingId, setRenamingId] = useState(null)
  const menuRef = useRef(null)
  const manageMenuRef = useRef(null)

  const activeSessionId = externalActiveId || localActiveId

  const { sessions, loading, error, fetchSessions, createSession, deleteSession, updateSession } = useSession()

  // 加载会话列表
  useEffect(() => {
    fetchSessions({ user_id: USER_ID })
  }, [fetchSessions])

  // 筛选会话 (排除已删除的)
  const filtered = sessions.filter((s) => {
    // 首先排除已删除的会话
    if (s.status === 'deleted') return false
    
    if (activeFilter === 'all') return true
    if (activeFilter === 'active') return s.status === 'active'
    return s.mode === activeFilter
  })

  // 关闭菜单
  useEffect(() => {
    const close = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setContextMenu({ visible: false, x: 0, y: 0, targetId: null, targetMode: null })
      }
      if (manageMenuRef.current && !manageMenuRef.current.contains(e.target)) {
        setManageMenu({ visible: false, x: 0, y: 0 })
      }
    }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [])

  const handleContext = (e, id, mode) => {
    e.preventDefault()
    setContextMenu({ visible: true, x: e.clientX, y: e.clientY, targetId: id, targetMode: mode })
    setManageMenu({ visible: false, x: 0, y: 0 })
  }

  const handleManageClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    setManageMenu({ visible: !manageMenu.visible, x: rect.left, y: rect.bottom + 4 })
    setContextMenu({ visible: false, x: 0, y: 0, targetId: null, targetMode: null })
  }


  // 右键菜单操作
  const handleAction = async (action) => {
    const targetId = contextMenu.targetId
    const targetMode = contextMenu.targetMode
    setContextMenu({ visible: false, x: 0, y: 0, targetId: null, targetMode: null })

    if (!targetId) return

    switch (action) {
      case 'delete':
        try {
          await deleteSession(targetId)
          if (activeSessionId === targetId) setLocalActiveId(null)
          // 刷新列表确保同步
          await fetchSessions({ user_id: USER_ID })
          console.log('[API] 删除会话成功:', targetId)
        } catch (err) {
          console.error('[API] 删除会话失败:', err)
        }
        break

      case 'rename':
        setRenamingId(targetId)
        break

      case 'changeMode':
        try {
          const newMode = targetMode === 'literature' ? 'science' : 'literature'
          await updateSession(targetId, { mode: newMode })
          await fetchSessions({ user_id: USER_ID }) // 刷新列表
          console.log('[API] 更改模式成功:', targetId, '->', newMode)
        } catch (err) {
          console.error('[API] 更改模式失败:', err)
        }
        break
    }
  }

  // 管理菜单操作
  const handleManageAction = async (action) => {
    setManageMenu({ visible: false, x: 0, y: 0 })
    if (action === 'refresh') {
      await fetchSessions({ user_id: USER_ID })
      console.log('[API] 刷新会话列表')
    }
  }

  // 重命名确认
  const handleRenameConfirm = async (newTitle) => {
    const targetId = renamingId
    setRenamingId(null)
    if (!targetId || !newTitle) return

    try {
      await updateSession(targetId, { title: newTitle })
      await fetchSessions({ user_id: USER_ID })
      console.log('[API] 重命名成功:', targetId, '->', newTitle)
    } catch (err) {
      console.error('[API] 重命名失败:', err)
    }
  }

  // 创建会话
  const handleCreateSession = async () => {
    try {
      const newSession = await createSession({
        user_id: USER_ID,
        title: `新会话 ${new Date().toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}`,
        mode: 'literature',
      })
      const newId = newSession.id || newSession.session_id
      setLocalActiveId(newId)
      onSessionSelect?.(newSession)
      await fetchSessions({ user_id: USER_ID }) // 刷新列表
      console.log('[API] 创建会话成功:', newId)
    } catch (err) {
      console.error('[API] 创建会话失败:', err)
    }
  }

  const handleSelectSession = (session) => {
    const id = session.id || session.session_id
    setLocalActiveId(id)
    onSessionSelect?.(session)
    console.log('[API] 选择会话:', id)
  }


  return (
    <div className="flex flex-col h-full text-sm">
      {/* Header */}
      <div className="px-3 py-2 flex items-center justify-between">
        <span className="text-[10px] font-bold text-gray-400 tracking-wider uppercase">Sessions</span>
        <div className="flex items-center gap-1">
          <button
            onClick={handleCreateSession}
            disabled={loading}
            className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600 disabled:opacity-50"
            title="新建会话"
          >
            <Plus size={14} />
          </button>
          <button
            onClick={handleManageClick}
            className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600"
            title="管理"
          >
            <MoreHorizontal size={14} />
          </button>
        </div>
      </div>

      {/* Filter Pills */}
      <div className="px-3 pb-2 flex gap-1.5 overflow-x-auto">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveFilter(cat.id)}
            className={`h-6 px-2 rounded text-[10px] font-medium whitespace-nowrap transition-colors ${
              activeFilter === cat.id
                ? 'bg-indigo-100 text-indigo-700'
                : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto">
        {loading && sessions.length === 0 ? (
          <div className="flex items-center justify-center py-8 text-gray-400">
            <Loader2 size={16} className="animate-spin mr-2" />
            <span className="text-xs">加载中...</span>
          </div>
        ) : error ? (
          <div className="px-3 py-4 text-xs text-red-500">{error}</div>
        ) : filtered.length === 0 ? (
          <div className="px-3 py-8 text-xs text-gray-400 text-center">暂无会话，点击 + 创建</div>
        ) : (
          filtered.map((session) => {
            const sessionId = session.id || session.session_id
            const { icon: Icon, color } = getModeIcon(session.mode)
            const tag = getModeTag(session.mode, session.status)
            const isActive = activeSessionId === sessionId
            const isRenaming = renamingId === sessionId

            return (
              <div
                key={sessionId}
                onClick={() => !isRenaming && handleSelectSession(session)}
                onContextMenu={(e) => handleContext(e, sessionId, session.mode)}
                className={`h-8 px-3 flex items-center gap-2 cursor-pointer transition-colors ${
                  isActive ? 'bg-indigo-50 border-r-2 border-indigo-500' : 'hover:bg-gray-100/80'
                }`}
              >
                <Icon size={14} className={color} />
                {isRenaming ? (
                  <RenameInput
                    value={session.title || '未命名会话'}
                    onConfirm={handleRenameConfirm}
                    onCancel={() => setRenamingId(null)}
                  />
                ) : (
                  <>
                    <span
                      className={`flex-1 truncate ${isActive ? 'text-indigo-700 font-medium' : 'text-gray-700'}`}
                    >
                      {session.title || '未命名会话'}
                    </span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-sm ${tag.className}`}>{tag.label}</span>
                  </>
                )}
              </div>
            )
          })
        )}
      </div>

      {/* Context Menu */}
      {contextMenu.visible && (
        <ContextMenu
          ref={menuRef}
          x={contextMenu.x}
          y={contextMenu.y}
          currentMode={contextMenu.targetMode}
          onAction={handleAction}
        />
      )}

      {/* Manage Menu */}
      {manageMenu.visible && (
        <ManageMenu ref={manageMenuRef} x={manageMenu.x} y={manageMenu.y} onAction={handleManageAction} />
      )}
    </div>
  )
}
