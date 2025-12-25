import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle, RefreshCw, Loader2, ChevronDown, ChevronRight, PenLine } from 'lucide-react'
import { getHealthScore, analyzeHealth } from '../../api/literatureApi'

// 解析错误信息中的字数要求
const parseMinLengthFromError = (errorMessage) => {
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

// 维度名称映射
const dimensionLabels = {
  structure: '结构',
  coherence: '连贯性',
  clarity: '清晰度',
  grammar: '语法',
  richness: '丰富度',
}

// 根据分数获取颜色
const getScoreColor = (score) => {
  if (score >= 0.8) return { bar: 'bg-green-500', text: 'text-green-600' }
  if (score >= 0.6) return { bar: 'bg-indigo-500', text: 'text-indigo-600' }
  return { bar: 'bg-orange-400', text: 'text-orange-600' }
}

// 维度详情组件
const DimensionDetail = ({ name, data }) => {
  const [expanded, setExpanded] = useState(false)
  const score = Math.round((data.score || 0) * 100)
  const color = getScoreColor(data.score)

  return (
    <div className="border border-gray-100 rounded-lg overflow-hidden">
      <div
        className="flex items-center gap-3 p-2.5 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="w-4">
          {expanded ? (
            <ChevronDown size={12} className="text-gray-400" />
          ) : (
            <ChevronRight size={12} className="text-gray-400" />
          )}
        </div>
        <div className="flex-1">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs font-medium text-gray-700">
              {dimensionLabels[name] || name}
            </span>
            <span className={`text-xs font-medium ${color.text}`}>{score}%</span>
          </div>
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${score}%` }}
              transition={{ duration: 0.6 }}
              className={`h-full ${color.bar} rounded-full`}
            />
          </div>
        </div>
      </div>

      {expanded && (
        <div className="px-3 pb-3 pt-1 bg-gray-50/50 border-t border-gray-100">
          {data.reasoning && (
            <p className="text-[11px] text-gray-600 leading-relaxed mb-2">{data.reasoning}</p>
          )}
          {data.issues && data.issues.length > 0 && (
            <div className="mb-2">
              <div className="text-[10px] text-orange-600 font-medium mb-1">问题</div>
              <ul className="text-[10px] text-gray-600 space-y-0.5">
                {data.issues.map((issue, i) => (
                  <li key={i} className="flex items-start gap-1">
                    <span className="text-orange-400 mt-0.5">•</span>
                    {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {data.suggestions && data.suggestions.length > 0 && (
            <div>
              <div className="text-[10px] text-green-600 font-medium mb-1">建议</div>
              <ul className="text-[10px] text-gray-600 space-y-0.5">
                {data.suggestions.map((sug, i) => (
                  <li key={i} className="flex items-start gap-1">
                    <span className="text-green-400 mt-0.5">•</span>
                    {sug}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}


export const HealthCheck = ({ sessionId, content }) => {
  const [healthData, setHealthData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [minLengthRequired, setMinLengthRequired] = useState(null)

  const fetchHealth = async () => {
    if (!sessionId) return
    setLoading(true)
    setError(null)
    try {
      const result = await getHealthScore(sessionId)
      setHealthData(result)
      setMinLengthRequired(null)
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
    setMinLengthRequired(null)
    try {
      const result = await analyzeHealth({ session_id: sessionId, content })
      setHealthData(result)
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

  useEffect(() => {
    fetchHealth()
  }, [sessionId])

  const overallScore = healthData?.overall_score
  const grade = healthData?.grade
  const dimensions = healthData?.dimensions

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-gray-400">
        <Loader2 size={20} className="animate-spin mb-2" />
        <span className="text-xs">评估中...</span>
      </div>
    )
  }

  if (!sessionId) {
    return <div className="text-center py-8 text-gray-400 text-xs">请先选择一个会话</div>
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
          {healthData ? '重新评估' : '开始评估'}
        </button>
      </div>

      {/* 字数不足提示 */}
      {minLengthRequired && (
        <ContentTooShortBanner minLength={minLengthRequired} featureName="评估健康度" />
      )}

      {error && <div className="mb-3 p-2 bg-red-50 text-red-600 text-xs rounded-lg">{error}</div>}

      {!healthData && !minLengthRequired ? (
        <div className="text-center py-8">
          <AlertCircle size={32} className="mx-auto mb-2 text-gray-300" />
          <p className="text-gray-400 text-xs mb-3">暂无健康度数据</p>
          <p className="text-[10px] text-gray-400">点击上方按钮开始评估</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* 总分卡片 */}
          {overallScore !== undefined && (
            <div className="text-center p-4 bg-gradient-to-br from-indigo-50 to-white rounded-xl border border-indigo-100">
              <div className="flex items-center justify-center gap-3">
                <div className="text-4xl font-bold text-indigo-600">
                  {Math.round(overallScore * 100)}
                </div>
                {grade && (
                  <div className="px-2.5 py-1 bg-indigo-100 text-indigo-700 text-lg font-bold rounded-lg">
                    {grade}
                  </div>
                )}
              </div>
              <div className="text-xs text-gray-500 mt-2">综合评分</div>
            </div>
          )}

          {/* 各维度详情 */}
          {dimensions && (
            <div className="space-y-2">
              <div className="text-xs text-gray-500 mb-2">各维度评分（点击展开详情）</div>
              {Object.entries(dimensions).map(([key, value]) => (
                <DimensionDetail key={key} name={key} data={value} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
