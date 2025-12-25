import { motion } from 'framer-motion'
import { PenTool, Code2 } from 'lucide-react'

export const ModeToggle = ({ isIDEMode, onToggle }) => {
  return (
    <div className="relative flex items-center p-0.5 rounded-xl bg-gray-100/80 border border-gray-200/50">
      {/* 滑动背景 */}
      <motion.div
        className="absolute inset-y-0.5 rounded-[10px] shadow-sm"
        initial={false}
        animate={{
          x: isIDEMode ? '100%' : '0%',
          background: isIDEMode
            ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
            : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
        }}
        transition={{
          type: 'spring',
          stiffness: 400,
          damping: 30,
        }}
        style={{
          width: 'calc(50% - 2px)',
          left: '2px',
        }}
      />

      {/* 写作模式按钮 */}
      <button
        onClick={() => onToggle(false)}
        className={`relative z-10 flex items-center gap-1.5 px-3 py-1.5 rounded-[10px] text-xs font-medium transition-colors duration-200 ${
          !isIDEMode ? 'text-white' : 'text-gray-500 hover:text-gray-700'
        }`}
      >
        <PenTool size={12} className={!isIDEMode ? 'drop-shadow-sm' : ''} />
        <span>写作</span>
      </button>

      {/* IDE模式按钮 */}
      <button
        onClick={() => onToggle(true)}
        className={`relative z-10 flex items-center gap-1.5 px-3 py-1.5 rounded-[10px] text-xs font-medium transition-colors duration-200 ${
          isIDEMode ? 'text-white' : 'text-gray-500 hover:text-gray-700'
        }`}
      >
        <Code2 size={12} className={isIDEMode ? 'drop-shadow-sm' : ''} />
        <span>IDE</span>
      </button>
    </div>
  )
}
