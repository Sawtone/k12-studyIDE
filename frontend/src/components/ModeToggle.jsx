import React from 'react'
import { motion } from 'framer-motion'
import { PenTool, Code2 } from 'lucide-react'

export const ModeToggle = ({ isIDEMode, onToggle }) => {
  return (
    <div className="relative flex items-center bg-gray-100 p-1 rounded-full">
      <motion.div
        className="absolute h-8 bg-white rounded-full shadow-sm"
        layout
        transition={{ type: "spring", stiffness: 500, damping: 35 }}
        style={{
          width: 'calc(50% - 4px)',
          left: isIDEMode ? 'calc(50% + 2px)' : '4px',
        }}
      />
      
      <button
        onClick={() => onToggle(false)}
        className={`relative z-10 flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
          !isIDEMode ? 'text-indigo-600' : 'text-gray-500'
        }`}
      >
        <PenTool size={14} />
        写作
      </button>
      <button
        onClick={() => onToggle(true)}
        className={`relative z-10 flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
          isIDEMode ? 'text-indigo-600' : 'text-gray-500'
        }`}
      >
        <Code2 size={14} />
        IDE
      </button>
    </div>
  )
}
