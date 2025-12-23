import { NodeViewWrapper, NodeViewContent } from '@tiptap/react'
import { Lightbulb, FileText, AlertTriangle } from 'lucide-react'
import { LABEL_CONFIG } from '../types.js'

const IconMap = {
  Lightbulb,
  FileText,
  AlertTriangle,
}

export const BlockNodeView = ({ node, editor, getPos }) => {
  const { aiLabel } = node.attrs
  
  const labelConfig = aiLabel ? LABEL_CONFIG[aiLabel] : null
  const IconComponent = labelConfig ? IconMap[labelConfig.icon] : null

  let lineNumber = 1
  const pos = getPos()
  if (typeof pos === 'number') {
    editor.state.doc.nodesBetween(0, pos, (n) => {
      if (n.type.name === 'cognitiveParagraph') {
        lineNumber++
      }
    })
    lineNumber--
  }

  return (
    <NodeViewWrapper 
      className="cognitive-block grid grid-cols-[100px_1fr] gap-2 items-start relative group py-0.5"
      data-line={lineNumber}
    >
      {/* Left Column - Gutter */}
      <div 
        className="gutter-column flex items-center min-h-[1.5rem] pr-1"
        contentEditable={false}
      >
        {/* 行号 */}
        <div className="w-5 flex-shrink-0 text-right mr-1.5">
          <span className="text-[10px] font-mono text-gray-300 group-hover:text-gray-400 transition-colors select-none">
            {lineNumber}
          </span>
        </div>

        {/* 标签区域 */}
        <div className="flex-1 flex justify-end">
          {labelConfig && IconComponent && (
            <div 
              className={`
                inline-flex items-center gap-1 px-1.5 py-0.5 
                rounded text-[10px] font-medium border
                cursor-default select-none transition-all duration-150
                ${labelConfig.className}
              `}
            >
              <IconComponent size={10} className="flex-shrink-0" />
              <span>{labelConfig.label}</span>
            </div>
          )}

          {/* 空状态占位 */}
          {!labelConfig && (
            <div className="w-[60px] h-5 opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="h-full rounded border border-dashed border-gray-200/50 flex items-center justify-center">
                <span className="text-[9px] text-gray-300">待分析</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right Column - Content */}
      <div 
        className={`
          content-column relative rounded-md px-3 py-1.5 transition-all duration-150
          ${aiLabel 
            ? 'bg-white/70 border border-gray-100/80 shadow-sm' 
            : 'hover:bg-white/50 border border-transparent'
          }
        `}
      >
        <NodeViewContent 
          as="div"
          className="font-serif text-[15px] text-gray-700 leading-relaxed outline-none"
        />
        
        {aiLabel && (
          <div 
            className={`
              absolute left-0 top-1.5 bottom-1.5 w-[2px] rounded-full
              ${aiLabel === 'topic' ? 'bg-emerald-400' :
                aiLabel === 'evidence' ? 'bg-sky-400' : 'bg-rose-400'}
            `}
          />
        )}
      </div>
    </NodeViewWrapper>
  )
}
