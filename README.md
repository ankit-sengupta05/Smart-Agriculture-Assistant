<div align="center">

<!-- Animated Banner SVG -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:004d1a,50:00cc6a,100:00ff88&height=220&section=header&text=🌾%20PlantGuard&fontSize=60&fontColor=ffffff&fontAlignY=38&desc=Smart%20Agriculture%20Intelligence%20System&descAlignY=58&descSize=18&animation=fadeIn" width="100%"/>

<!-- Typing SVG -->
<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=Space+Mono&size=16&pause=1000&color=00FF88&center=true&vCenter=true&width=600&lines=🧠+ML+Yield+Prediction+%7C+TensorFlow+%2B+scikit-learn;👁️+Disease+Detection+%7C+OpenCV+Computer+Vision;⚗️+REST+API+%7C+Flask+%2B+SQLite;⚛️+React+Dashboard+%7C+Vite+%2B+JSX;🔐+Role-Based+Auth+%7C+Farmer+%26+Buyer" alt="Typing SVG" />
</a>

<br/><br/>

<!-- Tech Badges -->
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-REST_API-000000?style=for-the-badge&logo=flask&logoColor=00FF88)
![TensorFlow](https://img.shields.io/badge/TensorFlow-ML-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![React](https://img.shields.io/badge/React-Dashboard-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-Build-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-Pipeline-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

<br/>

<!-- Status Badges -->
![Status](https://img.shields.io/badge/Status-Active-00FF88?style=flat-square&logo=statuspage&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-:5000-00CC6A?style=flat-square&logo=flask)
![Frontend](https://img.shields.io/badge/Frontend-:5173-61DAFB?style=flat-square&logo=react)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

---

## ◈ Overview

**PlantGuard** is a full-stack AI-powered agricultural intelligence platform that combines machine learning, computer vision, and a modern REST API to help farmers predict crop yields, detect plant diseases, and access a digital marketplace — all in one system.

```
┌─────────────────────────────────────────────────────────┐
│                    PlantGuard System                    │
│                                                         │
│   React Dashboard  ←→  Flask API  ←→  SQLite DB        │
│         ↕                  ↕                            │
│   Yield Predictor    Disease Scanner                    │
│   (TF + sklearn)     (OpenCV + CV2)                     │
└─────────────────────────────────────────────────────────┘
```

---

## ◈ Features

| Module | Technology | Description |
|--------|-----------|-------------|
| 🧠 **Yield Prediction** | TensorFlow + Pandas | 13-feature ML inference pipeline |
| 👁️ **Disease Detection** | OpenCV + CV2 | Image-based pathogen classification |
| ⚗️ **REST API** | Flask + Flask-CORS | Token-authenticated JSON endpoints |
| 🗄️ **Marketplace** | SQLite | Searchable crop listing database |
| 🔐 **Auth System** | JWT-style tokens | Role-based farmer / buyer access |
| ⚛️ **Dashboard** | React + Vite | Hot-reloaded SPA frontend |

---

## ◈ Project Structure

```
PlantGuard/
│
├── backend/
│   ├── __init__.py                  ← marks as Python package
│   ├── app.py                       ← Flask REST API entry point
│   ├── agri.db                      ← SQLite DB (auto-created on first run)
│   │
│   ├── ml_pipeline/
│   │   ├── __init__.py
│   │   └── yield_predictor.py       ← TensorFlow + Pandas ML pipeline
│   │
│   └── vision/
│       ├── __init__.py
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

## ◈ Quick Start

### 1 · Backend — Flask API

```powershell
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install flask flask-cors numpy pandas opencv-python scikit-learn

# Run the API (from inside backend/ folder)
cd backend
python app.py
```

**Expected output:**

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

### 2 · Frontend — React + Vite

Open a **second terminal:**

```powershell
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## ◈ API Reference

### 🔓 Authentication

```powershell
# Login — returns Bearer token
curl -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username":"ramesh_farmer","password":"demo123"}'
```

### 📋 Listings

```powershell
# All listings
curl http://localhost:5000/api/listings

# Filter by crop type
curl "http://localhost:5000/api/listings?crop_type=rice"

# Keyword search
curl "http://localhost:5000/api/listings?search=wheat"
```

### 🧠 Yield Prediction  `🔐 auth required`

```powershell
curl -X POST http://localhost:5000/api/predict/yield `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer TOKEN" `
  -d '{
    "crop_type":           "wheat",
    "area_hectares":       10,
    "planting_date":       "2025-01-01",
    "soil_type":           "loam",
    "irrigation_type":     "drip",
    "rainfall_mm":         550,
    "temperature_avg":     22,
    "temperature_min":     14,
    "temperature_max":     32,
    "humidity_percent":    65,
    "solar_radiation":     18,
    "fertilizer_kg_per_ha":120,
    "pesticide_applications":2
  }'
```

### 👁️ Disease Scan  `🔐 auth required`

```powershell
curl -X POST http://localhost:5000/api/scan/disease `
  -H "Authorization: Bearer TOKEN" `
  -F "image=@path\to\crop_photo.jpg"
```

---

## ◈ Endpoint Summary

```
POST  /api/auth/login            →  Authenticate, receive token
GET   /api/listings              →  All crop listings
GET   /api/listings?crop_type=   →  Filter by crop
GET   /api/listings?search=      →  Full-text search
POST  /api/predict/yield    🔐   →  ML yield forecast (13 features)
POST  /api/scan/disease     🔐   →  CV disease classification
```

---

## ◈ Demo Accounts

| Username | Password | Role |
|----------|----------|------|
| `ramesh_farmer` | `demo123` | 🌱 Farmer |
| `sarah_buyer` | `demo123` | 🛒 Buyer |
| `carlos_grower` | `demo123` | 🌱 Farmer |
| `amina_trade` | `demo123` | 🛒 Buyer |

> **Farmers** can post listings, run yield predictions, and scan for disease.
> **Buyers** can browse and search the marketplace.

---

## ◈ ML Yield Predictor — Input Features

```python
{
  # Crop Identity
  "crop_type"              : "wheat",      # string
  "area_hectares"          : 10,           # float

  # Field Conditions
  "planting_date"          : "2025-01-01", # ISO date
  "soil_type"              : "loam",       # string
  "irrigation_type"        : "drip",       # string

  # Weather Data
  "rainfall_mm"            : 550,          # float
  "temperature_avg"        : 22,           # °C
  "temperature_min"        : 14,           # °C
  "temperature_max"        : 32,           # °C
  "humidity_percent"       : 65,           # 0–100
  "solar_radiation"        : 18,           # MJ/m²/day

  # Inputs
  "fertilizer_kg_per_ha"   : 120,          # float
  "pesticide_applications" : 2             # int
}
```

---

## ◈ Tech Stack

```
Backend          Flask 2.x · Python 3 · Flask-CORS
Database         SQLite (auto-initialised) · Pandas DataFrames
Machine Learning TensorFlow · scikit-learn · NumPy · Pandas
Computer Vision  OpenCV (cv2)
Frontend         React 18 · Vite · JSX
Package Mgmt     pip · npm
```

---

<div align="center">

<!-- Footer wave -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00ff88,100:004d1a&height=100&section=footer" width="100%"/>

**🌾 PlantGuard** — Built with Flask · TensorFlow · OpenCV · React · SQLite

</div>
