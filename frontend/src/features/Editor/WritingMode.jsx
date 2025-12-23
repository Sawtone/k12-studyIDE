import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { useEffect } from 'react'

// 将文本转换为 HTML，双换行表示新段落
const textToHtml = (text) => {
  if (!text) return '<p></p>'
  // 按双换行分割段落
  const paragraphs = text.split(/\n\n+/)
  return paragraphs.map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`).join('')
}

// 从编辑器提取文本，保留段落结构
const extractText = (editor) => {
  const paragraphs = []
  editor.state.doc.forEach((node) => {
    if (node.type.name === 'paragraph') {
      paragraphs.push(node.textContent)
    }
  })
  return paragraphs.join('\n\n')
}

export const WritingMode = ({ content, onContentChange }) => {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: false,
        bulletList: false,
        orderedList: false,
        listItem: false,
        blockquote: false,
        codeBlock: false,
        horizontalRule: false,
      }),
      Placeholder.configure({
        placeholder: '开始写作...',
        emptyEditorClass: 'is-editor-empty',
      }),
    ],
    content: textToHtml(content),
    editorProps: {
      attributes: {
        class: 'writing-editor outline-none min-h-full',
      },
    },
    onUpdate: ({ editor }) => {
      const text = extractText(editor)
      onContentChange(text)
    },
  })

  useEffect(() => {
    if (editor && !editor.isFocused) {
      const currentText = extractText(editor)
      if (currentText !== content) {
        editor.commands.setContent(textToHtml(content))
      }
    }
  }, [content, editor])

  return (
    <div 
      className="h-full overflow-auto"
      style={{
        backgroundColor: '#fdfbf7',
        backgroundImage: 'radial-gradient(circle, #e5e7eb 1px, transparent 1px)',
        backgroundSize: '24px 24px',
      }}
    >
      <div className="max-w-3xl mx-auto py-12 px-8">
        <EditorContent editor={editor} />
      </div>
    </div>
  )
}
