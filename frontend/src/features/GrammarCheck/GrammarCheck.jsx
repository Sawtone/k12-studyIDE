import { useState } from 'react'
import { AlertTriangle, CheckCircle, Loader2, Search } from 'lucide-react'
import { checkGrammar } from '../../api/literatureApi'

export const GrammarCheck = ({ sessionId, content }) => {
  const [issues, setIssues] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [checked, setChecked] = useState(false)

  const handleCheck = async () => {
    if (!sessionId || !content) return
    setLoading(true)
    setError(null)
    try {
      const result = await checkGrammar({ session_id: sessionId, content })
      setIssues(result.issues || result.errors || result.problems || [])
      setChecked(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getIssueTypeStyle = (type) => {
    switch (type) {
      case 'error':
      case 'typo':
        return { bg: 'bg-red-50', border: 'border-red-100', text: 'text-red-600', label: '错误' }
      case 'warning':
      case 'grammar':
        return { bg: 'bg-orange-50', border: 'border-orange-100', text: 'text-orange-600', label: '语法' }
      case 'suggestion':
      case 'style':
        return { bg: 'bg-blue-50', border: 'border-blue-100', text: 'text-blue-600', label: '建议' }
      default:
        return { bg: 'bg-gray-50', border: 'border-gray-100', text: 'text-gray-600', label: '提示' }
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
        <div className="space-y-2">
          <div className="text-xs text-gray-500 mb-2">
            发现 <span className="font-medium text-gray-700">{issues.length}</span> 个问题
          </div>
          {issues.map((issue, i) => {
            const style = getIssueTypeStyle(issue.type || issue.severity)
            return (
              <div
                key={i}
                className={`p-3 rounded-lg border ${style.bg} ${style.border}`}
              >
                <div className="flex items-start gap-2">
                  <AlertTriangle size={14} className={`${style.text} flex-shrink-0 mt-0.5`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded ${style.bg} ${style.text} font-medium`}>
                        {style.label}
                      </span>
                      {issue.position && (
                        <span className="text-[10px] text-gray-400">
                          位置: {issue.position}
                        </span>
                      )}
                    </div>
                    <p className={`text-xs mt-1 ${style.text}`}>
                      {issue.message || issue.description || issue.text}
                    </p>
                    {issue.suggestion && (
                      <p className="text-xs text-gray-600 mt-1">
                        建议: <span className="font-medium">{issue.suggestion}</span>
                      </p>
                    )}
                    {issue.original && issue.corrected && (
                      <div className="mt-2 text-xs">
                        <span className="line-through text-red-400">{issue.original}</span>
                        <span className="mx-2">→</span>
                        <span className="text-green-600 font-medium">{issue.corrected}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
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
