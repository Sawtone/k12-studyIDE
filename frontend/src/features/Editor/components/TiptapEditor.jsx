import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { useEffect, useCallback } from 'react'
import { LineNumberParagraph } from '../extensions/LineNumberParagraph'

export const TiptapEditor = ({ content, onChange, isIDEMode }) => {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        paragraph: false,
        heading: false,
        bulletList: false,
        orderedList: false,
        listItem: false,
        blockquote: false,
        codeBlock: false,
        horizontalRule: false,
      }),
      LineNumberParagraph,
      Placeholder.configure({
        placeholder: '继续写作...',
        emptyEditorClass: 'is-editor-empty',
      }),
    ],
    content: convertToTiptapContent(content),
    editorProps: {
      attributes: {
        class: 'ide-editor outline-none h-full',
      },
    },
    onUpdate: ({ editor }) => {
      const text = extractTextFromEditor(editor)
      onChange(text)
    },
  })

  useEffect(() => {
    if (editor && !editor.isFocused) {
      const currentText = extractTextFromEditor(editor)
      if (currentText !== content) {
        editor.commands.setContent(convertToTiptapContent(content))
      }
    }
  }, [content, editor])

  return (
    <div className="h-full bg-gradient-to-b from-gray-50 to-gray-100/50 overflow-auto">
      <div className="py-4 px-2">
        <EditorContent editor={editor} className="tiptap-ide" />
      </div>
    </div>
  )
}

function convertToTiptapContent(text) {
  if (!text) return '<p></p>'
  
  const sentences = text.split(/(?<=[。！？])/g).filter(s => s.trim())
  
  if (sentences.length === 0) return '<p></p>'
  
  return sentences.map(s => `<p>${s.trim()}</p>`).join('')
}

function extractTextFromEditor(editor) {
  const doc = editor.state.doc
  const texts = []
  
  doc.forEach(node => {
    if (node.type.name === 'lineNumberParagraph') {
      texts.push(node.textContent)
    }
  })
  
  return texts.join('')
}
