import { useState, useEffect, useRef } from "react";

// ─── Mock API (simulates Flask backend responses) ─────────────────────────────
const MOCK_LISTINGS = [
  { id: "lst-001", title: "Premium Basmati Rice — Punjab Harvest", crop_type: "rice", quantity_tons: 45, price_per_ton: 380, currency: "USD", quality_grade: "Grade A", location: "Punjab, India", farmer_name: "ramesh_farmer", verified: 1, certifications: ["organic"], harvest_date: "2025-02-15", description: "Freshly harvested long-grain basmati, pesticide-free.", views_count: 142 },
  { id: "lst-002", title: "Yellow Corn — Jalisco Fields", crop_type: "corn", quantity_tons: 120, price_per_ton: 195, currency: "USD", quality_grade: "Grade B", location: "Jalisco, Mexico", farmer_name: "carlos_grower", verified: 0, certifications: [], harvest_date: "2025-01-20", description: "Non-GMO yellow corn, suitable for feed and processing.", views_count: 87 },
  { id: "lst-003", title: "Whole Wheat — Winter Harvest", crop_type: "wheat", quantity_tons: 200, price_per_ton: 260, currency: "USD", quality_grade: "Grade A", location: "Punjab, India", farmer_name: "ramesh_farmer", verified: 1, certifications: ["fair-trade"], harvest_date: "2025-03-01", description: "Hard red winter wheat, protein content 12%+.", views_count: 203 },
  { id: "lst-004", title: "Cherry Tomatoes — Greenhouse Grown", crop_type: "tomato", quantity_tons: 8.5, price_per_ton: 1200, currency: "USD", quality_grade: "Premium", location: "Jalisco, Mexico", farmer_name: "carlos_grower", verified: 0, certifications: ["organic", "fair-trade"], harvest_date: "2025-01-10", description: "Vine-ripened cherry tomatoes, year-round supply.", views_count: 56 },
  { id: "lst-005", title: "Soybeans — Non-GMO Certified", crop_type: "soybean", quantity_tons: 75, price_per_ton: 420, currency: "USD", quality_grade: "Grade A", location: "Mato Grosso, Brazil", farmer_name: "paulo_soja", verified: 1, certifications: ["organic"], harvest_date: "2025-02-28", description: "Identity-preserved non-GMO soybeans for food-grade use.", views_count: 318 },
];

const CROP_ICONS = { rice: "🌾", corn: "🌽", wheat: "🌻", tomato: "🍅", soybean: "🫘", cotton: "🌿", potato: "🥔", onion: "🧅", sugarcane: "🎋", other: "🌱" };
const CROP_COLORS = { rice: "#4ade80", corn: "#fbbf24", wheat: "#f59e0b", tomato: "#f87171", soybean: "#a3e635", cotton: "#e2e8f0", potato: "#d97706", onion: "#c084fc" };

function mockPredictYield(form) {
  const bases = { wheat: 3.2, rice: 4.5, corn: 5.8, soybean: 2.7, tomato: 35, potato: 22, other: 3 };
  const base = (bases[form.crop_type] || 3) * form.area_hectares;
  const rain = Math.min(1.3, Math.max(0.5, form.rainfall_mm / 600));
  const temp = Math.max(0.7, 1 - Math.abs(form.temperature_avg - 22) * 0.02);
  const irrig = { drip: 1.25, sprinkler: 1.15, flood: 1.0, none: 0.8 }[form.irrigation_type] || 1;
  const yield_val = base * rain * temp * irrig;
  return {
    predicted_yield_tons: +yield_val.toFixed(2),
    confidence_score: 0.84,
    lower_bound: +(yield_val * 0.82).toFixed(2),
    upper_bound: +(yield_val * 1.18).toFixed(2),
    feature_importance: { rainfall: 0.28, temperature: 0.22, irrigation: 0.19, fertilizer: 0.15, soil_quality: 0.11, historical: 0.05 },
    recommendations: [
      form.rainfall_mm < 400 ? "⚠️ Low rainfall — consider supplemental irrigation." : "✅ Rainfall levels are adequate for this crop.",
      form.fertilizer_kg_per_ha < 80 ? "🌱 Fertilizer below optimal — increase nitrogen by 20%." : "✅ Fertilizer application is on target.",
      "📊 Expected harvest window: 85–95 days based on current GDD trajectory.",
    ],
    model_version: "v2.1-heuristic"
  };
}

