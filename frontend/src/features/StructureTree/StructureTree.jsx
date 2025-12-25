import { useState, useEffect, useRef } from 'react'
import { ChevronRight, ChevronDown, FileText, AlignLeft, Type, RefreshCw, Loader2 } from 'lucide-react'
import { getStructure, analyzeStructure } from '../../api/literatureApi'

// 根据节点类型获取图标和颜色
const getNodeStyle = (type) => {
  switch (type) {
    case 'root':
      return { icon: FileText, color: 'text-indigo-500', bg: 'bg-indigo-50', border: 'border-indigo-100' }
    case 'paragraph':
      return { icon: AlignLeft, color: 'text-emerald-500', bg: 'bg-emerald-50', border: 'border-emerald-100' }
    case 'sentence':
      return { icon: Type, color: 'text-amber-500', bg: 'bg-amber-50', border: 'border-amber-100' }
    default:
      return { icon: FileText, color: 'text-gray-500', bg: 'bg-gray-50', border: 'border-gray-100' }
  }
}

// 树节点组件
const TreeNode = ({ node, level = 0 }) => {
  const [expanded, setExpanded] = useState(level < 2) // 默认展开前两层
  const [textExpanded, setTextExpanded] = useState(false) // 文字展开状态
  const [isOverflowing, setIsOverflowing] = useState(false) // 是否溢出
  const titleRef = useRef(null)
  const summaryRef = useRef(null)
  const hasChildren = node.children && node.children.length > 0
  const style = getNodeStyle(node.type)
  const Icon = style.icon

  // 检测文字是否溢出
  useEffect(() => {
    const checkOverflow = () => {
      const titleEl = titleRef.current
      const summaryEl = summaryRef.current
      const titleOverflow = titleEl && titleEl.scrollWidth > titleEl.clientWidth
      const summaryOverflow = summaryEl && summaryEl.scrollHeight > summaryEl.clientHeight
      setIsOverflowing(titleOverflow || summaryOverflow)
    }
    checkOverflow()
    window.addEventListener('resize', checkOverflow)
    return () => window.removeEventListener('resize', checkOverflow)
  }, [node.title, node.summary])

  return (
    <div className="select-none">
      <div
        className={`flex items-start gap-2 py-1.5 px-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors`}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={() => hasChildren && setExpanded(!expanded)}
      >
        {/* 展开/收起图标 */}
        <div className="w-4 h-4 flex items-center justify-center flex-shrink-0 mt-0.5">
          {hasChildren ? (
            expanded ? (
              <ChevronDown size={12} className="text-gray-400" />
            ) : (
              <ChevronRight size={12} className="text-gray-400" />
            )
          ) : (
            <div className="w-1 h-1 rounded-full bg-gray-300" />
          )}
        </div>

        {/* 节点图标 */}
        <div className={`p-1 rounded ${style.bg} flex-shrink-0`}>
          <Icon size={12} className={style.color} />
        </div>

        {/* 节点内容 */}
        <div className="flex-1 min-w-0">
          <div
            ref={titleRef}
            className={`text-xs font-medium text-gray-700 ${textExpanded ? 'whitespace-normal break-words' : 'truncate'}`}
          >
            {node.title}
          </div>
          {node.summary && (
            <div
              ref={summaryRef}
              className={`text-[10px] text-gray-500 mt-0.5 ${textExpanded ? 'whitespace-normal break-words' : 'line-clamp-2'}`}
            >
              {node.summary}
            </div>
          )}
          {/* 展开/收起文字按钮 - 只在实际溢出时显示 */}
          {(isOverflowing || textExpanded) && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                setTextExpanded(!textExpanded)
              }}
              className="text-[9px] text-indigo-500 hover:text-indigo-600 mt-0.5"
            >
              {textExpanded ? '收起' : '展开全文'}
            </button>
          )}
        </div>
      </div>

      {/* 子节点 */}
      {hasChildren && expanded && (
        <div className="relative">
          {/* 连接线 */}
          <div
            className="absolute left-0 top-0 bottom-0 w-px bg-gray-200"
            style={{ left: `${level * 12 + 16}px` }}
          />
          {node.children.map((child, index) => (
            <TreeNode key={child.id || index} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  )
}


export const StructureTree = ({ sessionId, content }) => {
  const [structure, setStructure] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // 获取缓存的结构
  const fetchStructure = async () => {
    if (!sessionId) return
    setLoading(true)
    setError(null)
    try {
      const result = await getStructure(sessionId)
      setStructure(result)
    } catch (err) {
      // 如果没有缓存，显示空状态
      setStructure(null)
    } finally {
      setLoading(false)
    }
  }

  // 重新分析结构
  const handleAnalyze = async () => {
    if (!sessionId || !content) return
    setLoading(true)
    setError(null)
    try {
      const result = await analyzeStructure({ session_id: sessionId, content })
      setStructure(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStructure()
  }, [sessionId])

  // 内容变化时清空结构（提示用户重新分析）
  useEffect(() => {
    // 不清空，但可以显示提示
  }, [content])

  // 从 API 响应中提取树结构
  const tree = structure?.tree

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-gray-400">
        <Loader2 size={20} className="animate-spin mb-2" />
        <span className="text-xs">分析中...</span>
      </div>
    )
  }

  if (!sessionId) {
    return <div className="text-center py-8 text-gray-400 text-xs">请先选择一个会话</div>
  }

  return (
    <div>
      {/* 头部信息 */}
      {structure && (
        <div className="mb-3 p-2.5 bg-gradient-to-r from-indigo-50 to-white rounded-lg border border-indigo-100">
          {structure.structure_type && (
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] px-1.5 py-0.5 bg-indigo-100 text-indigo-600 rounded-full font-medium">
                {structure.structure_type}
              </span>
            </div>
          )}
          {structure.overall_pattern && (
            <p className="text-[11px] text-gray-600 leading-relaxed">{structure.overall_pattern}</p>
          )}
        </div>
      )}

      {/* 操作按钮 */}
      <div className="flex justify-between items-center mb-3">
        <span className="text-[10px] text-gray-400">
          {tree ? '点击节点展开/收起' : ''}
        </span>
        <button
          onClick={handleAnalyze}
          disabled={loading || !content}
          className="flex items-center gap-1 px-2 py-1 text-[10px] text-indigo-600 hover:bg-indigo-50 rounded transition-colors disabled:opacity-50"
        >
          <RefreshCw size={10} />
          {tree ? '重新分析' : '开始分析'}
        </button>
      </div>

      {error && <div className="mb-3 p-2 bg-red-50 text-red-600 text-xs rounded-lg">{error}</div>}

      {/* 树形结构 */}
      {tree ? (
        <div className="border border-gray-100 rounded-lg overflow-hidden">
          <TreeNode node={tree} level={0} />
        </div>
      ) : (
        <div className="text-center py-8">
          <FileText size={32} className="mx-auto mb-2 text-gray-300" />
          <p className="text-gray-400 text-xs mb-3">暂无结构分析</p>
          <p className="text-[10px] text-gray-400">点击上方按钮开始分析文章结构</p>
        </div>
      )}

      {/* 关系说明 */}
      {structure?.relationships && structure.relationships.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="text-[10px] text-gray-500 mb-2">段落关系</div>
          <div className="flex flex-wrap gap-1">
            {structure.relationships.slice(0, 5).map((rel, i) => (
              <span
                key={i}
                className="text-[9px] px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded"
              >
                {rel.from} → {rel.to}: {rel.relation}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
