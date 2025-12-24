import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { CognitiveParagraph } from './extensions/CognitiveParagraph.jsx'
import { useMockAnalysis } from './hooks/useMockAnalysis.js'
import { Sparkles, RotateCcw, Loader2 } from 'lucide-react'
import React, { useEffect, useImperativeHandle, forwardRef, useRef } from 'react'

// 将文本按句子分割转换为 HTML（IDE模式不显示段落分隔，只按句子分割）
const textToSentenceHtml = (text) => {
  if (!text) return '<p></p>'
  
  // 移除所有换行符，按句子分割（句号、问号、叹号、省略号）
  const normalizedText = text.replace(/\n+/g, ' ')
  const sentences = normalizedText.split(/(?<=[。！？…])/g).filter(s => s.trim())
  
  if (sentences.length === 0) return '<p></p>'
  
  return sentences.map(s => `<p>${s.trim()}</p>`).join('')
}

// 从编辑器提取文本（IDE模式：保留段落结构）
const extractTextFromEditor = (editor, originalContent) => {
  const allSentences = []
  const emptyPositions = [] // 记录空节点的位置
  
  editor.state.doc.forEach((node, pos) => {
    if (node.type.name === 'cognitiveParagraph') {
      const text = node.textContent.trim()
      if (text) {
        let sentence = text
        // 如果句子不以中文标点结尾，自动添加句号
        if (!/[。！？…]$/.test(sentence)) {
          sentence += '。'
        }
        allSentences.push({ text: sentence, pos })
      } else {
        // 记录空节点的位置
        emptyPositions.push(pos)
      }
    }
  })
  
  // 如果原始content有段落结构，尝试保持段落结构
  if (originalContent) {
    const originalParagraphs = originalContent.split(/\n\n+/).filter(p => p.trim())
    if (originalParagraphs.length > 1) {
      // 计算原始每个段落的句子数
      const originalSentenceCounts = originalParagraphs.map(para => {
        return para.split(/(?<=[。！？…])/g).filter(s => s.trim()).length
      })
      
      // 根据原始段落结构分配当前句子
      const newParagraphs = []
      let sentenceIndex = 0
      
      for (let i = 0; i < originalSentenceCounts.length; i++) {
        const paraSentences = []
        const targetCount = originalSentenceCounts[i]
        
        // 尝试分配目标数量的句子
        for (let j = 0; j < targetCount && sentenceIndex < allSentences.length; j++) {
          paraSentences.push(allSentences[sentenceIndex].text)
          sentenceIndex++
        }
        
        if (paraSentences.length > 0) {
          newParagraphs.push(paraSentences)
        }
      }
      
      // 如果还有剩余句子，添加到最后一个段落
      if (sentenceIndex < allSentences.length) {
        const remaining = allSentences.slice(sentenceIndex).map(s => s.text)
        if (remaining.length > 0) {
          if (newParagraphs.length > 0) {
            newParagraphs[newParagraphs.length - 1].push(...remaining)
          } else {
            newParagraphs.push(remaining)
          }
        }
      }
      
      if (newParagraphs.length > 1) {
        return newParagraphs.map(p => p.join('')).join('\n\n')
      } else if (newParagraphs.length === 1) {
        return newParagraphs[0].join(' ')
      }
    }
  }
  
  // 如果没有原始段落结构，尝试通过空节点识别段落
  if (emptyPositions.length > 0 && allSentences.length > 0) {
    const paragraphs = []
    let currentPara = []
    let lastEmptyPos = -1
    
    allSentences.forEach(({ text, pos }) => {
      // 检查这个句子之前是否有空节点（可能是段落分隔）
      const hasEmptyBefore = emptyPositions.some(emptyPos => emptyPos < pos && emptyPos > lastEmptyPos)
      
      if (hasEmptyBefore && currentPara.length > 0) {
        // 开始新段落
        paragraphs.push(currentPara)
        currentPara = [text]
        lastEmptyPos = emptyPositions.find(emptyPos => emptyPos < pos) || lastEmptyPos
      } else {
        currentPara.push(text)
      }
    })
    
    if (currentPara.length > 0) {
      paragraphs.push(currentPara)
    }
    
    if (paragraphs.length > 1) {
      return paragraphs.map(p => p.join('')).join('\n\n')
    }
  }
  
  // 默认：所有句子作为一个段落
  if (allSentences.length > 0) {
    return allSentences.map(s => s.text).join(' ')
  }
  
  return ''
}

