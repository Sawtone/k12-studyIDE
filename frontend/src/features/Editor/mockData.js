export const SAMPLE_CONTENT = `人工智能正在改变世界。它帮助我们更快地学习新知识。然而，我们必须谨慎对待它的发展。`

export const MOCK_ANALYSIS_RESPONSE = {
  success: true,
  documentId: 'doc-001',
  timestamp: new Date().toISOString(),
  blocks: [
    {
      type: 'topic',
      startPos: 0,
      endPos: 50,
      suggestion: '核心观点清晰',
      matchText: '人工智能正在改变世界',
    },
    {
      type: 'evidence',
      startPos: 51,
      endPos: 100,
      suggestion: '可补充具体案例',
      matchText: '它帮助我们更快地学习新知识',
    },
    {
      type: 'logic-gap',
      startPos: 101,
      endPos: 150,
      suggestion: '过渡需加强',
      matchText: '然而，我们必须谨慎对待它的发展',
    },
  ],
}

export const simulateApiDelay = (ms = 500) => {
  return new Promise(resolve => setTimeout(resolve, ms))
}
