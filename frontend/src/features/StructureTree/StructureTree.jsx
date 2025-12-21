import React from 'react'
import { CheckCircle, AlertCircle } from 'lucide-react'

export const StructureTree = () => {
  const nodes = [
    { label: '引言', status: 'ok', desc: '结构完整' },
    { label: '论点一', status: 'warning', desc: '缺少论据' },
    { label: '论点二', status: 'ok', desc: '逻辑清晰' },
    { label: '结论', status: 'ok', desc: '呼应主题' },
  ]

  return (
    <div className="relative">
      <div className="absolute left-[15px] top-6 bottom-6 w-0.5 bg-gray-200" />
      
      <div className="space-y-3">
        {nodes.map((node, i) => (
          <div key={i} className="flex items-start gap-3 relative">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 z-10 ${
              node.status === 'ok' ? 'bg-green-100' : 'bg-rose-100'
            }`}>
              {node.status === 'ok' 
                ? <CheckCircle size={16} className="text-green-600" />
                : <AlertCircle size={16} className="text-rose-500" />
              }
            </div>
            <div className={`flex-1 p-3 rounded-xl ${
              node.status === 'ok' ? 'bg-green-50 border border-green-100' : 'bg-rose-50 border border-rose-100'
            }`}>
              <div className={`font-medium text-sm ${
                node.status === 'ok' ? 'text-green-700' : 'text-rose-600'
              }`}>{node.label}</div>
              <div className={`text-xs mt-0.5 ${
                node.status === 'ok' ? 'text-green-600/70' : 'text-rose-500/70'
              }`}>{node.desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
