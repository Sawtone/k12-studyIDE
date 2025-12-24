import React, { useState } from 'react'
import { GitBranch, FileCheck, History, Lightbulb, ChevronDown, ChevronUp } from 'lucide-react'
import { AST } from '../features/AST/AST'
import { InitialCheck } from '../features/InitialCheck/InitialCheck'
import { SubsequentCheck } from '../features/SubsequentCheck/SubsequentCheck'
import { FullTextSuggestions } from '../features/FullTextSuggestions/FullTextSuggestions'
import { CompletionStatus } from '../features/CompletionStatus/CompletionStatus'

export const RightPanel = ({ width, analysisData, content, editorRef, onSendToChat }) => {
  const [expandedSections, setExpandedSections] = useState({
    ast: true,
    initialCheck: true,
    subsequentCheck: true,
    suggestions: true
  })
  
  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }
  
  // 处理AST节点点击，高亮编辑器内容
  const handleASTNodeClick = (text) => {
    console.log('AST node clicked, text:', text)
    console.log('Editor ref:', editorRef)
    console.log('Editor ref current:', editorRef?.current)
    
    if (editorRef?.current?.highlightNode) {
      console.log('Calling highlightNode')
      editorRef.current.highlightNode(text)
    } else {
      console.log('highlightNode method not available')
    }
  }
  
  // 处理发送建议到Chat
  const handleSendToChat = (suggestion) => {
    if (onSendToChat) {
      const message = `关于"${suggestion.title}"的建议：${suggestion.description}${suggestion.examples && suggestion.examples.length > 0 ? '\n\n示例：' + suggestion.examples.join('\n') : ''}`
      onSendToChat(message)
    }
  }
  
  const SectionHeader = ({ icon: Icon, title, isExpanded, onToggle }) => (
    <div
      onClick={onToggle}
      className="flex items-center justify-between px-3 py-2 cursor-pointer hover:bg-gray-50 transition-colors border-b border-gray-100"
    >
      <div className="flex items-center gap-2">
        <Icon size={14} className="text-indigo-500" />
        <span className="text-xs font-semibold text-gray-700">{title}</span>
      </div>
      {isExpanded ? (
        <ChevronUp size={14} className="text-gray-400" />
      ) : (
        <ChevronDown size={14} className="text-gray-400" />
      )}
    </div>
  )
  
  return (
    <div className="bg-white border-l border-gray-200 flex flex-col overflow-hidden" style={{ width }}>
      {/* AST - 文章结构树 */}
      <div className="flex flex-col border-b border-gray-100 overflow-hidden">
        <SectionHeader
          icon={GitBranch}
          title="AST"
          isExpanded={expandedSections.ast}
          onToggle={() => toggleSection('ast')}
        />
        {expandedSections.ast && (
          <div className="flex-1 p-2 overflow-auto" style={{ maxHeight: '300px' }}>
            <AST 
              astData={analysisData?.ast} 
              content={content}
              onNodeClick={handleASTNodeClick}
            />
          </div>
        )}
      </div>
      
      {/* 初始检查结果 */}
      <div className="flex flex-col border-b border-gray-100 overflow-hidden">
        <SectionHeader
          icon={FileCheck}
          title="初始检查结果"
          isExpanded={expandedSections.initialCheck}
          onToggle={() => toggleSection('initialCheck')}
        />
        {expandedSections.initialCheck && (
          <div className="flex-1 p-4 overflow-auto max-h-[200px]">
            <InitialCheck initialResult={analysisData?.initialCheck} />
          </div>
        )}
      </div>
      
      {/* 后续检查结果 */}
      <div className="flex flex-col border-b border-gray-100 overflow-hidden">
        <SectionHeader
          icon={History}
          title="后续检查结果"
          isExpanded={expandedSections.subsequentCheck}
          onToggle={() => toggleSection('subsequentCheck')}
        />
        {expandedSections.subsequentCheck && (
          <div className="flex-1 p-4 overflow-auto max-h-[200px]">
            <SubsequentCheck subsequentResults={analysisData?.subsequentChecks} />
          </div>
        )}
      </div>
      
      {/* 完成状态 */}
      {analysisData && (
        <div className="p-3 border-b border-gray-100">
          <CompletionStatus analysisData={analysisData} />
        </div>
      )}
      
      {/* 全文建议 */}
      <div className="flex flex-col flex-1 overflow-hidden">
        <SectionHeader
          icon={Lightbulb}
          title="全文建议"
          isExpanded={expandedSections.suggestions}
          onToggle={() => toggleSection('suggestions')}
        />
        {expandedSections.suggestions && (
          <div className="flex-1 p-4 overflow-auto">
            <FullTextSuggestions 
              suggestions={analysisData?.suggestions} 
              onSendToChat={handleSendToChat}
            />
          </div>
        )}
      </div>
    </div>
  )
}
