import { useState, useEffect, useRef, forwardRef } from 'react'
import { FileCode, FileType, FileText, MoreHorizontal, Pin, Trash2, Pencil, Tag, Plus } from 'lucide-react'

const mockFiles = [
  { id: 1, name: '二次函数应用.md', category: 'math', iconType: 'code' },
  { id: 2, name: '我的梦想作文.md', category: 'english', iconType: 'text' },
  { id: 3, name: '物理实验报告.md', category: 'drafts', iconType: 'file' },
  { id: 4, name: '古诗词鉴赏.md', category: 'english', iconType: 'text' },
  { id: 5, name: '几何证明练习.md', category: 'math', iconType: 'code' },
  { id: 6, name: '读书心得草稿.md', category: 'drafts', iconType: 'file' },
  { id: 7, name: '三角函数笔记.md', category: 'math', iconType: 'code' },
  { id: 8, name: '英语语法总结.md', category: 'english', iconType: 'text' },
]

const categories = [
  { id: 'all', label: '全部' },
  { id: 'math', label: '数学' },
  { id: 'english', label: '语文' },
  { id: 'drafts', label: '草稿' },
]

const iconMap = {
  code: { icon: FileCode, color: 'text-orange-500' },
  text: { icon: FileType, color: 'text-indigo-500' },
  file: { icon: FileText, color: 'text-emerald-500' },
}

const tagColors = {
  math: 'bg-orange-50 text-orange-600',
  english: 'bg-indigo-50 text-indigo-600',
  drafts: 'bg-gray-100 text-gray-500',
}

const tagLabels = { math: '数学', english: '语文', drafts: '草稿' }

const ContextMenu = forwardRef(({ x, y, onAction }, ref) => (
  <div ref={ref} className="fixed bg-white shadow-xl rounded-lg border border-gray-100 py-1 z-50 min-w-[140px]" style={{ left: x, top: y }}>
    {[
      { id: 'rename', icon: Pencil, label: '重命名' },
      { id: 'tag', icon: Tag, label: '更改标签' },
      { id: 'pin', icon: Pin, label: '置顶' },
    ].map(item => (
      <button key={item.id} onClick={() => onAction(item.id)} className="w-full px-3 py-1.5 text-xs flex items-center gap-2 hover:bg-gray-50 text-gray-600">
        <item.icon size={12} />
        <span>{item.label}</span>
      </button>
    ))}
    <div className="my-1 border-t border-gray-100" />
    <button onClick={() => onAction('delete')} className="w-full px-3 py-1.5 text-xs flex items-center gap-2 hover:bg-gray-50 text-red-500">
      <Trash2 size={12} />
      <span>删除</span>
    </button>
  </div>
))
ContextMenu.displayName = 'ContextMenu'

export const FileTree = () => {
  const [activeFilter, setActiveFilter] = useState('all')
  const [activeFile, setActiveFile] = useState(1)
  const [files, setFiles] = useState(mockFiles)
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, targetId: null })
  const menuRef = useRef(null)

  const filtered = files.filter(f => activeFilter === 'all' || f.category === activeFilter)

  useEffect(() => {
    const close = (e) => { if (menuRef.current && !menuRef.current.contains(e.target)) setContextMenu({ visible: false, x: 0, y: 0, targetId: null }) }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [])

  const handleContext = (e, id) => { e.preventDefault(); setContextMenu({ visible: true, x: e.clientX, y: e.clientY, targetId: id }) }
  const handleAction = (action) => {
    if (action === 'delete') setFiles(prev => prev.filter(f => f.id !== contextMenu.targetId))
    setContextMenu({ visible: false, x: 0, y: 0, targetId: null })
  }

  return (
    <div className="flex flex-col h-full text-sm">
      {/* Header */}
      <div className="px-3 py-2 flex items-center justify-between">
        <span className="text-[10px] font-bold text-gray-400 tracking-wider uppercase">Projects</span>
        <div className="flex items-center gap-1">
          <button className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600"><Plus size={14} /></button>
          <button className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600"><MoreHorizontal size={14} /></button>
        </div>
      </div>

      {/* Filter Pills */}
      <div className="px-3 pb-2 flex gap-1.5 overflow-x-auto">
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => setActiveFilter(cat.id)}
            className={`h-6 px-2 rounded text-[10px] font-medium whitespace-nowrap transition-colors ${
              activeFilter === cat.id ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* File List */}
      <div className="flex-1 overflow-y-auto">
        {filtered.map(file => {
          const { icon: Icon, color } = iconMap[file.iconType]
          const isActive = activeFile === file.id
          return (
            <div
              key={file.id}
              onClick={() => setActiveFile(file.id)}
              onContextMenu={(e) => handleContext(e, file.id)}
              className={`h-8 px-3 flex items-center gap-2 cursor-pointer transition-colors ${
                isActive ? 'bg-indigo-50 border-r-2 border-indigo-500' : 'hover:bg-gray-100/80'
              }`}
            >
              <Icon size={14} className={color} />
              <span className={`flex-1 truncate ${isActive ? 'text-indigo-700 font-medium' : 'text-gray-700'}`}>{file.name}</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded-sm ${tagColors[file.category]}`}>{tagLabels[file.category]}</span>
            </div>
          )
        })}
      </div>

      {contextMenu.visible && <ContextMenu ref={menuRef} x={contextMenu.x} y={contextMenu.y} onAction={handleAction} />}
    </div>
  )
}
