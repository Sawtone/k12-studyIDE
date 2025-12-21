import React from 'react'
import { WritingMode } from './WritingMode'
import { IDEMode } from './IDEMode'

export const Editor = ({ isIDEMode, content, setContent }) => {
  const sentences = content.split(/(?<=[。！？])/g).filter(s => s.trim())

  const handleIDEChange = (index, newValue) => {
    const newSentences = [...sentences]
    newSentences[index] = newValue
    setContent(newSentences.join(''))
  }

  if (!isIDEMode) {
    return <WritingMode content={content} setContent={setContent} />
  }

  return <IDEMode sentences={sentences} onSentenceChange={handleIDEChange} />
}
