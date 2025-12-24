import React, { useState } from 'react'
import { CheckCircle, AlertCircle, XCircle, TrendingUp, TrendingDown, Minus } from 'lucide-react'

export const SubsequentCheck = ({ subsequentResults }) => {
  const [selectedIndex, setSelectedIndex] = useState(0)
  
  // 默认数据
  const defaultResults = [
    {
      timestamp: new Date(Date.now() - 300000).toISOString(), // 5分钟前
      summary: {
        totalIssues: 2,
        critical: 0,
        warnings: 2,
        passed: 6
      },
      improvements: [
        { type: 'structure', status: 'improved', label: '结构完整性', desc: '已添加结论段落' },
        { type: 'logic', status: 'improved', label: '逻辑连贯性', desc: '添加了过渡句' },
      ]
    },
    {
      timestamp: new Date().toISOString(),
      summary: {
        totalIssues: 1,
        critical: 0,
        warnings: 1,
        passed: 7
      },
      improvements: [
        { type: 'argument', status: 'improved', label: '论证强度', desc: '补充了具体案例' },
      ]
    }
  ]
  
  const results = subsequentResults || defaultResults
  
  if (results.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400 text-sm">
        暂无后续检查结果
      </div>
    )
  }
  
  const currentResult = results[selectedIndex]
  const previousResult = selectedIndex > 0 ? results[selectedIndex - 1] : null
  
  const getStatusIcon = (status) => {
    switch (status) {
      case 'improved':
        return <TrendingUp size={14} className="text-green-600" />
      case 'regressed':
        return <TrendingDown size={14} className="text-red-600" />
      case 'unchanged':
        return <Minus size={14} className="text-gray-400" />
      default:
        return null
    }
  }
  
  const getChangeColor = (status) => {
    switch (status) {
      case 'improved':
        return 'bg-green-50 border-green-200 text-green-700'
      case 'regressed':
        return 'bg-red-50 border-red-200 text-red-700'
      case 'unchanged':
        return 'bg-gray-50 border-gray-200 text-gray-600'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }
  
  const compareSummary = (current, previous) => {
    if (!previous) return null
    
    return {
      totalIssues: current.totalIssues - previous.totalIssues,
      critical: current.critical - previous.critical,
      warnings: current.warnings - previous.warnings,
      passed: current.passed - previous.passed,
    }
  }
  
  const changes = compareSummary(currentResult.summary, previousResult?.summary)
  
  return (
    <div className="space-y-3">
      {/* 检查历史选择 */}
      {results.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-2">
          {results.map((result, index) => (
            <button
              key={index}
              onClick={() => setSelectedIndex(index)}
              className={`px-3 py-1.5 rounded-lg text-xs whitespace-nowrap transition-all ${
                selectedIndex === index
                  ? 'bg-indigo-100 text-indigo-700 font-medium'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              检查 #{index + 1}
            </button>
          ))}
        </div>
      )}
      
      {/* 当前检查摘要 */}
      <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-gray-500">
            {new Date(currentResult.timestamp).toLocaleString('zh-CN')}
          </span>
          {changes && (
            <div className="flex items-center gap-1 text-xs">
              {changes.totalIssues < 0 && (
                <span className="text-green-600">↓ {Math.abs(changes.totalIssues)}</span>
              )}
              {changes.totalIssues > 0 && (
                <span className="text-red-600">↑ {changes.totalIssues}</span>
              )}
            </div>
          )}
        </div>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <div className="text-lg font-bold text-red-600">{currentResult.summary.critical}</div>
            <div className="text-[10px] text-gray-600">严重问题</div>
          </div>
          <div>
            <div className="text-lg font-bold text-orange-600">{currentResult.summary.warnings}</div>
            <div className="text-[10px] text-gray-600">警告</div>
          </div>
          <div>
            <div className="text-lg font-bold text-green-600">{currentResult.summary.passed}</div>
            <div className="text-[10px] text-gray-600">通过</div>
          </div>
        </div>
      </div>
      
      {/* 改进项列表 */}
      {currentResult.improvements && currentResult.improvements.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-medium text-gray-700 mb-2">改进项：</div>
          {currentResult.improvements.map((improvement, index) => (
            <div
              key={index}
              className={`p-2.5 rounded-lg border flex items-start gap-2 ${getChangeColor(improvement.status)}`}
            >
              <div className="flex-shrink-0 mt-0.5">
                {getStatusIcon(improvement.status)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium">{improvement.label}</div>
                <div className="text-[10px] mt-0.5 opacity-80">{improvement.desc}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

