import { useState } from 'react'
import { Play, Loader2 } from 'lucide-react'

export default function PipelineTrigger({ onTriggerStart, onTriggerComplete }) {
  const [running, setRunning] = useState(false)
  
  const handleTrigger = async () => {
    setRunning(true)
    if (onTriggerStart) onTriggerStart()
    try {
      const res = await fetch('http://localhost:8000/api/run', { method: 'POST' })
      await res.json()
      
      setRunning(false)
      onTriggerComplete()
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
          Run Analysis
        </>
      )}
    </button>
  )
}
