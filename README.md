# 🌾 PlantGuard — Smart Agriculture Assistant

## Project Structure

```
PlantGuard/
│
├── backend/
│   ├── __init__.py                  ← required (marks as Python package)
│   ├── app.py                       ← Flask REST API entry point
│   ├── agri.db                      ← SQLite DB (auto-created on first run)
│   │
│   ├── ml_pipeline/
│   │   ├── __init__.py              ← required
│   │   └── yield_predictor.py       ← TensorFlow + Pandas ML pipeline
│   │
│   └── vision/
│       ├── __init__.py              ← required
│       └── disease_detector.py      ← OpenCV disease detection
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       └── App.jsx                  ← React dashboard
│
├── requirements.txt
└── README.md
```

---

## Quick Start

### Backend (Flask API)

```powershell
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install flask flask-cors numpy pandas opencv-python scikit-learn

# 3. Run the API  (from inside the backend/ folder)
cd backend
python app.py
```

You should see:
```
🌾 PlantGuard — Smart Agriculture API
──────────────────────────────────────
  Database initialised at ...agri.db
  Demo data seeded (4 users, 4 listings)
  Server starting on http://localhost:5000
  Demo login  →  ramesh_farmer / demo123  (farmer)
              →  sarah_buyer   / demo123  (buyer)
──────────────────────────────────────
```

---

### Frontend (React + Vite)

Open a **second terminal**:

```powershell
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## API Usage

### Login
```powershell
curl -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username":"ramesh_farmer","password":"demo123"}'
```

### Get listings
```powershell
curl http://localhost:5000/api/listings
curl "http://localhost:5000/api/listings?crop_type=rice"
curl "http://localhost:5000/api/listings?search=wheat"
```

### Predict yield  (replace TOKEN with value from login)
```powershell
curl -X POST http://localhost:5000/api/predict/yield `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer TOKEN" `
  -d '{
    "crop_type":"wheat",
    "area_hectares":10,
    "planting_date":"2025-01-01",
    "soil_type":"loam",
    "irrigation_type":"drip",
    "rainfall_mm":550,
    "temperature_avg":22,
    "temperature_min":14,
    "temperature_max":32,
    "humidity_percent":65,
    "solar_radiation":18,
    "fertilizer_kg_per_ha":120,
    "pesticide_applications":2
  }'
```

### Scan disease image
```powershell
curl -X POST http://localhost:5000/api/scan/disease `
  -H "Authorization: Bearer TOKEN" `
  -F "image=@path\to\crop_photo.jpg"
```

---

## Demo Accounts

| Username       | Password  | Role   |
|----------------|-----------|--------|
| ramesh_farmer  | demo123   | farmer |
| sarah_buyer    | demo123   | buyer  |
| carlos_grower  | demo123   | farmer |
| amina_trade    | demo123   | buyer  |
