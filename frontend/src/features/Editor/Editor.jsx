import { WritingMode } from './WritingMode.jsx'
import { IDEMode } from './IDEMode.jsx'

export const Editor = ({ isIDEMode, content, setContent }) => {
  if (isIDEMode) {
    return <IDEMode content={content} onContentChange={setContent} />
  }
  
  return <WritingMode content={content} onContentChange={setContent} />
}
