<div align="center">

<!-- ═══════════════════════════════════════════════════════════ -->
<!--                     ANIMATED HEADER                       -->
<!-- ═══════════════════════════════════════════════════════════ -->

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:001a08,30:003d12,60:00a846,100:00ff88&height=280&section=header&text=🌾%20PlantGuard&fontSize=72&fontColor=ffffff&fontAlignY=40&fontAlign=50&desc=Smart%20Agriculture%20Intelligence%20System&descSize=20&descAlignY=60&descAlign=50&animation=fadeIn&stroke=00ff88&strokeWidth=1" width="100%"/>

<br/>

<!-- Typing Animation -->
<a href="https://git.io/typing-svg">
<img src="https://readme-typing-svg.demolab.com?font=Space+Mono&weight=700&size=15&duration=2800&pause=800&color=00FF88&background=00000000&center=true&vCenter=true&multiline=false&width=700&height=40&lines=🧠+ML+Yield+Prediction+powered+by+TensorFlow;👁️+Real-Time+Disease+Detection+via+OpenCV;⚗️+Production-Ready+Flask+REST+API;⚛️+Modern+React+%2B+Vite+Dashboard;🌱+Empowering+Farmers+with+AI+Intelligence" alt="Typing SVG" />
</a>

<br/><br/>

<!-- ─── BADGE ROW 1 — Technologies ─── -->
<p>
<img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Flask-REST_API-000000?style=for-the-badge&logo=flask&logoColor=00FF88"/>
<img src="https://img.shields.io/badge/TensorFlow-ML_Engine-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white"/>
<img src="https://img.shields.io/badge/OpenCV-Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white"/>
</p>
<p>
<img src="https://img.shields.io/badge/React_18-Dashboard-61DAFB?style=for-the-badge&logo=react&logoColor=black"/>
<img src="https://img.shields.io/badge/Vite-Build_Tool-646CFF?style=for-the-badge&logo=vite&logoColor=white"/>
<img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
<img src="https://img.shields.io/badge/scikit--learn-Pipeline-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white"/>
</p>

<!-- ─── BADGE ROW 2 — Status ─── -->
<p>
<img src="https://img.shields.io/badge/Backend-%3A5000-00FF88?style=flat-square&logo=flask&logoColor=white"/>
<img src="https://img.shields.io/badge/Frontend-%3A5173-61DAFB?style=flat-square&logo=react&logoColor=white"/>
<img src="https://img.shields.io/badge/Status-Active-00FF88?style=flat-square&logo=statuspage&logoColor=white"/>
<img src="https://img.shields.io/badge/Auth-JWT_Style-orange?style=flat-square&logo=jsonwebtokens&logoColor=white"/>
<img src="https://img.shields.io/badge/ML_Features-13-blueviolet?style=flat-square&logo=tensorflow&logoColor=white"/>
<img src="https://img.shields.io/badge/License-MIT-green?style=flat-square"/>
</p>

</div>

---

<div align="center">

## `◈ System Architecture`

</div>

```
╔══════════════════════════════════════════════════════════════════╗
║                    🌾  PlantGuard  v1.0                         ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   ┌─────────────────┐         ┌──────────────────┐              ║
║   │  ⚛️  React SPA  │ ──────► │  ⚗️  Flask API   │             ║
║   │   Vite + JSX    │ ◄────── │   :5000          │              ║
║   │   :5173         │         └────────┬─────────┘              ║
║   └─────────────────┘                  │                         ║
║                              ┌─────────┼──────────┐             ║
║                              ▼         ▼          ▼             ║
║                        ┌──────────┐ ┌──────┐ ┌────────────┐    ║
║                        │🧠 Yield  │ │🗄️ DB │ │👁️ Disease  │   ║
║                        │Predictor │ │SQLite│ │ Detector   │    ║
║                        │TF+sklearn│ │      │ │  OpenCV    │    ║
║                        └──────────┘ └──────┘ └────────────┘    ║
╚══════════════════════════════════════════════════════════════════╝
```

---

<div align="center">

## `◈ Core Features`

</div>

<table>
<tr>
<td width="50%">

### 🧠 &nbsp; ML Yield Prediction
> **TensorFlow · scikit-learn · Pandas**

Feed 13 agronomic inputs — soil type, irrigation method, rainfall, temperature range, humidity, solar radiation, fertilizer load — and get a calibrated harvest forecast powered by a deep learning pipeline.

</td>
<td width="50%">

### 👁️ &nbsp; Disease Detection
> **OpenCV · Computer Vision**

Upload any crop photo. The vision module analyzes leaf texture, color patterns, and morphology to classify pathogens instantly — giving farmers an early warning system in their pocket.

</td>
</tr>
<tr>
<td width="50%">

### ⚗️ &nbsp; REST API
> **Flask · Flask-CORS · JSON**

A clean, documented API with Bearer token authentication. All prediction and scan endpoints are protected. Public listing endpoints support filtering and full-text search out of the box.

</td>
<td width="50%">

### 🗄️ &nbsp; Crop Marketplace
> **SQLite · Auto-seeded**

