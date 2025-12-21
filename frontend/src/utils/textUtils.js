export const calculateWordCount = (text) => {
  return text.length
}

export const calculateSentenceCount = (text) => {
  return text.split(/(?<=[。！？])/g).filter(s => s.trim()).length
}

export const calculateReadingTime = (wordCount) => {
  return Math.max(1, Math.ceil(wordCount / 300))
}
