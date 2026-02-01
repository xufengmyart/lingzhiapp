import React, { useState } from 'react'
import ReactQuill from 'react-quill'
import 'react-quill/dist/quill.snow.css'

interface MobileRichEditorProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  height?: string
  readOnly?: boolean
}

const MobileRichEditor: React.FC<MobileRichEditorProps> = ({
  value,
  onChange,
  placeholder = '开始输入...',
  height = '300px',
  readOnly = false
}) => {
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)

  // 监听窗口大小变化
  React.useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768)
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // 移动端精简工具栏
  const mobileModules = {
    toolbar: [
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline'],
      [{ 'list': 'ordered' }, { 'list': 'bullet' }],
      ['clean']
    ]
  }

  // 桌面端完整工具栏
  const desktopModules = {
    toolbar: [
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      [{ 'font': [] }],
      [{ 'size': ['small', false, 'large', 'huge'] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'list': 'ordered' }, { 'list': 'bullet' }],
      [{ 'align': [] }],
      ['link', 'image', 'video'],
      ['clean']
    ]
  }

  const modules = isMobile ? mobileModules : desktopModules

  const formats = [
    'header', 'font', 'size',
    'bold', 'italic', 'underline', 'strike',
    'color', 'background',
    'list', 'bullet',
    'align',
    'link', 'image', 'video'
  ]

  return (
    <div className="mobile-rich-editor">
      <style>{`
        .mobile-rich-editor .ql-container {
          min-height: ${height};
          font-size: 16px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
            'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
            sans-serif;
        }
        
        .mobile-rich-editor .ql-toolbar {
          border-radius: 8px 8px 0 0;
          border-color: #e5e7eb;
          background-color: #f9fafb;
        }
        
        .mobile-rich-editor .ql-container {
          border-radius: 0 0 8px 8px;
          border-color: #e5e7eb;
        }
        
        /* 移动端优化 */
        @media (max-width: 768px) {
          .mobile-rich-editor .ql-toolbar .ql-formats {
            margin-right: 0;
            margin-bottom: 8px;
          }
          
          .mobile-rich-editor .ql-toolbar button {
            padding: 6px 8px;
            min-width: 32px;
          }
          
          .mobile-rich-editor .ql-editor {
            font-size: 16px;
            line-height: 1.6;
          }
        }
        
        /* iOS Safari 防止双击缩放 */
        .mobile-rich-editor .ql-editor {
          -webkit-touch-callout: none;
          -webkit-user-select: text;
          user-select: text;
        }
      `}</style>
      
      <ReactQuill
        value={value}
        onChange={onChange}
        modules={modules}
        formats={formats}
        placeholder={placeholder}
        readOnly={readOnly}
        style={{ height }}
      />
    </div>
  )
}

export default MobileRichEditor
