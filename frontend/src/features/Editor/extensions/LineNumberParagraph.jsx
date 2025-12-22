import { Node, mergeAttributes } from '@tiptap/core'
import { ReactNodeViewRenderer, NodeViewWrapper, NodeViewContent } from '@tiptap/react'

const LineNumberParagraphView = ({ node, getPos, editor }) => {
  const pos = getPos()
  let lineNumber = 1
  
  if (typeof pos === 'number') {
    editor.state.doc.nodesBetween(0, pos, (n, p) => {
      if (n.type.name === 'lineNumberParagraph' && p < pos) {
        lineNumber++
      }
    })
  }

  const tag = getTagForLine(lineNumber)

  return (
    <NodeViewWrapper 
      className="line-row group flex items-start transition-all duration-150"
      data-line={lineNumber}
    >
      <div 
        className="line-gutter flex-shrink-0 w-12 pr-3 text-right select-none"
        contentEditable={false}
      >
        <span className="text-gray-400 text-sm font-mono leading-7">
          {lineNumber}
        </span>
      </div>
      
      <div className="line-content flex-1 flex items-center gap-2 py-1 px-3 rounded-lg border border-transparent group-hover:bg-white group-hover:border-gray-200/80 group-hover:shadow-sm transition-all duration-150">
        {tag && (
          <span 
            className={`flex-shrink-0 px-2 py-0.5 text-xs font-medium rounded-md border ${tag.className}`}
            contentEditable={false}
          >
            {tag.label}
          </span>
        )}
        <NodeViewContent 
          as="span" 
          className="flex-1 font-mono text-sm text-gray-700 leading-7 outline-none"
        />
      </div>
    </NodeViewWrapper>
  )
}

function getTagForLine(lineNumber) {
  const tags = {
    1: { label: '主题句', className: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
    2: { label: '论据', className: 'bg-amber-50 text-amber-700 border-amber-200' },
    3: { label: '⚠️ 过渡', className: 'bg-rose-50 text-rose-700 border-rose-200' },
  }
  return tags[lineNumber] || null
}

export const LineNumberParagraph = Node.create({
  name: 'lineNumberParagraph',
  group: 'block',
  content: 'inline*',
  
  parseHTML() {
    return [{ tag: 'p' }]
  },
  
  renderHTML({ HTMLAttributes }) {
    return ['p', mergeAttributes(HTMLAttributes), 0]
  },
  
  addNodeView() {
    return ReactNodeViewRenderer(LineNumberParagraphView)
  },
})
