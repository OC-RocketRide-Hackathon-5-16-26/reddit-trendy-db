import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

export default function YahooSidebar({ data, loading }) {
  if (loading) {
    return <div style={{ opacity: 0.5 }}>Fetching latest market data...</div>
  }

  if (!data || data.length === 0) {
    return <div style={{ opacity: 0.5 }}>No market data available.</div>
  }

  return (
    <div className="ticker-list">
      {data.map((ticker) => {
        const isPositive = ticker.change_percent > 0
        const isNegative = ticker.change_percent < 0
        
        return (
          <div key={ticker.symbol} className="ticker-item">
            <div>
              <div className="ticker-symbol">{ticker.symbol}</div>
              <div className="ticker-price">${ticker.price.toFixed(2)}</div>
            </div>
            <div className={`ticker-change ${isPositive ? 'change-positive' : isNegative ? 'change-negative' : ''}`}>
              {isPositive && <TrendingUp size={16} />}
              {isNegative && <TrendingDown size={16} />}
              {!isPositive && !isNegative && <Minus size={16} />}
              {Math.abs(ticker.change_percent).toFixed(2)}%
            </div>
          </div>
        )
      })}
    </div>
  )
}
