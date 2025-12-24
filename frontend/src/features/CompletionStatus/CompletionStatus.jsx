import React, { useEffect, useState } from 'react'
import { CheckCircle, AlertCircle, Loader2, RefreshCw } from 'lucide-react'

export const CompletionStatus = ({ analysisData, onRerunCheck }) => {
  const [isChecking, setIsChecking] = useState(false)
  const [completionStatus, setCompletionStatus] = useState(null)
  
  // 检查待修改项是否已完成
  const checkCompletion = () => {
    setIsChecking(true)
    
    // 模拟检查过程
    setTimeout(() => {
      if (!analysisData) {
        setCompletionStatus({
          completed: false,
          message: '请先运行分析',
          pendingCount: 0
        })
        setIsChecking(false)
        return
      }
      
      // 检查是否有待修改项
      const suggestions = analysisData.suggestions || []
      const initialCheck = analysisData.initialCheck
      const hasPendingIssues = initialCheck && initialCheck.summary.totalIssues > 0
      const hasHighPrioritySuggestions = suggestions.some(s => s.priority === 'high')
      
      const pendingCount = (hasPendingIssues ? 1 : 0) + (hasHighPrioritySuggestions ? suggestions.filter(s => s.priority === 'high').length : 0)
      
      if (pendingCount === 0) {
        setCompletionStatus({
          completed: true,
          message: '所有待修改项已完成！',
          pendingCount: 0
        })
      } else {
        setCompletionStatus({
          completed: false,
          message: `还有 ${pendingCount} 项待修改`,
          pendingCount
        })
      }
      
      setIsChecking(false)
    }, 1000)
  }
  
  useEffect(() => {
    if (analysisData) {
      checkCompletion()
    }
  }, [analysisData])
  
  if (!analysisData) {
    return (
      <div className="p-3 bg-gray-50 rounded-lg border border-gray-200 text-center">
        <div className="text-xs text-gray-500">请先运行分析</div>
      </div>
    )
  }
  
  if (isChecking) {
    return (
      <div className="p-3 bg-blue-50 rounded-lg border border-blue-200 flex items-center gap-2">
        <Loader2 size={14} className="text-blue-600 animate-spin" />
        <span className="text-xs text-blue-700">检查中...</span>
      </div>
    )
  }
  
  if (!completionStatus) {
    return null
  }
  
  return (
    <div className={`p-3 rounded-lg border flex items-center justify-between ${
      completionStatus.completed
        ? 'bg-green-50 border-green-200'
        : 'bg-orange-50 border-orange-200'
    }`}>
      <div className="flex items-center gap-2 flex-1">
        {completionStatus.completed ? (
          <CheckCircle size={16} className="text-green-600 flex-shrink-0" />
        ) : (
          <AlertCircle size={16} className="text-orange-600 flex-shrink-0" />
        )}
        <div className="flex-1 min-w-0">
          <div className={`text-xs font-medium ${
            completionStatus.completed ? 'text-green-700' : 'text-orange-700'
          }`}>
            {completionStatus.message}
          </div>
          {!completionStatus.completed && (
            <div className="text-[10px] text-orange-600/70 mt-0.5">
              {completionStatus.pendingCount} 项待处理
            </div>
          )}
        </div>
      </div>
      <button
        onClick={checkCompletion}
        className="p-1.5 hover:bg-white/60 rounded transition-colors"
        title="重新检查"
      >
        <RefreshCw size={12} className={completionStatus.completed ? 'text-green-600' : 'text-orange-600'} />
      </button>
    </div>
  )
}

