import React, { useState } from 'react'
import { Lightbulb, ArrowRight, CheckCircle, MessageSquare } from 'lucide-react'

export const FullTextSuggestions = ({ suggestions, onSendToChat }) => {
  const [appliedSuggestions, setAppliedSuggestions] = useState(new Set())
  // 默认建议数据
  const defaultSuggestions = [
    {
      type: 'structure',
      priority: 'high',
      title: '完善文章结构',
      description: '建议在文章末尾添加总结段落，呼应开头并升华主题。',
      examples: [
        '可以这样写：综上所述，人工智能的发展需要我们既保持开放态度，又保持谨慎...'
      ]
    },
    {
      type: 'logic',
      priority: 'medium',
      title: '加强段落过渡',
      description: '第二段和第三段之间缺少逻辑连接，建议添加过渡句。',
      examples: [
        '可以添加：尽管人工智能带来了诸多便利，但我们也不能忽视其潜在风险...'
      ]
    },
    {
      type: 'content',
      priority: 'medium',
      title: '补充具体案例',
      description: '在论述人工智能帮助学习时，可以添加具体的使用场景或案例。',
      examples: [
        '例如：在线教育平台利用AI个性化推荐学习内容，帮助学生更高效地掌握知识...'
      ]
    },
    {
      type: 'vocabulary',
      priority: 'low',
      title: '丰富表达方式',
      description: '部分词汇重复使用，建议使用同义词替换以增强表达力。',
      examples: [
        '"帮助" 可以替换为 "助力"、"促进"、"推动" 等'
      ]
    }
  ]
  
  const data = suggestions || defaultSuggestions
  
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'bg-red-50 border-red-200 text-red-800'
      case 'medium':
        return 'bg-orange-50 border-orange-200 text-orange-800'
      case 'low':
        return 'bg-blue-50 border-blue-200 text-blue-800'
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800'
    }
  }
  
  const getPriorityLabel = (priority) => {
    switch (priority) {
      case 'high':
        return '高优先级'
      case 'medium':
        return '中优先级'
      case 'low':
        return '低优先级'
      default:
        return '建议'
    }
  }
  
  return (
    <div className="space-y-3">
      {data.map((suggestion, index) => (
        <div
          key={index}
          className={`p-3 rounded-lg border ${getPriorityColor(suggestion.priority)}`}
        >
          {/* 标题和优先级 */}
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex items-start gap-2 flex-1">
              <Lightbulb size={16} className="flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold">{suggestion.title}</div>
                <div className="text-[10px] mt-0.5 opacity-70">
                  {getPriorityLabel(suggestion.priority)}
                </div>
              </div>
            </div>
          </div>
          
          {/* 描述 */}
          <div className="text-xs mb-2 leading-relaxed opacity-90">
            {suggestion.description}
          </div>
          
          {/* 示例 */}
          {suggestion.examples && suggestion.examples.length > 0 && (
            <div className="mt-2 space-y-1.5">
              {suggestion.examples.map((example, exIndex) => (
                <div
                  key={exIndex}
                  className="p-2 bg-white/60 rounded border border-white/80 text-xs leading-relaxed"
                >
                  <div className="flex items-start gap-1.5">
                    <ArrowRight size={12} className="flex-shrink-0 mt-0.5 opacity-60" />
                    <span className="flex-1">{example}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* 操作按钮 */}
          <div className="mt-2 flex gap-2">
            {!appliedSuggestions.has(index) ? (
              <>
                <button 
                  onClick={() => {
                    setAppliedSuggestions(prev => new Set([...prev, index]))
                    if (onSendToChat) {
                      onSendToChat(suggestion)
                    }
                  }}
                  className="px-2 py-1 text-[10px] bg-white/80 hover:bg-white rounded border border-white/60 transition-colors flex items-center gap-1"
                >
                  <MessageSquare size={10} />
                  发送到Chat
                </button>
                <button 
                  onClick={() => setAppliedSuggestions(prev => new Set([...prev, index]))}
                  className="px-2 py-1 text-[10px] bg-white/60 hover:bg-white/80 rounded border border-white/40 transition-colors"
                >
                  已处理
                </button>
              </>
            ) : (
              <div className="px-2 py-1 text-[10px] bg-green-100 text-green-700 rounded border border-green-200 flex items-center gap-1">
                <CheckCircle size={10} />
                已处理
              </div>
            )}
          </div>
        </div>
      ))}
      
      {data.length === 0 && (
        <div className="text-center py-8 text-gray-400 text-sm">
          <CheckCircle size={24} className="mx-auto mb-2 text-gray-300" />
          <div>暂无建议，文章质量良好！</div>
        </div>
      )}
    </div>
  )
}

