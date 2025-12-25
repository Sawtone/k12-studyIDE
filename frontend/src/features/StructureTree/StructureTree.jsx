import { useState, useEffect } from 'react'
import { CheckCircle, AlertCircle, RefreshCw, Loader2 } from 'lucide-react'
import { getStructure, analyzeStructure } from '../../api/literatureApi'

export const StructureTree = ({ sessionId, content }) => {
  const [structure, setStructure] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // 获取缓存的结构
  const fetchStructure = async () => {
    if (!sessionId) return
    setLoading(true)
    setError(null)
    try {
      const result = await getStructure(sessionId)
      setStructure(result)
    } catch (err) {
      // 如果没有缓存，显示空状态
      setStructure(null)
    } finally {
      setLoading(false)
    }
  }

  // 重新分析结构
  const handleAnalyze = async () => {
    if (!sessionId || !content) return
    setLoading(true)
    setError(null)
    try {
      const result = await analyzeStructure({ session_id: sessionId, content })
      setStructure(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStructure()
  }, [sessionId])

  // 从 API 响应中提取节点
  const nodes = structure?.nodes || structure?.sections || structure?.structure || []

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-gray-400">
        <Loader2 size={20} className="animate-spin mb-2" />
        <span className="text-xs">分析中...</span>
      </div>
    )
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
      {/* 操作按钮 */}
      <div className="flex justify-end mb-3">
        <button
          onClick={handleAnalyze}
          disabled={loading || !content}
          className="flex items-center gap-1 px-2 py-1 text-[10px] text-indigo-600 hover:bg-indigo-50 rounded transition-colors disabled:opacity-50"
        >
          <RefreshCw size={10} />
          重新分析
        </button>
      </div>

      {error && (
        <div className="mb-3 p-2 bg-red-50 text-red-600 text-xs rounded-lg">{error}</div>
      )}

      {nodes.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-400 text-xs mb-3">暂无结构分析</p>
          <button
            onClick={handleAnalyze}
            disabled={!content}
            className="px-3 py-1.5 bg-indigo-500 text-white text-xs rounded-lg hover:bg-indigo-600 disabled:opacity-50"
          >
            开始分析
          </button>
        </div>
      ) : (
        <div className="relative">
          <div className="absolute left-[15px] top-6 bottom-6 w-0.5 bg-gray-200" />
          <div className="space-y-3">
            {nodes.map((node, i) => {
              const status = node.status || (node.issues?.length > 0 ? 'warning' : 'ok')
              const label = node.label || node.title || node.name || `段落 ${i + 1}`
              const desc = node.desc || node.description || node.summary || ''

              return (
                <div key={i} className="flex items-start gap-3 relative">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 z-10 ${
                      status === 'ok' ? 'bg-green-100' : 'bg-rose-100'
                    }`}
                  >
                    {status === 'ok' ? (
                      <CheckCircle size={16} className="text-green-600" />
                    ) : (
                      <AlertCircle size={16} className="text-rose-500" />
                    )}
                  </div>
                  <div
                    className={`flex-1 p-3 rounded-xl ${
                      status === 'ok'
                        ? 'bg-green-50 border border-green-100'
                        : 'bg-rose-50 border border-rose-100'
                    }`}
                  >
                    <div
                      className={`font-medium text-sm ${
                        status === 'ok' ? 'text-green-700' : 'text-rose-600'
                      }`}
                    >
                      {label}
                    </div>
                    {desc && (
                      <div
                        className={`text-xs mt-0.5 ${
                          status === 'ok' ? 'text-green-600/70' : 'text-rose-500/70'
                        }`}
                      >
                        {desc}
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
