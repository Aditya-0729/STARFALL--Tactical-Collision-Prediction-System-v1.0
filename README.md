# 🌌 PROJECT STARFALL
### Tactical AI-Powered Real-Time Space Debris & NEO Collision Prediction System

![Project STARFALL Dashboard](Screenshot/)

---

## Overview

Project STARFALL is a full-stack tactical mission control system that tracks
real near-Earth space debris, satellites, and incoming Near-Earth Objects (NEOs)
in real time. It uses the SGP4 orbital mechanics algorithm to compute live
Cartesian state vectors for 500+ tracked objects, and an LSTM deep learning
model to predict 12-hour trajectories and assess collision probability.

---

## Dashboard Preview

The STARFALL HUD running live with real Space-Track and NASA data:

![HUD Overview](Screenshot/)

**4-Quadrant Layout:**
- **Center** — 3D WebGL globe with live debris particles orbiting Earth
- **Left Panel** — Live Vector Telemetry Matrix (X, Y, Z coordinates, altitude, Pc values)
- **Right Panel** — Risk Assessment Ticker (CRITICAL / WARNING / SAFE events)
- **Bottom Bar** — Chronos Time-Warp Control (1× to 1000× speed simulation)

---

## Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| Next.js 14 | React framework |
| React Three Fiber | 3D WebGL rendering |
| Three.js | Globe, particles, orbit rings |
| Framer Motion | Boot sequence animations |
| Zustand | Global state management |
| Tailwind CSS | Styling |

### Backend
| Technology | Purpose |
|---|---|
| FastAPI | REST API + WebSocket server |
| Python 3.12 | Core language |
| SGP4 | Orbital mechanics propagation |
| PyTorch | LSTM neural network |
| APScheduler | Background ingestion jobs |
| psycopg2 | PostgreSQL connection |
| SQLAlchemy | Async ORM |

### Database
| Technology | Purpose |
|---|---|
| PostgreSQL 15 | Primary database |
| TimescaleDB | Time-series optimization for orbital states |

### Data Sources
| Source | Data |
|---|---|
| Space-Track.org (US Space Force) | TLE orbital elements for 500+ objects |
| NASA NeoWs API | Near-Earth Object close approach data |
| SGP4 Propagator | Real-time Cartesian state vectors |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15 with TimescaleDB extension
- Space-Track.org account (free)
- NASA API key (free from api.nasa.gov)

### 1. Clone the Repository
```bash
git clone https://github.com/Aditya-0729/STARFALL--Tactical-Collision-Prediction-System-v1.0.git
cd starfall
```

### 2. Database Setup

Open pgAdmin 4 and run:
```sql
CREATE USER starfall WITH PASSWORD 'starfall_secret';
CREATE DATABASE starfall_db OWNER starfall;
GRANT ALL PRIVILEGES ON DATABASE starfall_db TO starfall;
```

Then run the schema:
```sql
-- Run contents of backend/app/db/schemas.sql
```

### 3. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\Activate.ps1
# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
# Copy .env.example to .env and fill in your credentials
```

### 4. Environment Variables

Create `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://starfall:starfall_secret@localhost:5432/starfall_db
NASA_API_KEY=your_nasa_api_key
SPACETRACK_USER=your_spacetrack_email
SPACETRACK_PASS=your_spacetrack_password
SECRET_KEY=your_random_secret_key
ENVIRONMENT=development
TLE_INGEST_INTERVAL=3600
NEO_INGEST_INTERVAL=86400
PROPAGATION_INTERVAL=60
AI_PREDICTION_INTERVAL=300
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### 5. Train the AI Model (Optional but Recommended)
```bash
# Run backend first for 30+ minutes to collect orbital data, then:
python -m ml.collect_training_data
python -m ml.train
python -m ml.evaluate
```

### 6. Start the System

**Terminal 1 — Backend:**
```bash
cd backend
.venv\Scripts\Activate.ps1   # Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | System health check |
| GET | `/api/objects/` | List all tracked objects |
| GET | `/api/objects/count` | Object count by type |
| GET | `/api/telemetry/latest` | Latest state vectors |
| GET | `/api/conjunctions/active` | Active conjunction events |
| GET | `/api/conjunctions/critical` | Critical risk events |
| WS | `/ws` | Real-time telemetry stream |

API documentation available at **http://localhost:8000/docs**

---

## AI Model

The LSTM (Long Short-Term Memory) neural network predicts orbital trajectories:

- **Input:** 48 sequential state vectors (4 hours of history at 5-min intervals)
- **Output:** 144 predicted positions (12 hours ahead)
- **Features:** X, Y, Z position (km) + Vx, Vy, Vz velocity (km/s)
- **Architecture:** 2-layer encoder-decoder LSTM, 128 hidden units
- **Training:** ~9,000 sequences from 213 real satellites
- **Best validation error:** ~1050 km over 12 hours

### Risk Classification
| Level | Probability of Collision (Pc) |
|---|---|
| SAFE | Pc < 1×10⁻⁴ |
| WARNING | 1×10⁻⁴ ≤ Pc < 1×10⁻³ |
| CRITICAL | Pc ≥ 1×10⁻³ |

---

## Data Sources

**Space-Track.org** — Operated by the US Space Force 18th Space Defense Squadron.
Provides Two-Line Element (TLE) sets for all tracked Earth-orbiting objects.

**NASA NeoWs** — NASA's Near Earth Object Web Service.
Provides close approach data for asteroids and comets.

**SGP4** — Simplified General Perturbations model 4.
Industry-standard algorithm used by NORAD for orbital propagation.

---

## License

MIT License — see LICENSE file for details.

---

## Acknowledgments

- US Space Force / 18th Space Defense Squadron for Space-Track data
- NASA Center for Near Earth Object Studies (CNEOS)
- Celestrak for orbital mechanics resources
- SGP4 Python library by Brandon Rhodes
