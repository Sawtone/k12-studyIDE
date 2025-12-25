import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { useEffect, useState, useRef, useCallback } from 'react'
import { AnimatePresence } from 'framer-motion'
import { WelcomeScreen } from './WelcomeScreen'
import { InspirationBanner } from './InspirationBanner'

// 将文本转换为 HTML
const textToHtml = (text) => {
  if (!text) return '<p></p>'
  const paragraphs = text.split(/\n\n+/)
  return paragraphs.map((p) => `<p>${p.replace(/\n/g, '<br>')}</p>`).join('')
}

// 从编辑器提取文本
const extractText = (editor) => {
  const paragraphs = []
  editor.state.doc.forEach((node) => {
    if (node.type.name === 'paragraph') {
      paragraphs.push(node.textContent)
    }
  })
  return paragraphs.join('\n\n')
}

// 检查是否为空内容
const isEmptyContent = (content) => {
  if (!content) return true
  return content.trim() === ''
}

export const WritingMode = ({ content, onContentChange, sessionId, inspiration, setInspiration }) => {
  // 是否显示欢迎页
  const [showWelcome, setShowWelcome] = useState(false)
  // 记录上一个 sessionId
  const prevSessionIdRef = useRef(null)
  // 标记是否刚切换会话，等待 content 同步
  const pendingWelcomeCheckRef = useRef(false)

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
        placeholder: '在这里开始写作，让想法自由流淌...',
        emptyEditorClass: 'is-editor-empty',
      }),
    ],
    content: content ? textToHtml(content) : '',
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

  // 从外部灵感状态获取数据
  const currentTopic = inspiration?.topic || null
  const currentInspiration = inspiration?.inspiration || null

  // 检查是否应该显示欢迎页
  const checkShowWelcome = useCallback((contentToCheck, inspirationToCheck) => {
    const hasInspiration = inspirationToCheck?.topic && inspirationToCheck?.inspiration
    const isEmpty = isEmptyContent(contentToCheck)
    return isEmpty && !hasInspiration
  }, [])

  // sessionId 变化时标记需要检查欢迎页
  useEffect(() => {
    if (sessionId && sessionId !== prevSessionIdRef.current) {
      prevSessionIdRef.current = sessionId
      // 标记需要在 content 更新后检查
      pendingWelcomeCheckRef.current = true
    }
  }, [sessionId])

  // content 变化时检查是否需要显示欢迎页
  useEffect(() => {
    if (pendingWelcomeCheckRef.current) {
      pendingWelcomeCheckRef.current = false
      const shouldShow = checkShowWelcome(content, inspiration)
      setShowWelcome(shouldShow)
    }
  }, [content, inspiration, checkShowWelcome])

  // 内容变化时更新编辑器
  useEffect(() => {
    if (editor && !editor.isFocused) {
      const currentText = extractText(editor)
      if (currentText !== (content || '')) {
        editor.commands.setContent(content ? textToHtml(content) : '')
      }
    }
  }, [content, editor])

  // 从欢迎页开始写作
  const handleStartWriting = ({ topic, inspiration: newInspiration }) => {
    setShowWelcome(false)

    if (topic && newInspiration) {
      // 保存灵感到外部状态
      setInspiration({ topic, inspiration: newInspiration })
    }

    // 聚焦编辑器
    setTimeout(() => {
      editor?.commands.focus()
    }, 100)
  }

  // 关闭灵感 Banner
  const handleCloseBanner = () => {
    setInspiration(null)
  }

  // 更新灵感内容
  const handleUpdateInspiration = (newInspiration) => {
    if (inspiration) {
      setInspiration({ ...inspiration, inspiration: newInspiration })
    }
  }

  // 判断是否显示 banner
  const shouldShowBanner = currentTopic && currentInspiration

  // 显示欢迎页
  if (showWelcome) {
    return <WelcomeScreen sessionId={sessionId} onStartWriting={handleStartWriting} />
  }

  return (
    <div
      className="h-full overflow-auto"
      style={{
        backgroundColor: '#fdfbf7',
        backgroundImage: 'radial-gradient(circle, #e5e7eb 1px, transparent 1px)',
        backgroundSize: '24px 24px',
      }}
    >
      {/* 灵感 Banner */}
      <AnimatePresence>
        {shouldShowBanner && (
          <InspirationBanner
            topic={currentTopic}
            inspiration={currentInspiration}
            sessionId={sessionId}
            onClose={handleCloseBanner}
            onUpdate={handleUpdateInspiration}
          />
        )}
      </AnimatePresence>

      {/* 编辑器 */}
      <div className="max-w-3xl mx-auto py-8 px-8">
        <EditorContent editor={editor} />
      </div>
    </div>
  )
}
