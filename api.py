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
    """Runs the main.py pipeline and waits for completion"""
    print("API Triggered: Running the data pipeline...")
    import subprocess
    # Using run instead of Popen to block until completed
    subprocess.run(["python3", "main.py"])

@app.post("/api/run", response_model=StatusResponse)
def trigger_run():
    run_pipeline()
    return {"status": "success", "message": "Pipeline completed successfully."}

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

@app.post("/api/webhook/report")
async def receive_report(data: dict):
    """Receives the report from RocketRide and saves it to a file"""
    print("Received report from RocketRide!")
    
    # Extract the answers field
    answers = data.get("answers", "")
    if not answers:
        # Fallback if the whole payload is the answer or structured differently
        answers = json.dumps(data, indent=2)
        
    os.makedirs("reports", exist_ok=True)
    with open("reports/daily_brief.md", "w", encoding="utf-8") as f:
        f.write(answers)
        
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
