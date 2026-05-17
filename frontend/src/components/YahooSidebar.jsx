import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

export default function YahooSidebar({ data, loading }) {
  if (loading) {
    return <div className="text-slate-400 text-center py-4">Fetching latest market data...</div>
  }

  if (!data || data.length === 0) {
    return <div className="text-slate-500 text-center py-4">No market data available.</div>
  }

  return (
    <div className="carousel-absolute-wrapper">
      {/* Moving container */}
      <div className="ticker-list animate-scroll-vertical hover:[animation-play-state:paused] max-md:flex-row max-md:animate-scroll-horizontal max-md:w-max">
        
        {/* Carousel 1 */}
        <div className="ticker-list max-md:flex-row max-md:gap-6">
          {data.map((ticker) => {
            const isPositive = ticker.change_percent > 0
            const isNegative = ticker.change_percent < 0
            
            return (
              <div key={`c1-${ticker.symbol}`} className="ticker-item max-md:w-[200px] max-md:flex-shrink-0">
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

        {/* Carousel 2 */}
        <div className="ticker-list max-md:flex-row max-md:gap-6">
          {data.map((ticker) => {
            const isPositive = ticker.change_percent > 0
            const isNegative = ticker.change_percent < 0
            
            return (
              <div key={`c2-${ticker.symbol}`} className="ticker-item max-md:w-[200px] max-md:flex-shrink-0">
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

        {/* Carousel 3 */}
        <div className="ticker-list max-md:flex-row max-md:gap-6">
          {data.map((ticker) => {
            const isPositive = ticker.change_percent > 0
            const isNegative = ticker.change_percent < 0
            
            return (
              <div key={`c3-${ticker.symbol}`} className="ticker-item max-md:w-[200px] max-md:flex-shrink-0">
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

        {/* Carousel 4 */}
        <div className="ticker-list max-md:flex-row max-md:gap-6">
          {data.map((ticker) => {
            const isPositive = ticker.change_percent > 0
            const isNegative = ticker.change_percent < 0
            
            return (
              <div key={`c4-${ticker.symbol}`} className="ticker-item max-md:w-[200px] max-md:flex-shrink-0">
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

      </div>
    </div>
  )
}
