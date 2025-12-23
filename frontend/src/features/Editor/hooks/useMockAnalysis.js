import { useState, useCallback } from 'react'
import { MOCK_ANALYSIS_RESPONSE, simulateApiDelay } from '../mockData.js'

export const useMockAnalysis = (editor) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [hasAnalyzed, setHasAnalyzed] = useState(false)

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

      setHasAnalyzed(true)
    } catch (error) {
      console.error('Analysis failed:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }, [editor])

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
  }, [editor])

  return { isAnalyzing, hasAnalyzed, runAnalysis, clearAnalysis }
}
