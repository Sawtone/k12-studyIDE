import React, { useState } from 'react'
import { FileText, Circle, ChevronRight, ChevronDown, BookOpen } from 'lucide-react'

// AST节点类型
const ASTNode = ({ node, level = 0, onNodeClick, isLast = false }) => {
  const [isExpanded, setIsExpanded] = useState(true) // 默认展开
  
  const handleClick = (e) => {
    e.stopPropagation()
    if (onNodeClick && node.text) {
      console.log('🌳 AST node clicked:', node.text)
      onNodeClick(node.text)
    } else if (onNodeClick && node.type === 'sentence' && node.label) {
      console.log('🌳 AST node clicked (using label):', node.label)
      onNodeClick(node.label)
    }
  }
  
  const handleToggleExpand = (e) => {
    e.stopPropagation()
    setIsExpanded(!isExpanded)
  }
  
  const isClickable = node.text || (node.type === 'sentence' && node.label)
  const hasChildren = node.children && node.children.length > 0
  
  // 根据节点类型设置样式
  const getNodeStyle = () => {
    if (node.type === 'paragraph') {
      return {
        container: 'bg-indigo-50/40 hover:bg-indigo-50/60',
        icon: 'text-indigo-600',
        iconBg: 'bg-indigo-100/80'
      }
    } else if (node.type === 'sentence') {
      return {
        container: isClickable 
          ? 'hover:bg-gray-100/60' 
          : '',
        icon: 'text-gray-400',
        iconBg: 'bg-gray-200/60'
      }
    }
    return {
      container: '',
      icon: 'text-gray-400',
      iconBg: 'bg-gray-100'
    }
  }
  
  const style = getNodeStyle()
  
  return (
    <div className="relative">
      <div 
        className={`group relative transition-all duration-150 ${
          isClickable ? 'cursor-pointer' : ''
        }`}
        onClick={handleClick}
      >
        <div 
          className={`flex items-center gap-1 py-0.5 px-1.5 rounded transition-all duration-150 ${
            style.container
          } ${isClickable ? 'hover:bg-indigo-50/80' : ''}`}
        >
          {/* 展开/折叠按钮 */}
          {hasChildren && (
            <button
              onClick={handleToggleExpand}
              className="flex-shrink-0 w-3.5 h-3.5 flex items-center justify-center hover:bg-indigo-100/60 rounded transition-colors -ml-0.5"
            >
              {isExpanded ? (
                <ChevronDown size={9} className="text-gray-500" />
              ) : (
                <ChevronRight size={9} className="text-gray-500" />
              )}
            </button>
          )}
          
          {/* 图标 */}
          <div className={`flex-shrink-0 w-3.5 h-3.5 rounded flex items-center justify-center ${style.iconBg} transition-colors`}>
            {node.type === 'paragraph' ? (
              <FileText size={9} className={style.icon} />
            ) : node.type === 'sentence' ? (
              <Circle size={5} className={style.icon} fill="currentColor" />
            ) : null}
          </div>
          
          {/* 内容区域 */}
          <div className="flex-1 min-w-0 flex items-center gap-1.5">
            <div className={`text-[10px] font-medium truncate ${
              node.type === 'paragraph' ? 'text-gray-800' :
              'text-gray-600'
            }`}>
              {node.label}
            </div>
            
            {node.meta && (
              <div className="text-[9px] text-gray-400 flex-shrink-0">
                {node.meta}
              </div>
            )}
            
            {node.status && (
              <div className={`text-[8px] px-1 py-0.5 rounded flex-shrink-0 ${
                node.status === 'ok' 
                  ? 'bg-emerald-100 text-emerald-700' 
                  : node.status === 'warning'
                  ? 'bg-orange-100 text-orange-700'
                  : 'bg-rose-100 text-rose-700'
              }`}>
                {node.status === 'ok' ? '✓' : node.status === 'warning' ? '⚠' : '✗'}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* 子节点 - 递归展开 */}
      {hasChildren && isExpanded && (
        <div className="ml-3 mt-0.5 space-y-0">
          {node.children.map((child, index) => (
            <ASTNode 
              key={index} 
              node={child} 
              level={level + 1} 
              onNodeClick={onNodeClick}
              isLast={index === node.children.length - 1}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// 从内容提取AST结构（文科模式）
export const extractASTFromContent = (content) => {
  if (!content) {
    return {
      type: 'document',
      label: '文档根节点',
      children: []
    }
  }
  
  // 按双换行分割段落
  const paragraphs = content.split(/\n\n+/).filter(p => p.trim())
  
  const astChildren = paragraphs.map((para, paraIndex) => {
    // 按句子分割（句号、问号、叹号、省略号）
    const sentences = para.split(/(?<=[。！？…])/g).filter(s => s.trim())
    
    return {
      type: 'paragraph',
      label: `段落 ${paraIndex + 1}`,
      meta: `${sentences.length} 句`,
      status: 'ok',
      children: sentences.map((sentence, sentIndex) => ({
        type: 'sentence',
        label: sentence.length > 30 ? sentence.substring(0, 30) + '...' : sentence,
        text: sentence, // 保存完整文本用于高亮
        status: 'ok'
      }))
    }
  })
  
  return {
    type: 'document',
    label: '文档根节点',
    children: astChildren
  }
}

export const AST = ({ astData, content, onNodeClick }) => {
  // 如果没有astData但有content，从content提取
  let data = astData
  if (!data && content) {
    data = extractASTFromContent(content)
  }
  
  // 如果还是没有，显示默认结构
  if (!data) {
    data = {
      type: 'document',
      label: '文档根节点',
      children: [
        {
          type: 'paragraph',
          label: '段落 1',
          meta: '3 句',
          status: 'ok',
          children: [
            { type: 'sentence', label: '人工智能正在改变世界。', text: '人工智能正在改变世界。', status: 'ok' },
            { type: 'sentence', label: '它帮助我们更快地学习新知识。', text: '它帮助我们更快地学习新知识。', status: 'ok' },
          ]
        },
        {
          type: 'paragraph',
          label: '段落 2',
          meta: '1 句',
          status: 'warning',
          children: [
            { type: 'sentence', label: '然而，我们必须谨慎对待它的发展。', text: '然而，我们必须谨慎对待它的发展。', status: 'warning' },
          ]
        }
      ]
    }
  }
  
  // 如果根节点有子节点，直接显示子节点（段落），不显示根节点
  const displayNodes = data.children && data.children.length > 0 ? data.children : []
  
  return (
    <div className="space-y-0.5">
      {displayNodes.length > 0 ? (
        displayNodes.map((child, index) => (
          <ASTNode 
            key={index} 
            node={child} 
            level={0} 
            onNodeClick={onNodeClick}
            isLast={index === displayNodes.length - 1}
          />
        ))
      ) : (
        <div className="text-center py-6 text-gray-400">
          <BookOpen size={16} className="mx-auto mb-1 text-gray-300 opacity-50" />
          <div className="text-[10px]">暂无内容结构</div>
        </div>
      )}
    </div>
  )
}

