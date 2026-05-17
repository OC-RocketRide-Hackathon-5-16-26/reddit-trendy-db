import { useState } from 'react'
import { Play, Loader2 } from 'lucide-react'

export default function PipelineTrigger({ onTriggerComplete }) {
  const [running, setRunning] = useState(false)
  
  const handleTrigger = async () => {
    setRunning(true)
    try {
      const res = await fetch('http://localhost:8000/api/run', { method: 'POST' })
      const data = await res.json()
      
      // The python script takes roughly ~20-30 seconds to run completely.
      // We'll wait 30 seconds before we automatically refetch the data
      setTimeout(() => {
        setRunning(false)
        onTriggerComplete()
      }, 30000)
      
    } catch (error) {
      console.error("Failed to trigger pipeline", error)
      setRunning(false)
    }
  }
  
  return (
    <button 
      onClick={handleTrigger} 
      disabled={running}
      className="trigger-btn"
    >
      {running ? (
        <>
          <Loader2 size={18} className="spinner" />
          Processing Pipeline (30s)...
        </>
      ) : (
        <>
          <Play size={18} fill="currentColor" />
          Run Agents
        </>
      )}
    </button>
  )
}
