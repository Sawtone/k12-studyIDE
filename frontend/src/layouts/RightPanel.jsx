import { GitBranch, Lightbulb, SpellCheck, Sparkles } from 'lucide-react'
import { StructureTree } from '../features/StructureTree/StructureTree'
import { HealthCheck } from '../features/HealthCheck/HealthCheck'
import { GrammarCheck } from '../features/GrammarCheck/GrammarCheck'
import { TextPolish } from '../features/TextPolish/TextPolish'
import { useState } from 'react'

const tabs = [
  { id: 'structure', label: '结构', icon: GitBranch },
  { id: 'health', label: '健康度', icon: Lightbulb },
  { id: 'grammar', label: '语法', icon: SpellCheck },
  { id: 'polish', label: '润色', icon: Sparkles },
]

export const RightPanel = ({ width, sessionId, content }) => {
  const [activeTab, setActiveTab] = useState('structure')

  return (
    <div className="bg-white border-l border-gray-200 flex flex-col overflow-hidden" style={{ width }}>
      {/* Tab 切换 */}
      <div className="flex border-b border-gray-100 px-2 pt-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium rounded-t-lg transition-colors ${
                isActive
                  ? 'bg-gray-50 text-indigo-600 border-b-2 border-indigo-500 -mb-px'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Icon size={12} />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* 内容区域 */}
      <div className="flex-1 overflow-auto p-3">
        {activeTab === 'structure' && <StructureTree sessionId={sessionId} content={content} />}
        {activeTab === 'health' && <HealthCheck sessionId={sessionId} content={content} />}
        {activeTab === 'grammar' && <GrammarCheck sessionId={sessionId} content={content} />}
        {activeTab === 'polish' && <TextPolish sessionId={sessionId} content={content} />}
      </div>
    </div>
  )
}
