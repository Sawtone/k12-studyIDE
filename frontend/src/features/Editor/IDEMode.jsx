import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { CognitiveParagraph } from './extensions/CognitiveParagraph.jsx'
import { ParagraphDivider } from './extensions/ParagraphDivider.jsx'
import { useMockAnalysis } from './hooks/useMockAnalysis.js'
import { Sparkles, RotateCcw, Loader2 } from 'lucide-react'
import { useEffect } from 'react'

// 将文本按段落和句子分割转换为 HTML
const textToSentenceHtml = (text) => {
  if (!text) return '<p></p>'
  
  // 先按双换行分割段落
  const paragraphs = text.split(/\n\n+/)
  
  const htmlParts = []
  
  paragraphs.forEach((para, paraIndex) => {
    // 每个段落内按句子分割
    const sentences = para.split(/(?<=[。！？])/g).filter(s => s.trim())
    
    if (sentences.length > 0) {
      sentences.forEach(s => {
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
        // 如果句子不以中文标点结尾，自动添加句号
        if (!/[。！？]$/.test(sentence)) {
          sentence += '。'
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
        placeholder: '开始写作，让 AI 帮你分析文章结构...',
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

  const { isAnalyzing, hasAnalyzed, runAnalysis, clearAnalysis } = useMockAnalysis(editor)

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
      {/* Toolbar */}
      <div className="ide-toolbar flex items-center justify-end gap-2 px-4 py-2 border-b border-gray-100 bg-gray-50/50">
        {hasAnalyzed && (
          <button
            onClick={clearAnalysis}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-all"
          >
            <RotateCcw size={12} />
            <span>清除标注</span>
          </button>
        )}
        
        <button
          onClick={runAnalysis}
          disabled={isAnalyzing}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${
            isAnalyzing 
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
              : 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white hover:shadow-md'
          }`}
        >
          {isAnalyzing ? (
            <>
              <Loader2 size={12} className="animate-spin" />
              <span>分析中...</span>
            </>
          ) : (
            <>
              <Sparkles size={12} />
              <span>AI 结构分析</span>
            </>
          )}
        </button>
      </div>

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
