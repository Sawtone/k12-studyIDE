import React from 'react'

export const ResizeHandle = ({ onMouseDown }) => {
  return (
    <div
      onMouseDown={onMouseDown}
      className="w-1 flex-shrink-0 cursor-col-resize hover:bg-indigo-200 active:bg-indigo-300 transition-colors group flex items-center justify-center"
    >
      <div className="w-0.5 h-12 bg-gray-300 group-hover:bg-indigo-400 rounded-full transition-colors" />
    </div>
  )
}
