import { createContext, useContext } from 'react'

export const EditorRefContext = createContext(null)

export const useEditorRef = () => {
  const context = useContext(EditorRefContext)
  return context
}

