import React from 'react'
import { GitBranch, Lightbulb } from 'lucide-react'
import { StructureTree } from '../features/StructureTree/StructureTree'
import { HealthCheck } from '../features/HealthCheck/HealthCheck'

export const RightPanel = ({ width }) => {
  return (
    <div className="bg-white border-l border-gray-200 flex flex-col overflow-hidden" style={{ width }}>
      <div className="flex-1 p-4 border-b border-gray-100 overflow-auto">
        <div className="flex items-center gap-2 mb-4 text-gray-700">
          <GitBranch size={16} className="text-indigo-500" />
          <span className="font-semibold text-sm">结构分析</span>
        </div>
        <StructureTree />
      </div>
      
      <div className="flex-1 p-4 overflow-auto">
        <div className="flex items-center gap-2 mb-4 text-gray-700">
          <Lightbulb size={16} className="text-indigo-500" />
          <span className="font-semibold text-sm">写作健康度</span>
        </div>
        <HealthCheck />
      </div>
    </div>
  )
}
