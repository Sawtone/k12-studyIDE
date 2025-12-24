import { useState, useCallback } from 'react'
import { MOCK_ANALYSIS_RESPONSE, simulateApiDelay } from '../mockData.js'

// 生成AST数据
const generateAST = (editor) => {
  const paragraphs = []
  let currentPara = { sentences: [] }
  
  editor.state.doc.descendants((node) => {
    if (node.type.name === 'cognitiveParagraph') {
      const text = node.textContent.trim()
      if (text) {
        currentPara.sentences.push({
          type: 'sentence',
          label: text.length > 30 ? text.substring(0, 30) + '...' : text,
          text: text, // 保存完整文本用于高亮
          status: node.attrs.aiLabel === 'logic-gap' ? 'warning' : 'ok'
        })
      }
    } else if (node.type.name === 'paragraphDivider') {
      if (currentPara.sentences.length > 0) {
        paragraphs.push(currentPara)
        currentPara = { sentences: [] }
      }
    }
  })
  
  if (currentPara.sentences.length > 0) {
    paragraphs.push(currentPara)
  }
  
  return {
    type: 'document',
    label: '文档根节点',
    children: paragraphs.map((para, index) => ({
      type: 'paragraph',
      label: `段落 ${index + 1}`,
      meta: `${para.sentences.length} 句`,
      status: para.sentences.some(s => s.status === 'warning') ? 'warning' : 'ok',
      children: para.sentences
    }))
  }
}

// 生成初始检查结果
const generateInitialCheck = (editor) => {
  const blocks = []
  editor.state.doc.descendants((node) => {
    if (node.type.name === 'cognitiveParagraph' && node.attrs.aiLabel) {
      blocks.push(node.attrs.aiLabel)
    }
  })
  
  const hasLogicGap = blocks.includes('logic-gap')
  const hasEvidence = blocks.includes('evidence')
  const hasTopic = blocks.includes('topic')
  
  return {
    timestamp: new Date().toISOString(),
    summary: {
      totalIssues: (hasLogicGap ? 1 : 0) + (hasEvidence ? 0 : 1),
      critical: hasLogicGap ? 1 : 0,
      warnings: hasEvidence ? 0 : 1,
      passed: 5
    },
    checks: [
      { type: 'structure', status: hasTopic ? 'ok' : 'warning', label: '结构完整性', desc: hasTopic ? '结构完整' : '缺少明确的主题' },
      { type: 'logic', status: hasLogicGap ? 'error' : 'ok', label: '逻辑连贯性', desc: hasLogicGap ? '存在逻辑断层' : '逻辑连贯' },
      { type: 'vocabulary', status: 'ok', label: '词汇丰富度', desc: '词汇使用恰当' },
      { type: 'argument', status: hasEvidence ? 'ok' : 'warning', label: '论证强度', desc: hasEvidence ? '论证充分' : '缺少论据支撑' },
      { type: 'grammar', status: 'ok', label: '语法正确性', desc: '语法无误' },
    ]
  }
}

// 生成后续检查结果
const generateSubsequentChecks = (isFirstCheck) => {
  if (isFirstCheck) return []
  
  return [
    {
      timestamp: new Date(Date.now() - 300000).toISOString(),
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
    }
  ]
}

// 生成全文建议
const generateSuggestions = (editor) => {
  const blocks = []
  editor.state.doc.descendants((node) => {
    if (node.type.name === 'cognitiveParagraph' && node.attrs.aiLabel) {
      blocks.push({ type: node.attrs.aiLabel, suggestion: node.attrs.aiSuggestion })
    }
  })
  
  const suggestions = []
  
  if (blocks.some(b => b.type === 'logic-gap')) {
    suggestions.push({
      type: 'logic',
      priority: 'high',
      title: '加强段落过渡',
      description: '部分段落之间缺少逻辑连接，建议添加过渡句。',
      examples: [
        '可以添加：尽管人工智能带来了诸多便利，但我们也不能忽视其潜在风险...'
      ]
    })
  }
  
  if (blocks.some(b => b.type === 'evidence')) {
    suggestions.push({
      type: 'content',
      priority: 'medium',
      title: '补充具体案例',
      description: '在论述时可以添加具体的使用场景或案例以增强说服力。',
      examples: [
        '例如：在线教育平台利用AI个性化推荐学习内容，帮助学生更高效地掌握知识...'
      ]
    })
  }
  
  suggestions.push({
    type: 'structure',
    priority: 'medium',
    title: '完善文章结构',
    description: '建议在文章末尾添加总结段落，呼应开头并升华主题。',
    examples: [
      '可以这样写：综上所述，人工智能的发展需要我们既保持开放态度，又保持谨慎...'
    ]
  })
  
  return suggestions
}

export const useMockAnalysis = (editor) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [hasAnalyzed, setHasAnalyzed] = useState(false)
  const [analysisData, setAnalysisData] = useState(null)
  const [isFirstCheck, setIsFirstCheck] = useState(true)

  const runAnalysis = useCallback(async () => {
    if (!editor) return

    setIsAnalyzing(true)
    
    try {
      await simulateApiDelay(800)
      
      const response = MOCK_ANALYSIS_RESPONSE
      const paragraphs = []
      
      editor.state.doc.descendants((node, pos) => {
        if (node.type.name === 'cognitiveParagraph') {
          const text = node.textContent.trim()
          if (text) {
            paragraphs.push({
              pos,
              text,
              uuid: node.attrs.uuid || `block-${pos}`,
            })
          }
        }
      })

      const matchBlock = (text) => {
        return response.blocks.find(block => {
          if (block.matchText) {
            return text.includes(block.matchText) || block.matchText.includes(text.slice(0, 20))
          }
          return false
        }) || null
      }

      const { tr } = editor.state
      let modified = false

      paragraphs.forEach(({ pos, text, uuid }) => {
        const matchedBlock = matchBlock(text)
        
        if (matchedBlock) {
          const node = editor.state.doc.nodeAt(pos)
          if (node) {
            tr.setNodeMarkup(pos, undefined, {
              ...node.attrs,
              uuid,
              aiLabel: matchedBlock.type,
              aiSuggestion: matchedBlock.suggestion,
            })
            modified = true
          }
        }
      })

      if (modified) {
        editor.view.dispatch(tr)
      }

      // 生成完整的分析数据
      const fullAnalysisData = {
        ast: generateAST(editor),
        initialCheck: isFirstCheck ? generateInitialCheck(editor) : null,
        subsequentChecks: generateSubsequentChecks(isFirstCheck),
        suggestions: generateSuggestions(editor)
      }
      
      setAnalysisData(fullAnalysisData)
      setHasAnalyzed(true)
      setIsFirstCheck(false)
    } catch (error) {
      console.error('Analysis failed:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }, [editor, isFirstCheck])

  const clearAnalysis = useCallback(() => {
    if (!editor) return
    
    const { tr } = editor.state
    
    editor.state.doc.descendants((node, pos) => {
      if (node.type.name === 'cognitiveParagraph' && node.attrs.aiLabel) {
        tr.setNodeMarkup(pos, undefined, {
          ...node.attrs,
          aiLabel: null,
          aiSuggestion: null,
        })
      }
    })
    
    editor.view.dispatch(tr)
    setHasAnalyzed(false)
    setAnalysisData(null)
    setIsFirstCheck(true)
  }, [editor])

  return { 
    isAnalyzing, 
    hasAnalyzed, 
    runAnalysis, 
    clearAnalysis,
    analysisData 
  }
}
