import { useState, useEffect } from 'react'
import { AlertTriangle, CheckCircle, Loader2, Search, ChevronDown, ChevronRight, PenLine } from 'lucide-react'
import { checkGrammar, getGrammarResult } from '../../api/literatureApi'

// 解析错误信息中的字数要求
const parseMinLengthFromError = (errorMessage) => {
  // 匹配类似 "至少需要 50 字" 或 "minimum 50 characters" 的模式
  const patterns = [
    /至少[需要]?\s*(\d+)\s*[字个]/,
    /最少[需要]?\s*(\d+)\s*[字个]/,
    /minimum\s*(\d+)/i,
    /at least\s*(\d+)/i,
    /(\d+)\s*字[以]?上/,
    /(\d+)\s*characters/i,
  ]
  for (const pattern of patterns) {
    const match = errorMessage.match(pattern)
    if (match) return parseInt(match[1], 10)
  }
  return null
}

// 字数不足提示组件
const ContentTooShortBanner = ({ minLength, featureName = '使用此功能' }) => (
  <div className="p-4 bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl border border-amber-200 text-center">
    <PenLine size={28} className="mx-auto mb-2 text-amber-400" />
    <p className="text-sm font-medium text-amber-700 mb-1">内容太少啦</p>
    <p className="text-xs text-amber-600">
      至少需要 <span className="font-bold">{minLength}</span> 字才能{featureName}
    </p>
    <p className="text-[10px] text-amber-500 mt-2">继续写作，写够字数后再来检查吧 ✍️</p>
  </div>
)

