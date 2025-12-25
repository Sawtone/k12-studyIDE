import { Node, mergeAttributes } from '@tiptap/core'
import { ReactNodeViewRenderer } from '@tiptap/react'
import { BlockNodeView } from '../components/BlockNodeView.jsx'

export const CognitiveParagraph = Node.create({
  name: 'cognitiveParagraph',
  group: 'block',
  content: 'inline*',

  addAttributes() {
    return {
      uuid: {
        default: null,
        parseHTML: (element) => element.getAttribute('data-uuid'),
        renderHTML: (attributes) => {
          if (!attributes.uuid) return {}
          return { 'data-uuid': attributes.uuid }
        },
      },
    }
  },

  parseHTML() {
    return [{ tag: 'p' }]
  },

  renderHTML({ HTMLAttributes }) {
    return ['p', mergeAttributes(HTMLAttributes), 0]
  },

  addNodeView() {
    return ReactNodeViewRenderer(BlockNodeView)
  },
})
