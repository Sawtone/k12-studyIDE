import React from 'react'
import { motion } from 'framer-motion'
import { AlertCircle } from 'lucide-react'

export const HealthCheck = () => {
  const metrics = [
    { label: '词汇丰富度', value: 72, color: 'bg-indigo-500' },
    { label: '逻辑连贯性', value: 58, color: 'bg-orange-400' },
    { label: '论证强度', value: 85, color: 'bg-green-500' },
  ]

  return (
    <div className="space-y-4">
      {metrics.map((m, i) => (
        <div key={i}>
          <div className="flex justify-between text-sm mb-1.5">
            <span className="text-gray-600">{m.label}</span>
            <span className="font-medium text-gray-700">{m.value}%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${m.value}%` }}
              transition={{ duration: 0.8, delay: i * 0.15 }}
              className={`h-full ${m.color} rounded-full`}
            />
          </div>
        </div>
      ))}
      
      <div className="mt-5 p-3 bg-orange-50 rounded-xl border border-orange-100">
        <div className="flex items-start gap-2">
          <AlertCircle size={16} className="text-orange-500 flex-shrink-0 mt-0.5" />
          <div>
            <div className="font-medium text-orange-700 text-sm">改进建议</div>
            <div className="text-xs text-orange-600/80 mt-1 leading-relaxed">
              第二句和第三句之间缺少逻辑过渡，建议添加连接词。
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
