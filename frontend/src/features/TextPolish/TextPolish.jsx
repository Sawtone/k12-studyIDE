import { useState, useEffect } from 'react'
import { Sparkles, Loader2, Copy, Check, Star, ChevronDown, ChevronRight } from 'lucide-react'
import { polishText } from '../../api/literatureApi'

const styles = [
  { id: 'formal', label: '正式' },
  { id: 'casual', label: '轻松' },
  { id: 'academic', label: '学术' },
  { id: 'creative', label: '创意' },
]

// 润色结果卡片
const PolishCard = ({ result, index, isRecommended, copiedIndex, onCopy }) => {
  const [expanded, setExpanded] = useState(false)
  const text = result.polished_text || result.text || result.content
  const styleLabel = result.style || `版本 ${index + 1}`

  return (
    <div
      className={`rounded-xl border transition-colors ${
        isRecommended
          ? 'bg-gradient-to-br from-indigo-50 to-white border-indigo-200'
          : 'bg-gradient-to-br from-gray-50 to-white border-gray-100 hover:border-gray-200'
      }`}
    >
      <div className="p-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-medium text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">
              {styleLabel}
            </span>
            {isRecommended && (
              <span className="flex items-center gap-0.5 text-[9px] text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded-full">
                <Star size={8} className="fill-amber-500" />
                推荐
              </span>
            )}
          </div>
          <button
            onClick={() => onCopy(text, index)}
            className="flex items-center gap-1 text-[10px] text-gray-500 hover:text-indigo-600 transition-colors"
          >
            {copiedIndex === index ? (
              <>
                <Check size={10} className="text-green-500" />
                已复制
              </>
            ) : (
              <>
                <Copy size={10} />
                复制
              </>
            )}
          </button>
        </div>

        <p className="text-xs text-gray-700 leading-relaxed">{text}</p>

        {/* 展开详情 */}
        {(result.changes || result.reasoning) && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 mt-2 text-[10px] text-gray-400 hover:text-gray-600"
          >
            {expanded ? <ChevronDown size={10} /> : <ChevronRight size={10} />}
            {expanded ? '收起详情' : '查看修改说明'}
          </button>
        )}
      </div>

      {expanded && (result.changes || result.reasoning) && (
        <div className="px-3 pb-3 pt-1 border-t border-gray-100">
          {result.changes && result.changes.length > 0 && (
            <div className="mb-2">
              <div className="text-[10px] text-gray-500 font-medium mb-1">修改内容</div>
              <ul className="text-[10px] text-gray-600 space-y-0.5">
                {result.changes.map((change, i) => (
                  <li key={i} className="flex items-start gap-1">
                    <span className="text-indigo-400 mt-0.5">•</span>
                    {change}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {result.reasoning && (
            <div>
              <div className="text-[10px] text-gray-500 font-medium mb-1">修改理由</div>
              <p className="text-[10px] text-gray-600 leading-relaxed">{result.reasoning}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}


export const TextPolish = ({ sessionId, content }) => {
  const [results, setResults] = useState([])
  const [recommended, setRecommended] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedStyle, setSelectedStyle] = useState('formal')
  const [copiedIndex, setCopiedIndex] = useState(null)

  // 内容变化时清空结果
  useEffect(() => {
    setResults([])
    setRecommended(null)
  }, [content])

  const handlePolish = async () => {
    if (!sessionId || !content) return
    setLoading(true)
    setError(null)
    try {
      const result = await polishText({ session_id: sessionId, content, style: selectedStyle })
      setResults(result.versions || [])
      setRecommended(result.recommended)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedIndex(index)
      setTimeout(() => setCopiedIndex(null), 2000)
    } catch (err) {
      console.error('复制失败:', err)
    }
  }

  if (!sessionId) {
    return <div className="text-center py-8 text-gray-400 text-xs">请先选择一个会话</div>
  }

  return (
    <div>
      {/* 风格选择 */}
      <div className="mb-3">
        <div className="text-xs text-gray-500 mb-2">选择润色风格</div>
        <div className="flex flex-wrap gap-1.5">
          {styles.map((style) => (
            <button
              key={style.id}
              onClick={() => setSelectedStyle(style.id)}
              className={`px-2.5 py-1 text-[10px] font-medium rounded-full transition-colors ${
                selectedStyle === style.id
                  ? 'bg-indigo-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {style.label}
            </button>
          ))}
        </div>
      </div>

      {/* 润色按钮 */}
      <button
        onClick={handlePolish}
        disabled={loading || !content}
        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-violet-500 to-indigo-500 text-white text-xs font-medium rounded-lg hover:from-violet-600 hover:to-indigo-600 disabled:opacity-50 transition-all"
      >
        {loading ? (
          <>
            <Loader2 size={14} className="animate-spin" />
            润色中...
          </>
        ) : (
          <>
            <Sparkles size={14} />
            开始润色
          </>
        )}
      </button>

      {error && <div className="mt-3 p-2 bg-red-50 text-red-600 text-xs rounded-lg">{error}</div>}

      {/* 结果 */}
      {results.length > 0 && (
        <div className="mt-4 space-y-3">
          <div className="text-xs text-gray-500">
            为您生成了 <span className="font-medium text-gray-700">{results.length}</span> 个版本
          </div>
          {results.map((result, i) => (
            <PolishCard
              key={i}
              result={result}
              index={i}
              isRecommended={recommended === result.version || recommended === i + 1}
              copiedIndex={copiedIndex}
              onCopy={handleCopy}
            />
          ))}
        </div>
      )}

      {results.length === 0 && !loading && (
        <div className="mt-6 text-center py-4 text-gray-400 text-xs">
          选择风格后点击按钮开始润色
        </div>
      )}
    </div>
  )
}
