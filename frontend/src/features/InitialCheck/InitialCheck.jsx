import React from 'react'
import { CheckCircle, AlertCircle, XCircle, Clock } from 'lucide-react'

export const InitialCheck = ({ initialResult }) => {
  // 默认数据
  const defaultResult = {
    timestamp: new Date().toISOString(),
    summary: {
      totalIssues: 3,
      critical: 1,
      warnings: 2,
      passed: 5
    },
    checks: [
      { type: 'structure', status: 'warning', label: '结构完整性', desc: '缺少明确的结论段落' },
      { type: 'logic', status: 'error', label: '逻辑连贯性', desc: '第二段与第三段之间缺少过渡' },
      { type: 'vocabulary', status: 'ok', label: '词汇丰富度', desc: '词汇使用恰当' },
      { type: 'argument', status: 'warning', label: '论证强度', desc: '部分论点缺少论据支撑' },
      { type: 'grammar', status: 'ok', label: '语法正确性', desc: '语法无误' },
    ]
  }
  
  const result = initialResult || defaultResult
  
  const getStatusIcon = (status) => {
    switch (status) {
      case 'ok':
        return <CheckCircle size={14} className="text-green-600" />
      case 'warning':
        return <AlertCircle size={14} className="text-orange-500" />
      case 'error':
        return <XCircle size={14} className="text-red-500" />
      default:
        return null
    }
  }
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'ok':
        return 'bg-green-50 border-green-100 text-green-700'
      case 'warning':
        return 'bg-orange-50 border-orange-100 text-orange-700'
      case 'error':
        return 'bg-red-50 border-red-100 text-red-700'
      default:
        return 'bg-gray-50 border-gray-100 text-gray-700'
    }
  }
  
  return (
    <div className="space-y-3">
      {/* 检查摘要 */}
      <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex items-center gap-2 mb-2">
          <Clock size={14} className="text-gray-500" />
          <span className="text-xs text-gray-500">
            {result.timestamp ? new Date(result.timestamp).toLocaleString('zh-CN') : '初始检查'}
          </span>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <div className="text-lg font-bold text-red-600">{result.summary.critical}</div>
            <div className="text-[10px] text-gray-600">严重问题</div>
          </div>
          <div>
            <div className="text-lg font-bold text-orange-600">{result.summary.warnings}</div>
            <div className="text-[10px] text-gray-600">警告</div>
          </div>
          <div>
            <div className="text-lg font-bold text-green-600">{result.summary.passed}</div>
            <div className="text-[10px] text-gray-600">通过</div>
          </div>
        </div>
      </div>
      
      {/* 检查项列表 */}
      <div className="space-y-2">
        {result.checks.map((check, index) => (
          <div
            key={index}
            className={`p-2.5 rounded-lg border flex items-start gap-2 ${getStatusColor(check.status)}`}
          >
            <div className="flex-shrink-0 mt-0.5">
              {getStatusIcon(check.status)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium">{check.label}</div>
              <div className="text-[10px] mt-0.5 opacity-80">{check.desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

