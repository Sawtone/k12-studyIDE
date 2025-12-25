import { Sparkles, ChevronRight, FileText, Clock, Save, Loader2, Cloud } from 'lucide-react'
import { SystemStatus } from '../features/SystemStatus/SystemStatus'

// 格式化保存时间
const formatSaveTime = (date) => {
  if (!date) return null
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

export const Header = ({
  wordCount,
  sentenceCount,
  readingTime,
  syncing = false,
  lastSaved,
  sessionTitle,
}) => {
  const saveTimeText = formatSaveTime(lastSaved)

  return (
    <header className="h-12 bg-white border-b border-gray-200 flex items-center justify-between px-4 flex-shrink-0">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center">
            <Sparkles size={14} className="text-white" />
          </div>
          <span className="font-semibold text-gray-800">认知IDE</span>
        </div>

        <div className="h-4 w-px bg-gray-200" />

        <div className="flex items-center gap-1.5 text-sm text-gray-500">
          <span className="hover:text-gray-700 cursor-pointer">会话</span>
          <ChevronRight size={14} />
          <span className="text-gray-700 font-medium truncate max-w-[200px]">
            {sessionTitle || '未选择会话'}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4 text-sm text-gray-500">
        <div className="flex items-center gap-1.5">
          <FileText size={14} />
          <span>{wordCount} 字</span>
        </div>
        <div className="h-3 w-px bg-gray-200" />
        <div className="flex items-center gap-1.5">
          <Clock size={14} />
          <span>约 {readingTime} 分钟</span>
        </div>
        <div className="h-3 w-px bg-gray-200" />

        {/* 同步状态 */}
        {syncing ? (
          <div className="flex items-center gap-1.5 text-indigo-500">
            <Loader2 size={14} className="animate-spin" />
            <span>保存中...</span>
          </div>
        ) : saveTimeText ? (
          <div className="flex items-center gap-1.5 text-green-600">
            <Cloud size={14} />
            <span>已保存 {saveTimeText}</span>
          </div>
        ) : (
          <div className="flex items-center gap-1.5 text-gray-400">
            <Save size={14} />
            <span>未保存</span>
          </div>
        )}

        <div className="h-3 w-px bg-gray-200" />
        <SystemStatus compact />
      </div>
    </header>
  )
}
