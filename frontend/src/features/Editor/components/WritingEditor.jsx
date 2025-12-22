import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { useEffect } from 'react'

export const WritingEditor = ({ content, onChange }) => {
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
    content: content ? `<p>${content}</p>` : '',
    editorProps: {
      attributes: {
        class: 'writing-editor outline-none h-full font-serif text-lg text-gray-700 leading-relaxed',
      },
    },
    onUpdate: ({ editor }) => {
      onChange(editor.getText())
    },
  })

  useEffect(() => {
    if (editor && !editor.isFocused) {
      const currentText = editor.getText()
      if (currentText !== content) {
        editor.commands.setContent(content ? `<p>${content}</p>` : '')
      }
    }
  }, [content, editor])

  return (
    <div 
      className="h-full p-8 overflow-auto"
      style={{
        backgroundColor: '#fdfbf7',
        backgroundImage: 'radial-gradient(#e5e7eb 1px, transparent 1px)',
        backgroundSize: '20px 20px',
      }}
    >
      <EditorContent editor={editor} className="tiptap-writing h-full" />
    </div>
  )
}
