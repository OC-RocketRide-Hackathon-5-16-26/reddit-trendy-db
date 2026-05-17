import ReactMarkdown from 'react-markdown'
import { FileText, TrendingUp, TrendingDown } from 'lucide-react'
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
  // If loading and no content yet, show initial loading state
  if (loading && !content) {
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

  const renderItem = (text, rest, type) => {
    const Icon = type === 'positive' ? TrendingUp : TrendingDown;
    const colorClass = type === 'positive' ? 'change-positive' : 'change-negative';
    return (
      <div className="sentiment-item flex items-center gap-2 my-2 text-[0.95rem]">
        <Icon className={`${colorClass} flex-shrink-0`} size={16} />
        <span>
          {text}
          {rest}
        </span>
      </div>
    )
  };

  const checkSentiment = (children) => {
    if (!children) return null;
    const firstChild = children[0];
    
    // Case 1: First child is a string
    if (typeof firstChild === 'string') {
      const text = firstChild.trim();
      
      if (text.startsWith('[POSITIVE]')) {
        return renderItem(text.slice(10), children.slice(1), 'positive');
      }
      if (text.startsWith('[NEGATIVE]')) {
        return renderItem(text.slice(10), children.slice(1), 'negative');
      }
    }
    
    // Case 2: First child is a React element (like a <p> tag inside an <li>)
    if (firstChild && typeof firstChild === 'object' && firstChild.props) {
      const pChildren = firstChild.props.children;
      if (Array.isArray(pChildren) && typeof pChildren[0] === 'string') {
        const text = pChildren[0].trim();
        
        if (text.startsWith('[POSITIVE]')) {
          return renderItem(text.slice(10), pChildren.slice(1), 'positive');
        }
        if (text.startsWith('[NEGATIVE]')) {
          return renderItem(text.slice(10), pChildren.slice(1), 'negative');
        }
      } else if (typeof pChildren === 'string') {
        const text = pChildren.trim();
        
        if (text.startsWith('[POSITIVE]')) {
          return renderItem(text.slice(10), null, 'positive');
        }
        if (text.startsWith('[NEGATIVE]')) {
          return renderItem(text.slice(10), null, 'negative');
        }
      }
    }
    
    return null;
  };

  // Custom renderer to replace sentiment markers with Lucide icons
  const markdownComponents = {
    p: ({ children }) => {
      const result = checkSentiment(children);
      if (result) return result;
      return <p className="my-2">{children}</p>;
    },
    li: ({ children }) => {
      const result = checkSentiment(children);
      if (result) return result;
      return <li className="my-2">{children}</li>;
    }
  };

  return (
    <div className="loading-container">
      {/* Sharp loading bar at the top */}
      {loading && <div className="loading-bar"></div>}
      
      {/* Blurred content during loading */}
      <div className={`markdown-body ${loading ? 'loading-blur' : ''}`}>
        {chunks.map((chunk, index) => {
          if (!chunk.trim()) return null;
          
          const isFirst = index === 0;
          const markdownContent = isFirst ? chunk : `## ${chunk}`;
          
          return (
            <AnimatedSection key={index}>
              <ReactMarkdown components={markdownComponents}>
                {markdownContent}
              </ReactMarkdown>
            </AnimatedSection>
          )
        })}
      </div>
    </div>
  )
}
