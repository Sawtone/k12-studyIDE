import React from 'react'

export const IDEMode = ({ sentences, onSentenceChange }) => {
  const getTagForSentence = (index) => {
    const tags = [
      { label: '主题句', color: 'green' },
      { label: '论据', color: 'orange' },
      { label: '⚠️ 过渡', color: 'rose' },
    ]
    return tags[index] || null
  }

  return (
    <div className="h-full bg-gray-50 overflow-auto p-4">
      <div className="space-y-1">
        {sentences.map((sentence, i) => {
          const tag = getTagForSentence(i)
          return (
            <div key={i} className="flex items-start group">
              <div className="w-10 flex-shrink-0 text-right pr-3 text-gray-400 text-sm font-mono select-none pt-2">
                {i + 1}
              </div>
              
              <div className="flex-1 flex items-center gap-2 py-1.5 px-3 rounded-lg hover:bg-white border border-transparent hover:border-gray-200 transition-all">
                {tag && (
                  <span className={`flex-shrink-0 px-2 py-0.5 bg-${tag.color}-50 text-${tag.color}-700 text-xs font-medium rounded border border-${tag.color}-200`}>
                    {tag.label}
                  </span>
                )}
                
                <input
                  type="text"
                  value={sentence}
                  onChange={(e) => onSentenceChange(i, e.target.value)}
                  className="flex-1 font-mono text-sm text-gray-700 bg-transparent focus:outline-none"
                />
              </div>
            </div>
          )
        })}
        
        <div className="flex items-center text-gray-300 text-sm font-mono">
          <div className="w-10 text-right pr-3">{sentences.length + 1}</div>
          <span className="italic pl-3">继续写作...</span>
        </div>
      </div>
    </div>
  )
}