export const IDEMode = forwardRef(({ content, onContentChange, onAnalysisDataChange }, ref) => {
  // 保存原始content的段落结构
  const originalContentRef = React.useRef(content)
  
  React.useEffect(() => {
    originalContentRef.current = content
  }, [content])
  
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        paragraph: false,
        heading: false,
        bulletList: false,
        orderedList: false,
        listItem: false,
        blockquote: false,
        codeBlock: false,
        horizontalRule: false,
      }),
      CognitiveParagraph,
      // 移除ParagraphDivider，IDE模式不显示段落分隔符
      Placeholder.configure({
        placeholder: '开始写作，让 AI 帮你分析文章结构...',
        emptyEditorClass: 'is-editor-empty',
      }),
    ],
    content: textToSentenceHtml(content),
    editorProps: {
      attributes: {
        class: 'ide-editor-content outline-none min-h-[400px] py-6 px-4',
      },
    },
    onUpdate: ({ editor }) => {
      const text = extractTextFromEditor(editor, originalContentRef.current)
      onContentChange(text)
    },
  })

  const { isAnalyzing, hasAnalyzed, runAnalysis, clearAnalysis, analysisData } = useMockAnalysis(editor)

  // 暴露编辑器方法给父组件
  useImperativeHandle(ref, () => ({
    highlightNode: (text) => {
      if (!editor) {
        console.warn('Editor not available for highlighting')
        return
      }
      
      const searchText = text.trim()
      console.log('🔍 Searching for text:', searchText)
      
      // 查找包含该文本的节点
      let targetPos = null
      let targetNode = null
      
      editor.state.doc.descendants((node, pos) => {
        if (node.type.name === 'cognitiveParagraph') {
          const nodeText = node.textContent.trim()
          
          // 多种匹配策略
          const exactMatch = nodeText === searchText
          const includesMatch = nodeText.includes(searchText) || searchText.includes(nodeText)
          
          // 移除标点符号后比较（更宽松的匹配）
          const normalize = (str) => str.replace(/[。！？，、\s]/g, '')
          const normalizedMatch = normalize(nodeText) === normalize(searchText) ||
                                   normalize(nodeText).includes(normalize(searchText)) ||
                                   normalize(searchText).includes(normalize(nodeText))
          
          if (exactMatch || includesMatch || normalizedMatch) {
            targetPos = pos
            targetNode = node
            console.log('✅ Found node at pos:', pos, 'text:', nodeText)
            return false // 停止遍历
          }
        }
      })
      
      if (targetPos !== null && targetNode) {
        console.log('🎯 Highlighting node at position:', targetPos)
        
        // 使用requestAnimationFrame确保DOM已更新
        requestAnimationFrame(() => {
          setTimeout(() => {
            try {
              const domNode = editor.view.nodeDOM(targetPos)
              
              if (!domNode) {
                console.warn('DOM node not found for position:', targetPos)
                return
              }
              
              // 查找cognitive-block容器
              let element = domNode
              if (domNode instanceof Text) {
                element = domNode.parentElement
              }
              
              if (element instanceof HTMLElement) {
                // 优先查找cognitive-block
                let blockElement = element.closest('.cognitive-block')
                
                // 如果没找到，尝试向上查找包含data-line属性的元素
                if (!blockElement) {
                  let current = element
                  while (current && current !== editor.view.dom) {
                    if (current.classList?.contains('cognitive-block') || 
                        current.hasAttribute('data-line')) {
                      blockElement = current
                      break
                    }
                    current = current.parentElement
                  }
                }
                
                // 如果还是没找到，使用content-column
                if (!blockElement) {
                  blockElement = element.closest('.content-column') || element
                }
                
                if (blockElement) {
                  console.log('✨ Highlighting element:', blockElement)
                  
                  // 只添加高亮样式，不滚动
                  blockElement.classList.add('highlighted-node')
                  
                  // 2秒后移除高亮
                  setTimeout(() => {
                    blockElement.classList.remove('highlighted-node')
                  }, 2000)
                } else {
                  console.warn('Could not find block element to highlight')
                }
              }
            } catch (error) {
              console.error('Error highlighting node:', error)
            }
          }, 50)
        })
      } else {
        console.warn('❌ Node not found for text:', searchText)
        // 打印所有节点文本以便调试
        const allTexts = []
        editor.state.doc.descendants((node) => {
          if (node.type.name === 'cognitiveParagraph') {
            allTexts.push(node.textContent.trim())
          }
        })
        console.log('Available node texts:', allTexts)
      }
    },
    getEditor: () => editor
  }), [editor])

  // 当分析数据变化时，通知父组件
  useEffect(() => {
    if (analysisData && onAnalysisDataChange) {
      onAnalysisDataChange(analysisData)
    }
  }, [analysisData, onAnalysisDataChange])

  // 当 content 从外部变化时同步
  useEffect(() => {
    if (editor && !editor.isFocused) {
      const currentTexts = []
      editor.state.doc.descendants((node) => {
        if (node.type.name === 'cognitiveParagraph' && node.textContent.trim()) {
          currentTexts.push(node.textContent.trim())
        }
      })
      const currentContent = currentTexts.join('')
      
      if (currentContent !== content) {
        editor.commands.setContent(textToSentenceHtml(content))
      }
    }
  }, [content, editor])

  return (
    <div className="ide-mode-container h-full flex flex-col">
      {/* Toolbar */}
      <div className="ide-toolbar flex items-center justify-end gap-2 px-4 py-2 border-b border-gray-100 bg-gray-50/50">
        {hasAnalyzed && (
          <button
            onClick={clearAnalysis}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-all"
          >
            <RotateCcw size={12} />
            <span>清除标注</span>
          </button>
        )}
        
        <button
          onClick={runAnalysis}
          disabled={isAnalyzing}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${
            isAnalyzing 
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
              : 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white hover:shadow-md'
          }`}
        >
          {isAnalyzing ? (
            <>
              <Loader2 size={12} className="animate-spin" />
              <span>分析中...</span>
            </>
          ) : (
            <>
              <Sparkles size={12} />
              <span>AI 结构分析</span>
            </>
          )}
        </button>
      </div>

      {/* Editor Canvas */}
      <div 
        className="ide-canvas flex-1 overflow-auto"
        style={{
          backgroundColor: '#f8fafc',
        }}
      >
        <div className="py-4">
          <EditorContent editor={editor} />
        </div>
      </div>
    </div>
  )
})

IDEMode.displayName = 'IDEMode'
