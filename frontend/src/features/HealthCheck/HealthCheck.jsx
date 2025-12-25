import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle, RefreshCw, Loader2 } from 'lucide-react'
import { getHealthScore, analyzeHealth } from '../../api/literatureApi'

export const HealthCheck = ({ sessionId, content }) => {
  const [healthData, setHealthData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchHealth = async () => {
    if (!sessionId) return
    setLoading(true)
    setError(null)
    try {
      const result = await getHealthScore(sessionId)
      setHealthData(result)
    } catch (err) {
      setHealthData(null)
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!sessionId || !content) return
    setLoading(true)
    setError(null)
    try {
      const result = await analyzeHealth({ session_id: sessionId, content })
      setHealthData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHealth()
  }, [sessionId])

  // 从 API 响应中提取指标
  const metrics = healthData?.metrics || healthData?.scores || []
  const suggestions = healthData?.suggestions || healthData?.recommendations || []
  const overallScore = healthData?.overall_score || healthData?.score

  const getColorClass = (value) => {
    if (value >= 80) return 'bg-green-500'
    if (value >= 60) return 'bg-indigo-500'
    return 'bg-orange-400'
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-gray-400">
        <Loader2 size={20} className="animate-spin mb-2" />
        <span className="text-xs">评估中...</span>
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
      <div className="flex justify-end mb-3">
        <button
          onClick={handleAnalyze}
          disabled={loading || !content}
          className="flex items-center gap-1 px-2 py-1 text-[10px] text-indigo-600 hover:bg-indigo-50 rounded transition-colors disabled:opacity-50"
        >
          <RefreshCw size={10} />
          重新评估
        </button>
      </div>

      {error && (
        <div className="mb-3 p-2 bg-red-50 text-red-600 text-xs rounded-lg">{error}</div>
      )}

      {metrics.length === 0 && !overallScore ? (
        <div className="text-center py-8">
          <p className="text-gray-400 text-xs mb-3">暂无健康度数据</p>
          <button
            onClick={handleAnalyze}
            disabled={!content}
            className="px-3 py-1.5 bg-indigo-500 text-white text-xs rounded-lg hover:bg-indigo-600 disabled:opacity-50"
          >
            开始评估
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* 总分 */}
          {overallScore !== undefined && (
            <div className="text-center p-4 bg-gradient-to-br from-indigo-50 to-white rounded-xl border border-indigo-100">
              <div className="text-3xl font-bold text-indigo-600">{overallScore}</div>
              <div className="text-xs text-gray-500 mt-1">综合评分</div>
            </div>
          )}

          {/* 各项指标 */}
          {metrics.map((m, i) => {
            const label = m.label || m.name || m.metric
            const value = m.value || m.score || 0
            return (
              <div key={i}>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-gray-600">{label}</span>
                  <span className="font-medium text-gray-700">{value}%</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${value}%` }}
                    transition={{ duration: 0.8, delay: i * 0.15 }}
                    className={`h-full ${getColorClass(value)} rounded-full`}
                  />
                </div>
              </div>
            )
          })}

          {/* 建议 */}
          {suggestions.length > 0 && (
            <div className="mt-5 p-3 bg-orange-50 rounded-xl border border-orange-100">
              <div className="flex items-start gap-2">
                <AlertCircle size={16} className="text-orange-500 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-orange-700 text-sm">改进建议</div>
                  <ul className="text-xs text-orange-600/80 mt-1 leading-relaxed space-y-1">
                    {suggestions.map((s, i) => (
                      <li key={i}>{typeof s === 'string' ? s : s.text || s.content}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
