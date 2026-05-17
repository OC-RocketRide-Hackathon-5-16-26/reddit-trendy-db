import os
import json
import subprocess
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow the Vite frontend (port 5173) to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StatusResponse(BaseModel):
    status: str
    message: str

def run_pipeline():
    """Runs the main.py pipeline in the background"""
    print("API Triggered: Running the data pipeline...")
    # Using subprocess to run the existing orchestration script
    subprocess.Popen(["python3", "main.py"])

@app.post("/api/run", response_model=StatusResponse)
async def trigger_run(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_pipeline)
    return {"status": "success", "message": "Pipeline triggered successfully. It will take a few moments to generate the brief."}

@app.get("/api/report")
async def get_report():
    report_path = "reports/daily_brief.md"
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not generated yet.")
    
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    return {"content": content}

@app.get("/api/yahoo")
async def get_yahoo_data():
    yahoo_path = "data/yahoo_trending.json"
    if not os.path.exists(yahoo_path):
        return {"data": []}
        
    with open(yahoo_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return {"data": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
