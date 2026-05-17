import { FileText, Star, AlertTriangle, Quote } from 'lucide-react'

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

  // Parser functions
  function parseStocks(sectionText) {
    const blocks = sectionText.split(/^### /m).slice(1);
    return blocks.map(block => {
      const lines = block.split('\n');
      const header = lines[0].trim(); // "1. Microsoft (MSFT)"
      const stockName = header.replace(/^\d+\.\s+/, '');
      
      const confidenceLine = lines.find(l => l.includes('Confidence Score'));
      const confidence = confidenceLine ? confidenceLine.split(':')[1].trim() : 'N/A';
      
      const explanationLine = lines.find(l => l.includes('Explanation'));
      const explanation = explanationLine ? explanationLine.split('**')[2].trim() : '';
      
      const perfLine = lines.find(l => l.includes('Actual Market Performance'));
      const performance = perfLine ? perfLine.split('**')[2].trim() : '';
      
      return { stockName, confidence, explanation, performance };
    });
  }

  function parseQuotes(sectionText) {
    const lines = sectionText.split('\n');
    return lines.filter(l => l.trim().startsWith('*')).map(l => l.trim().replace(/^\*\s+/, ''));
  }

  const sections = content.split(/^## /m);
  let trending = [];
  let angry = [];
  let quotes = [];

  sections.forEach(section => {
    if (section.startsWith('Trending')) {
      trending = parseStocks(section);
    } else if (section.startsWith('Angry')) {
      angry = parseStocks(section);
    } else if (section.startsWith('Representative Quotes')) {
      quotes = parseQuotes(section);
    }
  });

  return (
    <div className="report-container">
      {/* Trending Section */}
      <div className="section-group">
        <h3 className="section-header" style={{ color: 'var(--accent-color)' }}>
          <Star size={18} style={{ marginRight: '8px' }} /> Trending Stocks
        </h3>
        {trending.map((stock, index) => (
          <details key={index} className="stock-details">
            <summary>
              <span>{stock.stockName}</span>
              <span className="confidence-badge">{stock.confidence}</span>
            </summary>
            <div className="accordion-content">
              <p><strong>Explanation:</strong> {stock.explanation}</p>
              <p><strong>Market Performance:</strong> {stock.performance}</p>
            </div>
          </details>
        ))}
      </div>

      {/* Angry Section */}
      <div className="section-group" style={{ marginTop: '20px' }}>
        <h3 className="section-header" style={{ color: 'var(--danger-color)' }}>
          <AlertTriangle size={18} style={{ marginRight: '8px' }} /> Angry Stocks
        </h3>
        {angry.map((stock, index) => (
          <details key={index} className="stock-details">
            <summary>
              <span>{stock.stockName}</span>
              <span className="confidence-badge badge-danger">{stock.confidence}</span>
            </summary>
            <div className="accordion-content">
              <p><strong>Explanation:</strong> {stock.explanation}</p>
              <p><strong>Market Performance:</strong> {stock.performance}</p>
            </div>
          </details>
        ))}
      </div>

      {/* Quotes Section */}
      {quotes.length > 0 && (
        <div className="section-group" style={{ marginTop: '20px' }}>
          <h3 className="section-header">
            <Quote size={18} style={{ marginRight: '8px' }} /> Representative Quotes
          </h3>
          <div className="quotes-list">
            {quotes.map((quote, index) => (
              <div key={index} className="quote-item">
                {quote}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
