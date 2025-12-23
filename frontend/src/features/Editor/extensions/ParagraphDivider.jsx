import { Node } from '@tiptap/core'
import { ReactNodeViewRenderer, NodeViewWrapper } from '@tiptap/react'
import { CornerDownLeft } from 'lucide-react'
import { useState } from 'react'

const ParagraphDividerView = ({ editor, getPos }) => {
  const [isHovered, setIsHovered] = useState(false)

  // 计算当前是第几个段落分隔符（即下一段是第几段）
  let paragraphNumber = 2 // 默认从第2段开始
  const pos = getPos()
  if (typeof pos === 'number') {
    let dividerCount = 0
    editor.state.doc.nodesBetween(0, pos, (node) => {
      if (node.type.name === 'paragraphDivider') {
        dividerCount++
      }
    })
    paragraphNumber = dividerCount + 2
  }

  return (
    <NodeViewWrapper 
      className="paragraph-divider grid grid-cols-[100px_1fr] gap-2 items-center py-2 cursor-default select-none group"
      contentEditable={false}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Left Gutter - Boundary Marker */}
      <div className="flex items-center justify-end pr-3">
        <span className="text-[10px] text-gray-200 font-light">•</span>
      </div>
      
      {/* Right Column - The Soft Link */}
      <div className="flex items-center justify-center px-4">
        {/* Left Dashed Connector */}
        <div 
          className={`
            flex-1 max-w-[30%] h-0 
            border-t transition-all duration-200
            ${isHovered 
              ? 'border-solid border-indigo-200' 
              : 'border-dashed border-indigo-100/60'
            }
          `}
        />
        
        {/* Central Badge */}
        <div className="relative mx-3">
          <div 
            className={`
              w-6 h-6 flex items-center justify-center
              rounded-full bg-white border
              transition-all duration-200
              ${isHovered 
                ? 'border-indigo-200 shadow-md' 
                : 'border-indigo-100 shadow-sm'
              }
            `}
          >
            <CornerDownLeft 
              size={11} 
              className={`transition-colors duration-200 ${
                isHovered ? 'text-indigo-500' : 'text-indigo-300'
              }`}
            />
          </div>
          
          {/* Hover Tooltip */}
          {isHovered && (
            <div className="absolute left-1/2 -translate-x-1/2 top-full mt-1.5 whitespace-nowrap">
              <span className="text-[9px] text-indigo-400 font-medium bg-indigo-50/80 px-1.5 py-0.5 rounded">
                当前为第 {paragraphNumber} 段
              </span>
            </div>
          )}
        </div>
        
        {/* Right Dashed Connector */}
        <div 
          className={`
            flex-1 max-w-[30%] h-0 
            border-t transition-all duration-200
            ${isHovered 
              ? 'border-solid border-indigo-200' 
              : 'border-dashed border-indigo-100/60'
            }
          `}
        />
      </div>
    </NodeViewWrapper>
  )
}

export const ParagraphDivider = Node.create({
  name: 'paragraphDivider',
  group: 'block',
  atom: true,
  
  parseHTML() {
    return [{ tag: 'hr[data-type="paragraph-divider"]' }]
  },
  
  renderHTML() {
    return ['hr', { 'data-type': 'paragraph-divider' }]
  },
  
  addNodeView() {
    return ReactNodeViewRenderer(ParagraphDividerView)
  },
})
