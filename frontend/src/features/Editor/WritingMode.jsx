import React from 'react'

export const WritingMode = ({ content, setContent }) => {
  return (
    <div 
      className="h-full p-8"
      style={{
        backgroundColor: '#fdfbf7',
        backgroundImage: 'radial-gradient(#e5e7eb 1px, transparent 1px)',
        backgroundSize: '20px 20px',
      }}
    >
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        className="w-full h-full font-serif text-lg text-gray-700 bg-transparent resize-none focus:outline-none leading-relaxed"
        placeholder="开始写作..."
        style={{ lineHeight: '2.2' }}
      />
    </div>
  )
}