A role-aware digital marketplace. Farmers post crop listings; buyers browse and filter. Database auto-initializes and seeds on first run — zero config required.

</td>
</tr>
<tr>
<td width="50%">

### 🔐 &nbsp; Role-Based Auth
> **Farmer · Buyer · JWT-style Tokens**

Two distinct user roles with scoped permissions. Token-based sessions protect sensitive AI endpoints. Seeded with 4 demo accounts across both roles — ready to test immediately.

</td>
<td width="50%">

### ⚛️ &nbsp; React Dashboard
> **React 18 · Vite · JSX**

A hot-reloaded single-page application. Prediction forms, disease scan interface, listing browser — all wired to the backend API. Fast dev loop, clean component architecture.

</td>
</tr>
</table>

---

<div align="center">

## `◈ Project Structure`

</div>

```
🌾 PlantGuard/
│
├── 📁 backend/
│   ├── 🐍 __init__.py                ← marks as Python package
│   ├── 🐍 app.py                     ← Flask REST API entry point
│   ├── 🗄️ agri.db                   ← SQLite DB (auto-created on first run)
│   │
│   ├── 📁 ml_pipeline/
│   │   ├── 🐍 __init__.py
│   │   └── 🧠 yield_predictor.py    ← TensorFlow + Pandas ML pipeline
│   │
│   └── 📁 vision/
│       ├── 🐍 __init__.py
│       └── 👁️ disease_detector.py  ← OpenCV disease detection
│
├── 📁 frontend/
│   ├── 🌐 index.html
│   ├── 📦 package.json
│   ├── ⚡ vite.config.js
│   └── 📁 src/
│       ├── ⚛️ main.jsx
│       └── ⚛️ App.jsx              ← React dashboard
│
├── 📄 requirements.txt
└── 📖 README.md
```

---

<div align="center">

## `◈ Quick Start`

<img src="https://readme-typing-svg.demolab.com?font=Space+Mono&size=13&pause=1500&color=00E5CC&center=true&width=500&lines=Get+up+and+running+in+under+2+minutes...;Two+terminals.+That%27s+all+you+need." alt="Typing SVG" />

</div>

### ![](https://img.shields.io/badge/STEP_01-Backend_%E2%80%94_Flask_API-00FF88?style=for-the-badge&logo=flask&logoColor=black)

```powershell
# ── Create and activate virtual environment ──────────────
python -m venv venv
venv\Scripts\activate

# ── Install all dependencies ──────────────────────────────
pip install flask flask-cors numpy pandas opencv-python scikit-learn

# ── Start the API  (run from inside backend/ folder) ─────
cd backend
python app.py
```

<details>
<summary>📟 &nbsp; Expected terminal output</summary>

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

</details>

<br/>

### ![](https://img.shields.io/badge/STEP_02-Frontend_%E2%80%94_React_+_Vite-61DAFB?style=for-the-badge&logo=react&logoColor=black)

> Open a **second terminal** — keep the backend running

```powershell
cd frontend
npm install       # install node modules
npm run dev       # start dev server → http://localhost:5173
```

---

<div align="center">

## `◈ API Reference`

<img src="https://readme-typing-svg.demolab.com?font=Space+Mono&size=13&pause=2000&color=FFB830&center=true&width=500&lines=All+endpoints+return+JSON.;Protected+routes+require+Authorization+header." alt="Typing SVG" />

</div>

### 🔓 &nbsp; Authentication

```powershell
curl -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username":"ramesh_farmer","password":"demo123"}'
```

> Returns a Bearer token — use it in the `Authorization` header for protected routes.

---

### 📋 &nbsp; Listings &nbsp; ![](https://img.shields.io/badge/PUBLIC-no_auth_needed-4CAF50?style=flat-square)

```powershell
# ── All listings ──────────────────────────────────────────
curl http://localhost:5000/api/listings

# ── Filter by crop type ───────────────────────────────────
curl "http://localhost:5000/api/listings?crop_type=rice"

# ── Full-text keyword search ──────────────────────────────
curl "http://localhost:5000/api/listings?search=wheat"
```

---

### 🧠 &nbsp; Yield Prediction &nbsp; ![](https://img.shields.io/badge/🔐_AUTH-required-FF6F00?style=flat-square)

```powershell
curl -X POST http://localhost:5000/api/predict/yield `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer TOKEN" `
  -d '{
    "crop_type"              : "wheat",
    "area_hectares"          : 10,
    "planting_date"          : "2025-01-01",
    "soil_type"              : "loam",
    "irrigation_type"        : "drip",
    "rainfall_mm"            : 550,
    "temperature_avg"        : 22,
    "temperature_min"        : 14,
    "temperature_max"        : 32,
    "humidity_percent"       : 65,
    "solar_radiation"        : 18,
    "fertilizer_kg_per_ha"   : 120,
    "pesticide_applications" : 2
  }'
```

---

### 👁️ &nbsp; Disease Scan &nbsp; ![](https://img.shields.io/badge/🔐_AUTH-required-FF6F00?style=flat-square)

```powershell
curl -X POST http://localhost:5000/api/scan/disease `
  -H "Authorization: Bearer TOKEN" `
  -F "image=@path\to\crop_photo.jpg"
```

