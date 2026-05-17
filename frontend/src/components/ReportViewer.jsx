import ReactMarkdown from 'react-markdown'
import { FileText } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

function AnimatedSection({ children }) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target); // Only animate once
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`section-fade-in ${isVisible ? 'is-visible' : ''}`}
    >
      {children}
    </div>
  );
}

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

  // Split by "## " at the start of a line
  const chunks = content.split(/^## /m);

  return (
    <div className="markdown-body">
      {chunks.map((chunk, index) => {
        if (!chunk.trim()) return null;
        
        // If it's the first chunk and doesn't look like it had a header,
        // it might be the top title or intro.
        const isFirst = index === 0;
        const markdownContent = isFirst ? chunk : `## ${chunk}`;
        
        return (
          <AnimatedSection key={index}>
            <ReactMarkdown>{markdownContent}</ReactMarkdown>
          </AnimatedSection>
        )
      })}
    </div>
  )
}
