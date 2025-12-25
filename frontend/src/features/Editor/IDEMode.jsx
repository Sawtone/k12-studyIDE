import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { CognitiveParagraph } from './extensions/CognitiveParagraph.jsx'
import { ParagraphDivider } from './extensions/ParagraphDivider.jsx'
import { useEffect } from 'react'

// 将文本按段落和句子分割转换为 HTML
const textToSentenceHtml = (text) => {
  if (!text) return '<p></p>'

  // 先按双换行分割段落
  const paragraphs = text.split(/\n\n+/)

  const htmlParts = []

  paragraphs.forEach((para, paraIndex) => {
    // 每个段落内按句子分割
    const sentences = para.split(/(?<=[。！？])/g).filter((s) => s.trim())

    if (sentences.length > 0) {
      sentences.forEach((s) => {
        htmlParts.push(`<p>${s.trim()}</p>`)
      })
    }

    // 段落之间添加分隔符（最后一个段落后不加）
    if (paraIndex < paragraphs.length - 1) {
      htmlParts.push('<hr data-type="paragraph-divider">')
    }
  })

  return htmlParts.length > 0 ? htmlParts.join('') : '<p></p>'
}

// 检测文本是否主要是英文
const isEnglishText = (text) => {
  // 移除空格和标点后统计字符
  const cleanText = text.replace(/[\s\p{P}]/gu, '')
  if (!cleanText) return false
  
  // 统计英文字母数量
  const englishChars = (cleanText.match(/[a-zA-Z]/g) || []).length
  // 如果英文字母占比超过50%，认为是英文
  return englishChars / cleanText.length > 0.5
}

// 从编辑器提取文本，保留段落结构
// 空行（空的段落节点）视为段落分隔
const extractTextFromEditor = (editor) => {
  const parts = []
  let currentParagraph = []

  editor.state.doc.forEach((node) => {
    if (node.type.name === 'cognitiveParagraph') {
      const text = node.textContent.trim()
      if (text) {
        let sentence = text
        // 如果句子不以标点结尾，根据语言自动添加句号
        if (!/[。！？.!?]$/.test(sentence)) {
          sentence += isEnglishText(sentence) ? '.' : '。'
        }
        currentParagraph.push(sentence)
      } else {
        // 空行视为段落分隔
        if (currentParagraph.length > 0) {
          parts.push(currentParagraph.join(''))
          currentParagraph = []
        }
      }
    } else if (node.type.name === 'paragraphDivider') {
      // 遇到分隔符，保存当前段落并开始新段落
      if (currentParagraph.length > 0) {
        parts.push(currentParagraph.join(''))
        currentParagraph = []
      }
    }
  })

  // 保存最后一个段落
  if (currentParagraph.length > 0) {
    parts.push(currentParagraph.join(''))
  }

  return parts.join('\n\n')
}

export const IDEMode = ({ content, onContentChange }) => {
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
      CognitiveParagraph,
      ParagraphDivider,
      Placeholder.configure({
        placeholder: '开始写作，每句话一行，空行分段...',
        emptyEditorClass: 'is-editor-empty',
      }),
    ],
    content: textToSentenceHtml(content),
    editorProps: {
      attributes: {
        class: 'ide-editor-content outline-none min-h-[400px] py-6 px-4',
      },
    },
    onUpdate: ({ editor }) => {
      const text = extractTextFromEditor(editor)
      onContentChange(text)
    },
  })

  // 当 content 从外部变化时同步
  useEffect(() => {
    if (editor && !editor.isFocused) {
      const currentTexts = []
      editor.state.doc.descendants((node) => {
        if (node.type.name === 'cognitiveParagraph' && node.textContent.trim()) {
          currentTexts.push(node.textContent.trim())
        }
      })
      const currentContent = currentTexts.join('')

      if (currentContent !== content) {
        editor.commands.setContent(textToSentenceHtml(content))
      }
    }
  }, [content, editor])

  return (
    <div className="ide-mode-container h-full flex flex-col">
      {/* Editor Canvas */}
      <div
        className="ide-canvas flex-1 overflow-auto"
        style={{
          backgroundColor: '#f8fafc',
        }}
      >
        <div className="py-4">
          <EditorContent editor={editor} />
        </div>
      </div>
    </div>
  )
}
