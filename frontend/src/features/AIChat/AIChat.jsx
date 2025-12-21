import React, { useState } from 'react'
import { Send } from 'lucide-react'

export const AIChat = () => {
  const [input, setInput] = useState('')
  const messages = [
    { role: 'ai', content: '👋 你好！我是写作助手，随时为你服务。' },
    { role: 'ai', content: '💡 第二段存在逻辑跳跃，需要帮你修复吗？' },
    { role: 'user', content: '好的，请帮我看看' },
    { role: 'ai', content: '✨ 建议添加过渡句说明为什么需要谨慎。' },
  ]

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
      </div>
      <div className="mt-3 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入问题..."
          className="flex-1 px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-300 transition-all"
        />
        <button className="p-2 bg-indigo-500 text-white rounded-xl hover:bg-indigo-600 transition-colors">
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
