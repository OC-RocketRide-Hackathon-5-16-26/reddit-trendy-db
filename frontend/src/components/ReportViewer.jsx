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
    h3: ({ children }) => {
      if (typeof children === 'string') {
        const match = children.match(/(.*)\[Mentions: (\d+), Upvotes: (\d+)\]/);
        if (match) {
          const title = match[1].trim();
          const mentions = match[2];
          const upvotes = match[3];
          return (
            <h3 className="flex justify-between items-center text-xl font-bold text-slate-100 my-4 border-b border-slate-800 pb-2">
              <span>{title}</span>
              <span className="text-sm font-normal text-slate-400 bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700">
                Mentions: <span className="text-emerald-400 font-semibold">{mentions}</span> | Upvotes: <span className="text-emerald-400 font-semibold">{upvotes}</span>
              </span>
            </h3>
          );
        }
      }
      return <h3 className="text-xl font-bold text-slate-100 my-4">{children}</h3>;
    },
    p: ({ children }) => {
      const result = checkSentiment(children);
      if (result) return result;
      return <p className="my-2">{children}</p>;
    },
    li: ({ children }) => {
      const result = checkSentiment(children);
      if (result) return result;
      return <li className="my-2">{children}</li>;
    },
    strong: ({ children }) => {
      if (typeof children === 'string' && children.trim().startsWith('Confidence Score:')) {
        const text = children.trim();
        let colorClass = ''; // Default (inherits from parent)
        
        if (text.includes('(Buy)')) {
          colorClass = 'text-emerald-400';
        } else if (text.includes('(Hold)')) {
          colorClass = 'text-yellow-400';
        } else if (text.includes('(Sell)')) {
          colorClass = 'text-rose-400';
        }
        
        return (
          <span className="relative group cursor-help border-b border-dashed border-slate-500 pb-0.5">
            <strong className={colorClass}>{children}</strong>
            <div className="absolute bottom-full left-0 mb-2 w-64 p-3 bg-slate-900/95 backdrop-blur-md border border-slate-700 rounded-lg shadow-2xl text-xs text-slate-200 opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none transform translate-y-1 group-hover:translate-y-0 z-50">
              <div className="font-semibold text-white mb-1">Confidence Score Scale</div>
              <p className="mb-1"><span className="text-emerald-400 font-bold">4.0 - 5.0</span>: Strong signal to **Buy** (High conviction based on Reddit sentiment & analysis).</p>
              <p className="mb-1"><span className="text-yellow-400 font-bold">2.0 - 4.0</span>: Neutral / Hold (Mixed sentiment or moderate discussion).</p>
              <p><span className="text-rose-400 font-bold">1.0 - 2.0</span>: Strong signal to **Sell** (High negative sentiment or warning signs).</p>
              <div className="absolute w-2 h-2 bg-slate-900 border-r border-b border-slate-700 transform rotate-45 left-4 -bottom-1"></div>
            </div>
          </span>
        );
      }
      return <strong>{children}</strong>;
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
