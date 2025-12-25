import { useState, useCallback, useRef, useEffect } from 'react'

export const useResizable = (initialLeftWidth = 280, initialRightWidth = 280) => {
  const [leftWidth, setLeftWidth] = useState(initialLeftWidth)
  const [rightWidth, setRightWidth] = useState(initialRightWidth)
  const containerRef = useRef(null)
  const draggingRef = useRef(null)

  const handleMouseDown = useCallback((side) => (e) => {
    e.preventDefault()
    draggingRef.current = side
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }, [])

  const handleMouseMove = useCallback((e) => {
    if (!draggingRef.current || !containerRef.current) return
    
    const rect = containerRef.current.getBoundingClientRect()
    
    if (draggingRef.current === 'left') {
      const newWidth = Math.max(180, Math.min(400, e.clientX - rect.left))
      setLeftWidth(newWidth)
    } else if (draggingRef.current === 'right') {
      const newWidth = Math.max(200, Math.min(400, rect.right - e.clientX))
      setRightWidth(newWidth)
    }
  }, [])

  const handleMouseUp = useCallback(() => {
    draggingRef.current = null
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }, [])

  useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [handleMouseMove, handleMouseUp])

  return {
    leftWidth,
    rightWidth,
    containerRef,
    handleMouseDown,
  }
}
