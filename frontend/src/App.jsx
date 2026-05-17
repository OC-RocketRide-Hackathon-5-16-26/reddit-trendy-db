import { useState, useEffect } from 'react'
import { Activity } from 'lucide-react'
import ReportViewer from './components/ReportViewer'
import YahooSidebar from './components/YahooSidebar'
import PipelineTrigger from './components/PipelineTrigger'

function App() {
  const [report, setReport] = useState(null)
  const [yahooData, setYahooData] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [reportRes, yahooRes] = await Promise.all([
        fetch('http://localhost:8000/api/report').catch(() => null),
        fetch('http://localhost:8000/api/yahoo').catch(() => null)
      ])

      if (reportRes && reportRes.ok) {
        const data = await reportRes.json()
        setReport(data.content)
      }
      
      if (yahooRes && yahooRes.ok) {
        const data = await yahooRes.json()
        setYahooData(data.data)
      }
    } catch (error) {
      console.error("Failed to fetch data", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div className="app-container">
      <header className="header">
        <h1 className="title">
          <Activity size={32} style={{ display: 'inline', marginRight: '10px', color: '#8a2be2' }} />
          Trendy Stocks Terminal
        </h1>
        <PipelineTrigger onTriggerComplete={fetchData} />
      </header>
      
      <main className="main-content">
        <div className="glass-panel">
          <h2 className="panel-title">AI Synthesized Brief</h2>
          <ReportViewer content={report} loading={loading} />
        </div>
        
        <div className="glass-panel">
          <h2 className="panel-title">Market Overview</h2>
          <YahooSidebar data={yahooData} loading={loading} />
        </div>
      </main>
    </div>
  )
}

export default App