---

<div align="center">

## `◈ Endpoint Map`

</div>

```
┌──────────┬──────────────────────────────┬──────────────────────────────────────┬────────┐
│  Method  │  Route                       │  Description                         │  Auth  │
├──────────┼──────────────────────────────┼──────────────────────────────────────┼────────┤
│  POST    │  /api/auth/login             │  Authenticate → receive Bearer token │   ✗    │
│  GET     │  /api/listings               │  All crop marketplace listings        │   ✗    │
│  GET     │  /api/listings?crop_type=    │  Filter listings by crop type         │   ✗    │
│  GET     │  /api/listings?search=       │  Full-text keyword search             │   ✗    │
│  POST    │  /api/predict/yield          │  ML yield forecast (13 features)      │  🔐    │
│  POST    │  /api/scan/disease           │  CV pathogen classification           │  🔐    │
└──────────┴──────────────────────────────┴──────────────────────────────────────┴────────┘
```

---

<div align="center">

## `◈ ML Input Features`

</div>

```python
# ════════════════════════════════════════════════════
#   🧠  PlantGuard Yield Predictor — 13 Features
# ════════════════════════════════════════════════════

payload = {

    # ── Crop Identity ─────────────────────────────
    "crop_type"              : "wheat",       # str  — rice / wheat / maize / etc.
    "area_hectares"          : 10,            # float — cultivated area

    # ── Field Conditions ──────────────────────────
    "planting_date"          : "2025-01-01",  # ISO 8601 date string
    "soil_type"              : "loam",        # clay / sandy / loam / silt
    "irrigation_type"        : "drip",        # drip / sprinkler / flood / none

    # ── Weather & Climate ─────────────────────────
    "rainfall_mm"            : 550,           # float — seasonal rainfall
    "temperature_avg"        : 22,            # float — °C average
    "temperature_min"        : 14,            # float — °C minimum
    "temperature_max"        : 32,            # float — °C maximum
    "humidity_percent"       : 65,            # float — 0 to 100
    "solar_radiation"        : 18,            # float — MJ/m²/day

    # ── Agronomic Inputs ──────────────────────────
    "fertilizer_kg_per_ha"   : 120,           # float — kg per hectare
    "pesticide_applications" : 2              # int   — number of applications
}
```

---

<div align="center">

## `◈ Demo Accounts`

<img src="https://readme-typing-svg.demolab.com?font=Space+Mono&size=13&pause=2000&color=C792EA&center=true&width=500&lines=All+accounts+share+password%3A+demo123;Roles+control+API+access+permissions." alt="Typing SVG" />

</div>

<table align="center">
<tr>
<th>Username</th>
<th>Password</th>
<th>Role</th>
<th>Permissions</th>
</tr>
<tr>
<td><code>ramesh_farmer</code></td>
<td><code>demo123</code></td>
<td>🌱 Farmer</td>
<td>Post listings · Yield predict · Disease scan</td>
</tr>
<tr>
<td><code>sarah_buyer</code></td>
<td><code>demo123</code></td>
<td>🛒 Buyer</td>
<td>Browse & search marketplace</td>
</tr>
<tr>
<td><code>carlos_grower</code></td>
<td><code>demo123</code></td>
<td>🌱 Farmer</td>
<td>Post listings · Yield predict · Disease scan</td>
</tr>
<tr>
<td><code>amina_trade</code></td>
<td><code>demo123</code></td>
<td>🛒 Buyer</td>
<td>Browse & search marketplace</td>
</tr>
</table>

---

<div align="center">

## `◈ Tech Stack`

</div>

| Layer | Technology | Purpose |
|-------|-----------|---------|
| ![](https://img.shields.io/badge/Backend-000?style=flat-square) | `Flask 2.x` · `Python 3` · `Flask-CORS` | REST API server & routing |
| ![](https://img.shields.io/badge/Database-003B57?style=flat-square) | `SQLite` · `Pandas DataFrames` | Persistence & data wrangling |
| ![](https://img.shields.io/badge/ML-FF6F00?style=flat-square) | `TensorFlow` · `scikit-learn` · `NumPy` · `Pandas` | Yield prediction pipeline |
| ![](https://img.shields.io/badge/Vision-5C3EE8?style=flat-square) | `OpenCV (cv2)` | Plant disease classification |
| ![](https://img.shields.io/badge/Frontend-61DAFB?style=flat-square) | `React 18` · `Vite` · `JSX` | SPA dashboard |
| ![](https://img.shields.io/badge/Tooling-grey?style=flat-square) | `pip` · `npm` | Package management |

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00ff88,50:00a846,100:001a08&height=120&section=footer&text=🌾%20PlantGuard&fontSize=24&fontColor=ffffff&fontAlignY=65&animation=fadeIn" width="100%"/>

<sub>Built with ⚗️ Flask · 🧠 TensorFlow · 👁️ OpenCV · ⚛️ React · 🗄️ SQLite</sub>

</div>
