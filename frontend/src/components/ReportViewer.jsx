import ReactMarkdown from 'react-markdown'
import { FileText } from 'lucide-react'

export default function ReportViewer({ content, loading }) {
  if (loading) {
    return <div style={{ opacity: 0.5 }}>Loading synthesized brief...</div>
  }

  if (!content) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
        <FileText size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
        <p>No daily brief found.</p>
        <p style={{ fontSize: '0.9rem' }}>Run the pipeline to generate a new report.</p>
      </div>
    )
  }

  return (
    <div className="markdown-body">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  )
}
