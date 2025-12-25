import { FileText, FileCode } from 'lucide-react'
import { ModeToggle } from '../components/ModeToggle'
import { Editor } from '../features/Editor/Editor'

export const EditorPanel = ({
  isIDEMode,
  onModeToggle,
  content,
  setContent,
  sentenceCount,
  sessionId,
  sessionTitle,
}) => {
  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-white mx-0.5 rounded-t-xl shadow-sm border border-gray-200 border-b-0 mt-2">
      <div className="h-12 border-b border-gray-100 flex items-center justify-between px-4 bg-gray-50/50 rounded-t-xl">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          {isIDEMode ? (
            <FileCode size={16} className="text-amber-500" />
          ) : (
            <FileText size={16} className="text-indigo-500" />
          )}
          <span className="font-medium truncate max-w-[200px]">
            {sessionTitle || '未选择会话'}
          </span>
          <span className="text-gray-400">·</span>
          <span className="text-gray-400">{sentenceCount} 句</span>
        </div>

        <ModeToggle isIDEMode={isIDEMode} onToggle={onModeToggle} />
      </div>

      <div className="flex-1 overflow-hidden">
        {sessionId ? (
          <Editor isIDEMode={isIDEMode} content={content} setContent={setContent} />
        ) : (
          <div className="h-full flex items-center justify-center text-gray-400">
            <div className="text-center">
              <FileText size={48} className="mx-auto mb-3 text-gray-300" />
              <p className="text-sm">请从左侧选择或创建一个会话</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
