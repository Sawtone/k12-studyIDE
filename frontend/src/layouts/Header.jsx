import { Sparkles, ChevronRight, Tag, FileText, Clock, Save } from 'lucide-react'
import { SystemStatus } from '../features/SystemStatus/SystemStatus'

export const Header = ({ wordCount, sentenceCount, readingTime }) => {
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
          <span className="hover:text-gray-700 cursor-pointer">我的项目</span>
          <ChevronRight size={14} />
          <span className="hover:text-gray-700 cursor-pointer">作文集</span>
          <ChevronRight size={14} />
          <span className="text-gray-700 font-medium">AI伦理.md</span>
        </div>
        
        <span className="px-2 py-0.5 bg-blue-50 text-blue-600 text-xs font-medium rounded-full flex items-center gap-1">
          <Tag size={10} />
          语文
        </span>
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
        <div className="flex items-center gap-1.5 text-green-600">
          <Save size={14} />
          <span>已自动保存</span>
        </div>
        <div className="h-3 w-px bg-gray-200" />
        <SystemStatus compact />
      </div>
    </header>
  )
}
