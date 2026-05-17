# Reddit Trendy DB

A premium financial terminal that scrapes trending stocks from Reddit, enriches them with real-time Yahoo Finance data, and uses Gemini to synthesize a structured "Daily Brief" report.

## Overview

This project consists of three main components:
1. **Frontend**: A React-based glassmorphic dashboard to view the synthesized reports and market data.
2. **Backend API**: A FastAPI server that handles data orchestration and triggers the synthesis pipeline.
3. **Database**: A local ChromaDB instance used to store and retrieve scraped Reddit posts.

## Getting Started Locally

To run this project locally, you need to start three separate services. Open three terminal windows or tabs and run the following commands:

### 1. Start the Chroma Database
Chroma must be running on port 8330 for the pipeline to connect to it.
```bash
chroma run --path ./chroma_data --port 8330
```

### 2. Start the Backend API
The Python API handles the data ingestion, RocketRide integration, and Gemini synthesis.
```bash
python3 api.py
```

### 3. Start the Frontend
Navigate to the frontend directory and start the Vite development server.
```bash
cd frontend
npm run dev
```

## Features
- **Automated Scraping**: Fetches hot posts from r/stocks and r/wallstreetbets.
- **AI Synthesis**: Uses Gemini to rank the top 3 (Trending) and bottom 3 (Angry) stocks.
- **Quote Verification**: A Python safety net ensures extracted quotes are real.
- **Yahoo Finance Integration**: Fetches real-time prices to ensure data accuracy.
