import { NodeViewWrapper, NodeViewContent } from '@tiptap/react'

export const BlockNodeView = ({ node, editor, getPos }) => {
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
      className="cognitive-block grid grid-cols-[40px_1fr] gap-2 items-start relative group py-0.5"
      data-line={lineNumber}
    >
      {/* Left Column - Line Number */}
      <div className="gutter-column flex items-center justify-end min-h-[1.5rem] pr-2" contentEditable={false}>
        <span className="text-[11px] font-mono text-gray-300 group-hover:text-gray-400 transition-colors select-none">
          {lineNumber}
        </span>
      </div>

      {/* Right Column - Content */}
      <div className="content-column relative rounded-md px-3 py-1.5 transition-all duration-150 hover:bg-white/50 border border-transparent">
        <NodeViewContent
          as="div"
          className="font-serif text-[15px] text-gray-700 leading-relaxed outline-none"
        />
      </div>
    </NodeViewWrapper>
  )
}
