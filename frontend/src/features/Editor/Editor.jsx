import { WritingMode } from './WritingMode.jsx'
import { IDEMode } from './IDEMode.jsx'

export const Editor = ({ isIDEMode, content, setContent, sessionId, inspiration, setInspiration }) => {
  if (isIDEMode) {
    return <IDEMode content={content} onContentChange={setContent} sessionId={sessionId} />
  }

  return (
    <WritingMode
      content={content}
      onContentChange={setContent}
      sessionId={sessionId}
      inspiration={inspiration}
      setInspiration={setInspiration}
    />
  )
}