function mockScanDisease() {
  const scenarios = [
    { diseases: [{ name: "Leaf Blight", confidence: 0.87, severity: "moderate", affected_area_percent: 18.4, color: "#E67E22", treatment: "Apply copper-based fungicide. Remove infected leaves." }], overall_severity: "moderate", total_affected_percent: 18.4 },
    { diseases: [], overall_severity: "none", total_affected_percent: 0 },
    { diseases: [{ name: "Powdery Mildew", confidence: 0.92, severity: "mild", affected_area_percent: 7.2, color: "#ECF0F1", treatment: "Apply sulfur-based fungicide or neem oil." }, { name: "Rust", confidence: 0.71, severity: "mild", affected_area_percent: 3.8, color: "#E74C3C", treatment: "Apply triazole fungicide." }], overall_severity: "mild", total_affected_percent: 11.0 },
  ];
  return scenarios[Math.floor(Math.random() * scenarios.length)];
}

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [tab, setTab] = useState("market");
  const [listings, setListings] = useState(MOCK_LISTINGS);
  const [search, setSearch] = useState("");
  const [filterCrop, setFilterCrop] = useState("all");
  const [selectedListing, setSelectedListing] = useState(null);
  const [predResult, setPredResult] = useState(null);
  const [scanResult, setScanResult] = useState(null);
  const [predLoading, setPredLoading] = useState(false);
  const [scanLoading, setScanLoading] = useState(false);
  const [scanImage, setScanImage] = useState(null);
  const [predForm, setPredForm] = useState({ crop_type: "wheat", area_hectares: 5, planting_date: "2025-01-01", soil_type: "loam", irrigation_type: "drip", rainfall_mm: 550, temperature_avg: 22, temperature_min: 14, temperature_max: 32, humidity_percent: 65, solar_radiation: 18, fertilizer_kg_per_ha: 120, pesticide_applications: 2 });
  const fileRef = useRef();

  const filtered = listings.filter(l =>
    (filterCrop === "all" || l.crop_type === filterCrop) &&
    (l.title.toLowerCase().includes(search.toLowerCase()) || l.location.toLowerCase().includes(search.toLowerCase()))
  );

  const runPrediction = async () => {
    setPredLoading(true);
    await new Promise(r => setTimeout(r, 1400));
    setPredResult(mockPredictYield(predForm));
    setPredLoading(false);
  };

  const runScan = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setScanImage(url);
    setScanLoading(true);
    await new Promise(r => setTimeout(r, 2000));
    setScanResult(mockScanDisease());
    setScanLoading(false);
  };

  return (
    <div style={{ fontFamily: "'Instrument Serif', Georgia, serif", background: "#0a0f0a", minHeight: "100vh", color: "#e8f0e8" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Mono:wght@300;400;500&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: #0a0f0a; } ::-webkit-scrollbar-thumb { background: #2d4a2d; border-radius: 2px; }
        .pill { display: inline-flex; align-items: center; gap: 4px; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-family: 'DM Mono', monospace; font-weight: 500; letter-spacing: 0.04em; }
        .card { background: #111811; border: 1px solid #1e2e1e; border-radius: 12px; transition: border-color 0.2s, transform 0.2s; }
        .card:hover { border-color: #3a5a3a; transform: translateY(-1px); }
        .btn { border: none; cursor: pointer; font-family: 'DM Mono', monospace; font-size: 13px; font-weight: 500; letter-spacing: 0.06em; border-radius: 8px; transition: all 0.15s; }
        .btn-primary { background: #4ade80; color: #052005; padding: 10px 24px; }
        .btn-primary:hover { background: #86efac; }
        .btn-ghost { background: transparent; color: #a0c4a0; padding: 10px 20px; border: 1px solid #2d4a2d; }
        .btn-ghost:hover { background: #1e2e1e; color: #e8f0e8; }
        .input { background: #0d150d; border: 1px solid #2d4a2d; border-radius: 8px; color: #e8f0e8; padding: 10px 14px; font-family: 'DM Mono', monospace; font-size: 13px; width: 100%; outline: none; transition: border-color 0.15s; }
        .input:focus { border-color: #4ade80; }
        .label { font-family: 'DM Mono', monospace; font-size: 11px; color: #6b8f6b; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; display: block; }
        .tab { padding: 10px 20px; cursor: pointer; font-family: 'DM Mono', monospace; font-size: 12px; letter-spacing: 0.06em; border-radius: 8px; transition: all 0.15s; border: none; background: transparent; }
        .tab.active { background: #1e2e1e; color: #4ade80; }
        .tab:not(.active) { color: #6b8f6b; }
        .tab:not(.active):hover { color: #a0c4a0; background: #0d150d; }
        .bar-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #4ade80, #86efac); transition: width 0.8s ease; }
        select.input { appearance: none; }
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
        .fade-in { animation: fadeIn 0.4s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .scan-border { border: 2px dashed #2d4a2d; border-radius: 12px; transition: border-color 0.2s, background 0.2s; }
        .scan-border:hover { border-color: #4ade80; background: #0d150d; }
        .severity-none { background: #1a2e1a; color: #4ade80; }
        .severity-mild { background: #2a2a0a; color: #fbbf24; }
        .severity-moderate { background: #2a1a0a; color: #f97316; }
        .severity-severe { background: #2a0a0a; color: #f87171; }
      `}</style>

      {/* Header */}
      <div style={{ borderBottom: "1px solid #1e2e1e", padding: "0 32px", display: "flex", alignItems: "center", justifyContent: "space-between", height: 64 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg, #4ade80 0%, #166534 100%)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>🌾</div>
          <div>
            <div style={{ fontSize: 18, fontStyle: "italic", lineHeight: 1.1 }}>AgroIntel</div>
            <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#6b8f6b", letterSpacing: "0.1em" }}>SMART AGRICULTURE PLATFORM</div>
          </div>
        </div>
        <div style={{ display: "flex", gap: 4 }}>
          {[["market", "🌐 Marketplace"], ["predict", "🔬 ML Pipeline"], ["vision", "👁️ Disease Scan"]].map(([key, label]) => (
            <button key={key} className={`tab ${tab === key ? "active" : ""}`} onClick={() => setTab(key)}>{label}</button>
          ))}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span className="pill" style={{ background: "#0d2d0d", color: "#4ade80" }}>● LIVE</span>
          <div style={{ width: 32, height: 32, borderRadius: "50%", background: "#1e2e1e", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14 }}>👤</div>
        </div>
      </div>

      <div style={{ padding: "32px", maxWidth: 1280, margin: "0 auto" }}>

        {/* ── MARKETPLACE TAB ── */}
        {tab === "market" && (
          <div className="fade-in">
            <div style={{ marginBottom: 24 }}>
              <div style={{ fontSize: 32, fontStyle: "italic", marginBottom: 4 }}>Crop Marketplace</div>
              <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#6b8f6b" }}>Connect directly with verified farmers worldwide</div>
            </div>

            {/* Filters */}
            <div style={{ display: "flex", gap: 12, marginBottom: 24, flexWrap: "wrap" }}>
              <input className="input" placeholder="Search crops, locations..." value={search} onChange={e => setSearch(e.target.value)} style={{ maxWidth: 300 }} />
              <select className="input" value={filterCrop} onChange={e => setFilterCrop(e.target.value)} style={{ maxWidth: 180 }}>
                <option value="all">All Crops</option>
                {["wheat", "rice", "corn", "soybean", "tomato", "potato"].map(c => <option key={c} value={c}>{CROP_ICONS[c]} {c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
              </select>
              <div style={{ marginLeft: "auto", fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#6b8f6b", alignSelf: "center" }}>
                {filtered.length} listings
              </div>
            </div>

            {/* Stats row */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, marginBottom: 28 }}>
              {[
                { label: "Active Listings", value: "1,284", icon: "📋", delta: "+12 today" },
                { label: "Farmers Online", value: "342", icon: "👨‍🌾", delta: "across 28 countries" },
                { label: "Avg. Price/Ton", value: "$318", icon: "💰", delta: "wheat baseline" },
                { label: "Tons Available", value: "48,200t", icon: "⚖️", delta: "this month" },
              ].map(s => (
                <div key={s.label} className="card" style={{ padding: "16px 20px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                      <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#6b8f6b", letterSpacing: "0.08em", marginBottom: 4 }}>{s.label.toUpperCase()}</div>
                      <div style={{ fontSize: 26, fontStyle: "italic" }}>{s.value}</div>
                      <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4ade80", marginTop: 2 }}>{s.delta}</div>
                    </div>
                    <span style={{ fontSize: 24 }}>{s.icon}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Listings grid */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 16 }}>
              {filtered.map(l => (
                <div key={l.id} className="card" style={{ padding: 20, cursor: "pointer" }} onClick={() => setSelectedListing(l)}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                    <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                      <div style={{ width: 40, height: 40, borderRadius: 10, background: `${CROP_COLORS[l.crop_type]}22`, border: `1px solid ${CROP_COLORS[l.crop_type]}44`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20 }}>{CROP_ICONS[l.crop_type]}</div>
                      <div>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#6b8f6b", letterSpacing: "0.06em" }}>{l.crop_type.toUpperCase()}</div>
                        <div style={{ fontSize: 15, fontStyle: "italic", lineHeight: 1.2 }}>{l.title}</div>
                      </div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 20, color: "#4ade80" }}>${l.price_per_ton}</div>
                      <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#6b8f6b" }}>per ton</div>
                    </div>
                  </div>

                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#a0c4a0", marginBottom: 12, lineHeight: 1.5 }}>{l.description}</div>

                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 12 }}>
                    <span className="pill" style={{ background: "#0d2d0d", color: "#4ade80" }}>⚖️ {l.quantity_tons}t available</span>
                    <span className="pill" style={{ background: "#1a1a0d", color: "#fbbf24" }}>📍 {l.location}</span>
                    {l.verified ? <span className="pill" style={{ background: "#0d1a2d", color: "#60a5fa" }}>✓ Verified</span> : null}
                    {l.certifications.map(c => <span key={c} className="pill" style={{ background: "#1a0d2d", color: "#c084fc" }}>{c}</span>)}
                  </div>

                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#6b8f6b" }}>👤 {l.farmer_name} · {l.views_count} views</div>
                    <button className="btn btn-primary" style={{ padding: "6px 16px", fontSize: 11 }}>Contact Farmer →</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── ML PIPELINE TAB ── */}
        {tab === "predict" && (
          <div className="fade-in">
            <div style={{ marginBottom: 24 }}>
              <div style={{ fontSize: 32, fontStyle: "italic", marginBottom: 4 }}>Yield Prediction</div>
              <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#6b8f6b" }}>TensorFlow deep regression · Pandas feature engineering · Uncertainty quantification</div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, alignItems: "start" }}>
              {/* Form */}
              <div className="card" style={{ padding: 24 }}>
                <div style={{ fontSize: 18, fontStyle: "italic", marginBottom: 20 }}>Crop Parameters</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                  {[
                    { key: "crop_type", label: "Crop Type", type: "select", opts: ["wheat","rice","corn","soybean","tomato","potato","other"] },
                    { key: "area_hectares", label: "Area (hectares)", type: "number", min: 0.1, step: 0.5 },
                    { key: "planting_date", label: "Planting Date", type: "date" },
                    { key: "soil_type", label: "Soil Type", type: "select", opts: ["loam","clay","sandy","silt","clay_loam"] },
                    { key: "irrigation_type", label: "Irrigation", type: "select", opts: ["none","drip","sprinkler","flood"] },
                    { key: "rainfall_mm", label: "Seasonal Rainfall (mm)", type: "number", min: 0, step: 10 },
                    { key: "temperature_avg", label: "Avg Temp (°C)", type: "number", min: -10, max: 50, step: 0.5 },
                    { key: "humidity_percent", label: "Humidity (%)", type: "number", min: 0, max: 100, step: 1 },
                    { key: "fertilizer_kg_per_ha", label: "Fertilizer (kg/ha)", type: "number", min: 0, step: 10 },
                    { key: "pesticide_applications", label: "Pesticide Applications", type: "number", min: 0, step: 1 },
                  ].map(f => (
                    <div key={f.key}>
                      <label className="label">{f.label}</label>
                      {f.type === "select"
                        ? <select className="input" value={predForm[f.key]} onChange={e => setPredForm(p => ({ ...p, [f.key]: e.target.value }))}>
                            {f.opts.map(o => <option key={o} value={o}>{o}</option>)}
                          </select>
                        : <input className="input" type={f.type} min={f.min} max={f.max} step={f.step} value={predForm[f.key]} onChange={e => setPredForm(p => ({ ...p, [f.key]: f.type === "number" ? parseFloat(e.target.value) : e.target.value }))} />
                      }
                    </div>
                  ))}
                </div>
                <button className="btn btn-primary" style={{ marginTop: 20, width: "100%", padding: "12px" }} onClick={runPrediction} disabled={predLoading}>
                  {predLoading ? <span className="pulse">⚙️ Running TF Model...</span> : "🔬 Run Yield Prediction"}
                </button>
              </div>

              {/* Results */}
              <div>
                {!predResult && !predLoading && (
                  <div className="card" style={{ padding: 40, textAlign: "center" }}>
                    <div style={{ fontSize: 48, marginBottom: 12 }}>🌱</div>
                    <div style={{ fontSize: 18, fontStyle: "italic", color: "#6b8f6b" }}>Configure parameters and run prediction</div>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#3a5a3a", marginTop: 8 }}>TensorFlow · Pandas · Residual Neural Network</div>
                  </div>
                )}
                {predLoading && (
                  <div className="card" style={{ padding: 40, textAlign: "center" }}>
                    <div style={{ fontSize: 40, marginBottom: 12 }} className="pulse">⚙️</div>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#4ade80" }}>Running ML pipeline...</div>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#6b8f6b", marginTop: 6 }}>Feature engineering → TF inference → Uncertainty bounds</div>
                  </div>
                )}
                {predResult && !predLoading && (
                  <div className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                    {/* Main result */}
                    <div className="card" style={{ padding: 24 }}>
                      <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#6b8f6b", letterSpacing: "0.08em", marginBottom: 8 }}>PREDICTED YIELD</div>
                      <div style={{ fontSize: 56, fontStyle: "italic", color: "#4ade80", lineHeight: 1 }}>{predResult.predicted_yield_tons}<span style={{ fontSize: 20, color: "#6b8f6b" }}> tons</span></div>
                      <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#a0c4a0", marginTop: 4 }}>
                        95% CI: [{predResult.lower_bound}t — {predResult.upper_bound}t]
                      </div>
                      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
                        <span className="pill" style={{ background: "#0d2d0d", color: "#4ade80" }}>Confidence: {(predResult.confidence_score * 100).toFixed(0)}%</span>
                        <span className="pill" style={{ background: "#1a1a0a", color: "#fbbf24" }}>Model: {predResult.model_version}</span>
                      </div>
                    </div>

                    {/* Feature importance */}
                    <div className="card" style={{ padding: 24 }}>
                      <div style={{ fontSize: 16, fontStyle: "italic", marginBottom: 16 }}>Feature Importance</div>
                      {Object.entries(predResult.feature_importance).sort((a,b) => b[1]-a[1]).map(([feat, val]) => (
                        <div key={feat} style={{ marginBottom: 10 }}>
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                            <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#a0c4a0" }}>{feat.replace(/_/g, " ")}</span>
                            <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#4ade80" }}>{(val * 100).toFixed(0)}%</span>
                          </div>
                          <div style={{ height: 6, background: "#1e2e1e", borderRadius: 4, overflow: "hidden" }}>
                            <div className="bar-fill" style={{ width: `${val * 100 / 0.28 * 100}%`, maxWidth: "100%" }} />
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Recommendations */}
                    <div className="card" style={{ padding: 24 }}>
                      <div style={{ fontSize: 16, fontStyle: "italic", marginBottom: 12 }}>AI Recommendations</div>
                      {predResult.recommendations.map((r, i) => (
                        <div key={i} style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#a0c4a0", padding: "8px 0", borderBottom: i < predResult.recommendations.length - 1 ? "1px solid #1e2e1e" : "none" }}>{r}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ── COMPUTER VISION TAB ── */}
        {tab === "vision" && (
          <div className="fade-in">
            <div style={{ marginBottom: 24 }}>
              <div style={{ fontSize: 32, fontStyle: "italic", marginBottom: 4 }}>Crop Disease Detection</div>
              <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#6b8f6b" }}>OpenCV real-time analysis · HSV segmentation · Contour detection · Bounding box annotation</div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, alignItems: "start" }}>
              {/* Upload */}
              <div>
                <div className="card scan-border" style={{ padding: 32, textAlign: "center", cursor: "pointer", marginBottom: 16 }} onClick={() => fileRef.current.click()}>
                  {scanImage
                    ? <img src={scanImage} alt="scan" style={{ maxHeight: 280, maxWidth: "100%", borderRadius: 8, objectFit: "contain" }} />
                    : <>
                        <div style={{ fontSize: 52, marginBottom: 12 }}>📸</div>
                        <div style={{ fontSize: 18, fontStyle: "italic", marginBottom: 6 }}>Upload crop photo</div>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#6b8f6b" }}>JPG, PNG · Click or drag to upload</div>
                      </>
                  }
                  <input ref={fileRef} type="file" accept="image/*" style={{ display: "none" }} onChange={runScan} />
                </div>

                {/* Pipeline stages */}
                <div className="card" style={{ padding: 20 }}>
                  <div style={{ fontSize: 15, fontStyle: "italic", marginBottom: 14 }}>OpenCV Pipeline</div>
                  {[
                    { stage: "Pre-processing", detail: "CLAHE enhancement + denoising", icon: "🔧" },
                    { stage: "Leaf Segmentation", detail: "GrabCut + HSV green-range masking", icon: "🍃" },
                    { stage: "Disease Detection", detail: "Colour thresholds + morphological ops", icon: "🔬" },
                    { stage: "Contour Analysis", detail: "findContours → bounding boxes", icon: "📐" },
                    { stage: "Annotation", detail: "Overlay + severity banner rendering", icon: "🎨" },
                  ].map((s, i) => (
                    <div key={s.stage} style={{ display: "flex", gap: 12, alignItems: "flex-start", padding: "8px 0", borderBottom: i < 4 ? "1px solid #1e2e1e" : "none" }}>
                      <span style={{ fontSize: 16 }}>{s.icon}</span>
                      <div>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#e8f0e8" }}>{s.stage}</div>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#6b8f6b" }}>{s.detail}</div>
                      </div>
                      <div style={{ marginLeft: "auto" }}>
                        <span className="pill" style={{ background: "#0d2d0d", color: "#4ade80" }}>
                          {scanLoading && i === 2 ? <span className="pulse">⚙️</span> : "✓"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Results */}
              <div>
                {!scanResult && !scanLoading && (
                  <div className="card" style={{ padding: 40, textAlign: "center" }}>
                    <div style={{ fontSize: 48, marginBottom: 12 }}>🔎</div>
                    <div style={{ fontSize: 18, fontStyle: "italic", color: "#6b8f6b" }}>Upload a crop image to scan</div>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#3a5a3a", marginTop: 8 }}>Detects: Leaf Blight · Rust · Mildew · Mosaic Virus · Root Rot</div>
                  </div>
                )}
                {scanLoading && (
                  <div className="card" style={{ padding: 40, textAlign: "center" }}>
                    <div style={{ fontSize: 40, marginBottom: 12 }} className="pulse">👁️</div>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#4ade80" }}>Analysing image...</div>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#6b8f6b", marginTop: 6 }}>OpenCV pipeline running · ~2s</div>
                  </div>
                )}
                {scanResult && !scanLoading && (
                  <div className="fade-in" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                    {/* Severity summary */}
                    <div className={`card severity-${scanResult.overall_severity}`} style={{ padding: 24 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                        <div>
                          <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, letterSpacing: "0.08em", opacity: 0.7 }}>OVERALL SEVERITY</div>
                          <div style={{ fontSize: 36, fontStyle: "italic", lineHeight: 1.1, textTransform: "capitalize" }}>
                            {scanResult.overall_severity === "none" ? "✅ Healthy" : scanResult.overall_severity}
                          </div>
                        </div>
                        <div style={{ textAlign: "right" }}>
                          <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 28 }}>{scanResult.total_affected_percent}%</div>
                          <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, opacity: 0.7 }}>leaf area affected</div>
                        </div>
                      </div>
                      <div style={{ height: 8, background: "rgba(0,0,0,0.3)", borderRadius: 4, overflow: "hidden" }}>
                        <div style={{ height: "100%", width: `${Math.min(100, scanResult.total_affected_percent * 2)}%`, borderRadius: 4, background: "currentColor", transition: "width 1s ease" }} />
                      </div>
                    </div>

                    {/* Detected diseases */}
                    {scanResult.diseases.length > 0 && (
                      <div className="card" style={{ padding: 24 }}>
                        <div style={{ fontSize: 16, fontStyle: "italic", marginBottom: 14 }}>Detected Diseases</div>
                        {scanResult.diseases.map((d, i) => (
                          <div key={i} style={{ padding: "12px 0", borderBottom: i < scanResult.diseases.length - 1 ? "1px solid #1e2e1e" : "none" }}>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                              <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                                <div style={{ width: 12, height: 12, borderRadius: "50%", background: d.color }} />
                                <span style={{ fontSize: 15, fontStyle: "italic" }}>{d.name}</span>
                              </div>
                              <div style={{ display: "flex", gap: 6 }}>
                                <span className="pill" style={{ background: "#0d2d0d", color: "#4ade80" }}>{(d.confidence * 100).toFixed(0)}% conf</span>
                                <span className="pill" style={{ background: "#1a1a0a", color: "#fbbf24" }}>{d.affected_area_percent}% area</span>
                              </div>
                            </div>
                            <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#a0c4a0", lineHeight: 1.5 }}>💊 {d.treatment}</div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Recs */}
                    <div className="card" style={{ padding: 24 }}>
                      <div style={{ fontSize: 16, fontStyle: "italic", marginBottom: 12 }}>Treatment Plan</div>
                      {[
                        scanResult.overall_severity === "none" ? "✅ No disease detected — continue weekly monitoring." : `⚠️ ${scanResult.diseases.length} disease(s) identified requiring treatment.`,
                        "📸 Re-scan in 7 days to monitor treatment effectiveness.",
                        scanResult.overall_severity === "severe" ? "🚨 Quarantine field — prevent spread to adjacent plots." : "🌿 Maintain field hygiene and proper spacing.",
                      ].map((r, i) => (
                        <div key={i} style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#a0c4a0", padding: "8px 0", borderBottom: i < 2 ? "1px solid #1e2e1e" : "none" }}>{r}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Listing detail modal */}
      {selectedListing && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100, padding: 24 }} onClick={() => setSelectedListing(null)}>
          <div className="card fade-in" style={{ maxWidth: 520, width: "100%", padding: 28 }} onClick={e => e.stopPropagation()}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                <div style={{ width: 48, height: 48, borderRadius: 12, background: `${CROP_COLORS[selectedListing.crop_type]}22`, border: `1px solid ${CROP_COLORS[selectedListing.crop_type]}44`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24 }}>{CROP_ICONS[selectedListing.crop_type]}</div>
                <div>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#6b8f6b" }}>{selectedListing.crop_type.toUpperCase()} · {selectedListing.quality_grade}</div>
                  <div style={{ fontSize: 20, fontStyle: "italic" }}>{selectedListing.title}</div>
                </div>
              </div>
              <button className="btn btn-ghost" style={{ padding: "4px 10px" }} onClick={() => setSelectedListing(null)}>✕</button>
            </div>
            <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#a0c4a0", marginBottom: 16, lineHeight: 1.6 }}>{selectedListing.description}</div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
              {[["Price", `$${selectedListing.price_per_ton}/ton`], ["Quantity", `${selectedListing.quantity_tons} tons`], ["Location", selectedListing.location], ["Harvest", selectedListing.harvest_date]].map(([k, v]) => (
                <div key={k} style={{ background: "#0d150d", borderRadius: 8, padding: "10px 14px" }}>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#6b8f6b", marginBottom: 3 }}>{k.toUpperCase()}</div>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 14, color: "#e8f0e8" }}>{v}</div>
                </div>
              ))}
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn btn-primary" style={{ flex: 1, padding: "12px" }}>📩 Contact Farmer</button>
              <button className="btn btn-ghost" style={{ flex: 1, padding: "12px" }}>💼 Place Order</button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div style={{ borderTop: "1px solid #1e2e1e", padding: "16px 32px", display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 40 }}>
        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a" }}>AGROINTEL PLATFORM · FLASK API + TENSORFLOW + OPENCV</div>
        <div style={{ display: "flex", gap: 12 }}>
          {["ML Pipeline", "OpenCV Vision", "REST API", "Marketplace"].map(t => (
            <span key={t} className="pill" style={{ background: "#0d150d", color: "#3a5a3a", border: "1px solid #1e2e1e" }}>{t}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
