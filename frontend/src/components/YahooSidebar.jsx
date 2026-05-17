import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

export default function YahooSidebar({ data, loading }) {
  if (loading) {
    return <div style={{ opacity: 0.5 }}>Fetching latest market data...</div>
  }

  if (!data || data.length === 0) {
    return <div style={{ opacity: 0.5 }}>No market data available.</div>
  }

  // Duplicate data for seamless loop
  const displayData = [...data, ...data];

  return (
    <div className="carousel-track">
      {displayData.map((ticker, index) => {
        const isPositive = ticker.change_percent > 0
        const isNegative = ticker.change_percent < 0
        
        return (
          <div key={`${ticker.symbol}-${index}`} className="carousel-item">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: '700', fontSize: '1rem' }}>{ticker.symbol}</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>${ticker.price.toFixed(2)}</div>
              </div>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '4px',
                color: isPositive ? 'var(--accent-color)' : isNegative ? 'var(--danger-color)' : 'var(--text-secondary)',
                fontWeight: '600'
              }}>
                {isPositive && <TrendingUp size={16} />}
                {isNegative && <TrendingDown size={16} />}
                {!isPositive && !isNegative && <Minus size={16} />}
                {Math.abs(ticker.change_percent).toFixed(2)}%
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
