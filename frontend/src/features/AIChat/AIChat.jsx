import { useState, useRef, useEffect } from 'react'
import { Send, Sparkles, User, Loader2, Trash2, BookOpen } from 'lucide-react'
import { sendChatMessage } from '../../api/chatApi'

export const AIChat = ({ sessionId, editorContent }) => {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      content: '你好！我是小小思 ✨\n\n我可以帮你润色文章、提供写作建议、解答问题。有什么需要帮忙的吗？'
    }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    const trimmedInput = input.trim()
    if (!trimmedInput || isLoading) return

    const userMessage = { role: 'user', content: trimmedInput }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      let messageToSend = trimmedInput

      // 判断是否需要关联编辑器内容
      if (editorContent && editorContent.trim()) {
        // 强关联关键词：直接针对文章内容操作
        const strongKeywords = [
          '润色', '修改', '改写', '检查', '语法', '错误', '问题',
          '这段', '这篇', '文章', '内容', '帮我看', '帮我改',
          '优化', '改进', '提升', '纠正', '修正'
        ]
        // 弱关联关键词：可以参考文章举例
        const weakKeywords = ['建议', '怎么写', '如何', '技巧', '方法']

        const hasStrongKeyword = strongKeywords.some((k) => trimmedInput.includes(k))
        const hasWeakKeyword = weakKeywords.some((k) => trimmedInput.includes(k))

        if (hasStrongKeyword) {
          // 强关联：完整附带编辑器内容
          messageToSend = `请针对以下文章内容回答问题。

【当前编辑的文章】
${editorContent}

【用户问题】
${trimmedInput}`
        } else if (hasWeakKeyword) {
          // 弱关联：简要提及有文章，可以举例参考
          messageToSend = `用户正在写一篇文章，内容大致是：
"${editorContent.slice(0, 150)}${editorContent.length > 150 ? '...' : ''}"

用户的问题是：${trimmedInput}

请给出写作建议，可以结合用户文章中的具体例子来说明。`
        }
      }

      const response = await sendChatMessage({
        session_id: sessionId || 'default',
        message: messageToSend
      })

      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content: response.content || response.reply || response.message || '抱歉，我暂时无法回答这个问题。',
          actionItems: response.action_items
        }
      ])
    } catch (error) {
      console.error('Chat error:', error)
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content: '网络出现问题，请稍后再试 🙏',
          isError: true
        }
      ])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleClear = () => {
    setMessages([
      {
        role: 'ai',
        content: '对话已清空，有什么新问题吗？ 😊'
      }
    ])
  }

  const quickQuestions = ['帮我润色这篇文章', '检查语法错误', '给我写作建议']

  return (
    <div className="flex flex-col h-full">
      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-3 scrollbar-thin">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}

        {isLoading && (
          <div className="flex items-start gap-2">
            <div
              className="w-5 h-5 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 
                          flex items-center justify-center flex-shrink-0"
            >
              <Sparkles size={10} className="text-white" />
            </div>
            <div className="bg-gray-50 border border-gray-100 rounded-2xl rounded-tl-sm px-3 py-2">
              <div className="flex items-center gap-1.5 text-gray-400">
                <Loader2 size={12} className="animate-spin" />
                <span className="text-xs">思考中...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 快捷提问 */}
      {messages.length <= 2 && !isLoading && (
        <div className="px-3 pb-2">
          <div className="flex flex-wrap gap-1">
            {quickQuestions.map((q, i) => (
              <button
                key={i}
                onClick={() => setInput(q)}
                className="px-2 py-0.5 text-[10px] bg-indigo-50 text-indigo-600 
                         rounded-full hover:bg-indigo-100 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 输入区域 */}
      <div className="px-3 pb-3 pt-2 border-t border-gray-100">
        <div className="flex items-end gap-1.5">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入问题..."
            rows={1}
            className="flex-1 px-2.5 py-2 text-sm bg-gray-50 border border-gray-200 
                     rounded-lg resize-none overflow-hidden
                     focus:outline-none focus:ring-1 focus:ring-indigo-200 focus:border-indigo-300 
                     focus:bg-white transition-all placeholder:text-gray-400"
            style={{ minHeight: '36px', maxHeight: '80px' }}
            onInput={(e) => {
              e.target.style.height = 'auto'
              e.target.style.height = Math.min(e.target.scrollHeight, 80) + 'px'
            }}
          />

          <div className="flex gap-1">
            {messages.length > 1 && (
              <button
                onClick={handleClear}
                className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 
                         rounded-lg transition-all"
                title="清空对话"
              >
                <Trash2 size={14} />
              </button>
            )}
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="p-2 bg-gradient-to-r from-indigo-500 to-purple-500 text-white 
                       rounded-lg hover:from-indigo-600 hover:to-purple-600 
                       disabled:opacity-50 disabled:cursor-not-allowed
                       transition-all active:scale-95"
            >
              <Send size={14} />
            </button>
          </div>
        </div>

        {editorContent && (
          <div className="mt-1.5 flex items-center gap-1 text-[10px] text-gray-400">
            <BookOpen size={9} />
            <span>已关联编辑内容</span>
          </div>
        )}
      </div>
    </div>
  )
}

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user'

  return (
    <div className={`flex items-start gap-1.5 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser
            ? 'bg-gradient-to-br from-emerald-400 to-teal-500'
            : 'bg-gradient-to-br from-indigo-500 to-purple-500'
        }`}
      >
        {isUser ? (
          <User size={10} className="text-white" />
        ) : (
          <Sparkles size={10} className="text-white" />
        )}
      </div>

      <div
        className={`max-w-[80%] px-2.5 py-2 text-xs leading-relaxed ${
          isUser
            ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-xl rounded-tr-sm'
            : `bg-gray-50 border ${message.isError ? 'border-red-100' : 'border-gray-100'} text-gray-700 rounded-xl rounded-tl-sm`
        }`}
      >
        <div className="whitespace-pre-wrap break-words">{message.content}</div>
        
        {/* 显示建议操作 */}
        {message.actionItems && message.actionItems.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200/50 space-y-1">
            {message.actionItems.map((item, i) => (
              <div key={i} className="flex items-start gap-1.5 text-[11px] text-gray-500">
                <span className="text-indigo-400">•</span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
