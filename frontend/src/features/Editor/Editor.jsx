import { TiptapEditor } from './components/TiptapEditor'
import { WritingEditor } from './components/WritingEditor'

export const Editor = ({ isIDEMode, content, setContent }) => {
  if (!isIDEMode) {
    return <WritingEditor content={content} onChange={setContent} />
  }

  return <TiptapEditor content={content} onChange={setContent} isIDEMode={isIDEMode} />
}
