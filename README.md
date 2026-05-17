# Reddit Stock IQ

A premium financial terminal that scrapes trending stocks from Reddit, enriches them with real-time Yahoo Finance data, and uses Gemini AI to synthesize a structured daily market brief.

## Overview

This project consists of three main components:

1. **Frontend** — A React-based glassmorphic dashboard to view synthesized reports and live market data.
2. **Backend API** — A FastAPI server that orchestrates data ingestion, the RocketRide pipeline, and Gemini synthesis.
3. **Database** — A local ChromaDB instance used to store and semantically retrieve scraped Reddit posts.

---

## Prerequisites

Before installing, make sure you have the following installed on your machine:

- **Python 3.10+**
- **Node.js 18+** and **npm**
- **ChromaDB** — install via pip: `pip install chromadb`
- **Playwright** (for RocketRide browser automation): installed via pip and requires a one-time browser setup
- **RocketRide** — must be running locally with a configured pipeline and dropper endpoint

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/OC-RocketRide-Hackathon-5-16-26/reddit-trendy-db.git
cd reddit-trendy-db
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

Then install the Playwright browser binary (required for RocketRide automation):

```bash
playwright install chromium
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Environment Variables

Create a `.env` file in the project root. The following keys are required:

```env
# RocketRide connection settings
ROCKETRIDE_URI=
ROCKETRIDE_WEBHOOK_URL=
ROCKETRIDE_APIKEY=
ROCKETRIDE_PRIVATE_TOKEN=
ROCKETRIDE_DROPPER_URL=
ROCKETRIDE_DROPPER_KEY=

# Reddit API (optional — used for authenticated requests)
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=python:trendy_stocks_bot:v1.0 (by /u/yourusername)

# Reddit subreddit endpoints (public JSON, no auth required)
REDDIT_HOT_STOCKS=https://www.reddit.com/r/stocks/.json
REDDIT_HOT_WSB=https://www.reddit.com/r/wallstreetbets/.json

# Gemini API key — obtain from Google AI Studio
GEMINI_API_KEY=
```

> **Note**: Your RocketRide keys can be found in your local RocketRide instance settings. Your Gemini API key can be obtained from [Google AI Studio](https://aistudio.google.com).

---

## Running Locally

You will need **three terminal windows** running simultaneously.

### Terminal 1 — Start ChromaDB

ChromaDB must be running on port `8330` before the pipeline can connect to it.

```bash
chroma run --path ./chroma_data --port 8330
```

### Terminal 2 — Start the Backend API

```bash
python3 api.py
```

The API will be available at `http://localhost:8000`.

### Terminal 3 — Start the Frontend

```bash
cd frontend
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

---

## Usage

1. Open the dashboard at `http://localhost:5173`.
2. Click **Run Analysis** to trigger the full pipeline.
3. The pipeline will fetch Reddit posts, process them through RocketRide and ChromaDB, and generate a Gemini-synthesized market brief.
4. The dashboard will update automatically when synthesis is complete.

---

## Features

- **Parallel Scraping** — Fetches 100 hot posts from r/stocks and r/wallstreetbets simultaneously.
- **AI Synthesis** — Gemini 3.1 Flash Lite generates a structured market brief with confidence scores and sentiment analysis.
- **Quote Verification** — A fuzzy-match safety net ensures all extracted post excerpts are real.
- **Yahoo Finance Integration** — Real-time price and daily change data for every trending stock.
- **Live Dashboard** — Premium dark-mode React UI with animated loading states and Buy/Hold/Sell signals.