// 问题卡片组件
const IssueCard = ({ issue }) => {
  const [expanded, setExpanded] = useState(false)
  
  const getIssueTypeStyle = (type, severity) => {
    // 优先按 severity 判断
    if (severity === 'high') {
      return { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-600', label: '严重' }
    }
    if (severity === 'medium') {
      return { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-600', label: '中等' }
    }
    if (severity === 'low') {
      return { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-600', label: '轻微' }
    }
    // 按 type 判断
    switch (type) {
      case 'grammar':
        return { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-600', label: '语法' }
      case 'syntax':
        return { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-600', label: '句法' }
      case 'style':
        return { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-600', label: '风格' }
      case 'typo':
        return { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-600', label: '拼写' }
      default:
        return { bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-600', label: '提示' }
    }
  }

  const style = getIssueTypeStyle(issue.type, issue.severity)
  const hasExplanation = issue.explanation

  return (
    <div className={`rounded-xl border ${style.border} ${style.bg} overflow-hidden`}>
      <div
        className={`p-3 ${hasExplanation ? 'cursor-pointer' : ''}`}
        onClick={() => hasExplanation && setExpanded(!expanded)}
      >
        <div className="flex items-start gap-2">
          <AlertTriangle size={14} className={`${style.text} flex-shrink-0 mt-0.5`} />
          <div className="flex-1 min-w-0">
            {/* 标签和位置 */}
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${style.bg} ${style.text} font-medium border ${style.border}`}>
                {style.label}
              </span>
              {issue.type && (
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-500">
                  {issue.type}
                </span>
              )}
              {issue.line_number && (
                <span className="text-[10px] text-gray-400">
                  第 {issue.line_number} 行
                </span>
              )}
              {hasExplanation && (
                <span className="ml-auto">
                  {expanded ? (
                    <ChevronDown size={12} className="text-gray-400" />
                  ) : (
                    <ChevronRight size={12} className="text-gray-400" />
                  )}
                </span>
              )}
            </div>

            {/* 原文和建议 */}
            {(issue.original_text || issue.suggestion) && (
              <div className="mt-2 text-xs space-y-1">
                {issue.original_text && (
                  <div className="flex items-start gap-1.5">
                    <span className="text-gray-400 flex-shrink-0">原文:</span>
                    <span className="text-red-500 line-through break-all">{issue.original_text}</span>
                  </div>
                )}
                {issue.suggestion && (
                  <div className="flex items-start gap-1.5">
                    <span className="text-gray-400 flex-shrink-0">建议:</span>
                    <span className="text-green-600 font-medium break-all">{issue.suggestion}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 展开的解释 */}
      {expanded && hasExplanation && (
        <div className="px-3 pb-3 pt-0 border-t border-gray-100/50">
          <div className="mt-2 p-2.5 bg-white/60 rounded-lg">
            <p className="text-[11px] text-gray-600 leading-relaxed">{issue.explanation}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export const GrammarCheck = ({ sessionId, content }) => {
  const [issues, setIssues] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [checked, setChecked] = useState(false)
  const [minLengthRequired, setMinLengthRequired] = useState(null) // 字数不足时的最低要求

  // 加载缓存的语法检查结果
  useEffect(() => {
    const fetchCachedResult = async () => {
      if (!sessionId) return
      try {
        const result = await getGrammarResult(sessionId)
        if (result && (result.issues || result.errors || result.problems)) {
          setIssues(result.issues || result.errors || result.problems || [])
          setChecked(true)
          setMinLengthRequired(null)
        }
      } catch (err) {
        // 没有缓存，忽略
      }
    }
    fetchCachedResult()
  }, [sessionId])

  const handleCheck = async () => {
    if (!sessionId || !content) return
    setLoading(true)
    setError(null)
    setMinLengthRequired(null)
    try {
      const result = await checkGrammar({ session_id: sessionId, content })
      setIssues(result.issues || result.errors || result.problems || [])
      setChecked(true)
    } catch (err) {
      const errorMsg = err.message || ''
      const minLength = parseMinLengthFromError(errorMsg)
      if (minLength) {
        setMinLengthRequired(minLength)
      } else {
        setError(errorMsg)
      }
    } finally {
      setLoading(false)
    }
  }

  if (!sessionId) {
    return (
      <div className="text-center py-8 text-gray-400 text-xs">
        请先选择一个会话
      </div>
    )
  }

  return (
    <div>
      {/* 检查按钮 */}
      <div className="mb-4">
        <button
          onClick={handleCheck}
          disabled={loading || !content}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-500 text-white text-xs font-medium rounded-lg hover:bg-indigo-600 disabled:opacity-50 transition-colors"
        >
          {loading ? (
            <>
              <Loader2 size={14} className="animate-spin" />
              检查中...
            </>
          ) : (
            <>
              <Search size={14} />
              检查语法
            </>
          )}
        </button>
      </div>

      {/* 字数不足提示 */}
      {minLengthRequired && (
        <ContentTooShortBanner minLength={minLengthRequired} featureName="检查语法" />
      )}

      {error && (
        <div className="mb-3 p-2 bg-red-50 text-red-600 text-xs rounded-lg">{error}</div>
      )}

      {/* 结果 */}
      {checked && issues.length === 0 && (
        <div className="text-center py-6">
          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-green-100 flex items-center justify-center">
            <CheckCircle size={24} className="text-green-600" />
          </div>
          <p className="text-sm font-medium text-green-700">太棒了！</p>
          <p className="text-xs text-gray-500 mt-1">未发现语法问题</p>
        </div>
      )}

      {issues.length > 0 && (
        <div className="space-y-2.5">
          <div className="text-xs text-gray-500 mb-2">
            发现 <span className="font-medium text-gray-700">{issues.length}</span> 个问题
            <span className="text-[10px] text-gray-400 ml-2">（点击卡片查看详细解释）</span>
          </div>
          {issues.map((issue, i) => (
            <IssueCard key={issue.id || i} issue={issue} />
          ))}
        </div>
      )}

      {!checked && !loading && (
        <div className="text-center py-6 text-gray-400 text-xs">
          点击上方按钮开始检查
        </div>
      )}
    </div>
  )
}
