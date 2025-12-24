import React, { useState, useEffect, useRef } from 'react'
import { Send } from 'lucide-react'

export const AIChat = ({ externalMessage }) => {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    { role: 'ai', content: '👋 你好！我是写作助手，随时为你服务。' },
  ])
  const messagesEndRef = useRef(null)
  
  // 接收外部消息（从右侧建议面板）
  useEffect(() => {
    if (externalMessage) {
      setMessages(prev => [
        ...prev,
        { role: 'user', content: externalMessage },
        { role: 'ai', content: '✨ 收到！我来帮你处理这个建议。' }
      ])
      // 滚动到底部
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    }
  }, [externalMessage])
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSend = () => {
    if (input.trim()) {
      setMessages(prev => [...prev, { role: 'user', content: input }])
      setInput('')
      setTimeout(() => {
        setMessages(prev => [...prev, { role: 'ai', content: '✨ 收到你的消息，让我来帮你分析一下。' }])
        scrollToBottom()
      }, 500)
    }
  }
  
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] px-3 py-2 rounded-2xl text-sm ${
              msg.role === 'user'
                ? 'bg-indigo-500 text-white rounded-br-sm'
                : 'bg-gray-100 text-gray-700 rounded-bl-sm'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="mt-3 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入问题..."
          className="flex-1 px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-300 transition-all"
        />
        <button 
          onClick={handleSend}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          className="p-2 bg-indigo-500 text-white rounded-xl hover:bg-indigo-600 transition-colors"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
