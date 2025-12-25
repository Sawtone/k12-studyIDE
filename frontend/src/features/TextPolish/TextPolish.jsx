import { useState } from 'react'
import { Sparkles, Loader2, Copy, Check } from 'lucide-react'
import { polishText } from '../../api/literatureApi'

const styles = [
  { id: 'formal', label: '正式' },
  { id: 'casual', label: '轻松' },
  { id: 'academic', label: '学术' },
  { id: 'creative', label: '创意' },
]

export const TextPolish = ({ sessionId, content }) => {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedStyle, setSelectedStyle] = useState('formal')
  const [copiedIndex, setCopiedIndex] = useState(null)

  const handlePolish = async () => {
    if (!sessionId || !content) return
    setLoading(true)
    setError(null)
    try {
      const result = await polishText({ session_id: sessionId, content, style: selectedStyle })
      setResults(result.versions || result.suggestions || result.results || [])
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
    return (
      <div className="text-center py-8 text-gray-400 text-xs">
        请先选择一个会话
      </div>
    )
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

      {error && (
        <div className="mt-3 p-2 bg-red-50 text-red-600 text-xs rounded-lg">{error}</div>
      )}

      {/* 结果 */}
      {results.length > 0 && (
        <div className="mt-4 space-y-3">
          <div className="text-xs text-gray-500">
            为您生成了 <span className="font-medium text-gray-700">{results.length}</span> 个版本
          </div>
          {results.map((result, i) => {
            const text = typeof result === 'string' ? result : result.text || result.content
            const label = result.label || result.style || `版本 ${i + 1}`
            return (
              <div
                key={i}
                className="p-3 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-100 hover:border-indigo-200 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-medium text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">
                    {label}
                  </span>
                  <button
                    onClick={() => handleCopy(text, i)}
                    className="flex items-center gap-1 text-[10px] text-gray-500 hover:text-indigo-600 transition-colors"
                  >
                    {copiedIndex === i ? (
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
              </div>
            )
          })}
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
