import { useState, useRef, useEffect, useCallback } from "react";

// ── Real API Layer ────────────────────────────────────────────────────────────
const API_BASE = "http://localhost:5000";

async function apiCall(path, options = {}) {
  const token = localStorage.getItem("pg_token");
  const isFormData = options.body instanceof FormData;
  const res = await fetch(API_BASE + path, {
    ...options,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: "Bearer " + token } : {}),
      ...(options.headers || {}),
    },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed (" + res.status + ")");
  return data;
}

// ── Constants ─────────────────────────────────────────────────────────────────
const CROP_ICON  = { rice:"🌾", corn:"🌽", wheat:"🌻", tomato:"🍅", soybean:"🫘", cotton:"🌿", potato:"🥔", onion:"🧅", sugarcane:"🎋", other:"🌱" };
const CROP_COLOR = { rice:"#4ade80", corn:"#fbbf24", wheat:"#f59e0b", tomato:"#f87171", soybean:"#a3e635", potato:"#d97706", onion:"#c084fc", other:"#94a3b8" };
const SEV_COLOR  = { none:"#4ade80", mild:"#fbbf24", moderate:"#f97316", severe:"#f87171" };

// ── Styles ────────────────────────────────────────────────────────────────────
const css = `
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@300;400;500&display=swap');
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#080d08}
  ::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:#080d08}::-webkit-scrollbar-thumb{background:#253525;border-radius:2px}
  .card{background:#0e160e;border:1px solid #1c2e1c;border-radius:14px;transition:border-color .2s,transform .15s}
  .card:hover{border-color:#3a563a}
  .btn{border:none;cursor:pointer;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:500;letter-spacing:.06em;border-radius:8px;transition:all .15s}
  .btn-green{background:#4ade80;color:#042004;padding:10px 22px}
  .btn-green:hover{background:#86efac}
  .btn-green:disabled{background:#1c3a1c;color:#3a563a;cursor:not-allowed}
  .btn-ghost{background:transparent;color:#8aad8a;padding:10px 18px;border:1px solid #253525}
  .btn-ghost:hover{background:#0e160e;color:#e8f0e8}
  .inp{background:#0a110a;border:1px solid #253525;border-radius:8px;color:#e8f0e8;padding:9px 13px;font-family:'JetBrains Mono',monospace;font-size:12px;width:100%;outline:none;transition:border-color .15s}
  .inp:focus{border-color:#4ade80}
  select.inp{appearance:none}
  .lbl{font-family:'JetBrains Mono',monospace;font-size:10px;color:#5a7a5a;letter-spacing:.08em;text-transform:uppercase;margin-bottom:5px;display:block}
  .tag{display:inline-flex;align-items:center;gap:3px;padding:2px 9px;border-radius:20px;font-size:10px;font-family:'JetBrains Mono',monospace;font-weight:500;letter-spacing:.04em}
  .fade{animation:fadeIn .35s ease}
  @keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
  .pulse{animation:pulse 1.8s ease-in-out infinite}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
  .err{background:#2a0a0a;border:1px solid #5a1a1a;border-radius:8px;padding:10px 14px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#f87171;margin-bottom:14px}
`;

// ── Tiny components ───────────────────────────────────────────────────────────
const Tag = ({ style, children }) => <span className="tag" style={style}>{children}</span>;

function StatCard({ label, value, sub, icon }) {
  return (
    <div className="card" style={{ padding:"16px 18px" }}>
      <div style={{ display:"flex", justifyContent:"space-between" }}>
        <div>
          <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:10, color:"#5a7a5a", letterSpacing:".08em", marginBottom:4 }}>{label.toUpperCase()}</div>
          <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:26, fontWeight:600, lineHeight:1 }}>{value}</div>
          <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:10, color:"#4ade80", marginTop:3 }}>{sub}</div>
        </div>
        <span style={{ fontSize:22 }}>{icon}</span>
      </div>
    </div>
  );
}

// ── Login ─────────────────────────────────────────────────────────────────────
function Login({ onLogin }) {
  const [form, setForm]       = useState({ username:"ramesh_farmer", password:"demo123" });
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  async function submit() {
    setLoading(true); setError("");
    try {
      const d = await apiCall("/api/auth/login", { method:"POST", body:JSON.stringify(form) });
      localStorage.setItem("pg_token", d.token);
      localStorage.setItem("pg_user",  JSON.stringify(d.user));
      onLogin(d.user);
    } catch(e) { setError(e.message); }
    finally    { setLoading(false); }
  }

  return (
    <div style={{ minHeight:"100vh", background:"#080d08", display:"flex", alignItems:"center", justifyContent:"center", padding:24 }}>
      <div className="card fade" style={{ width:"100%", maxWidth:400, padding:32 }}>
        <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:28 }}>
          <div style={{ width:40, height:40, borderRadius:10, background:"linear-gradient(135deg,#4ade80,#166534)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:20 }}>🌾</div>
          <div>
            <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:22, fontStyle:"italic", fontWeight:600 }}>PlantGuard</div>
            <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:9, color:"#5a7a5a", letterSpacing:".1em" }}>SMART AGRICULTURE PLATFORM</div>
          </div>
        </div>

        {error && <div className="err">⚠️ {error}</div>}

        <div style={{ marginBottom:14 }}>
          <label className="lbl">Username</label>
          <input className="inp" value={form.username} onChange={e=>setForm(p=>({...p,username:e.target.value}))} onKeyDown={e=>e.key==="Enter"&&submit()} />
        </div>
        <div style={{ marginBottom:20 }}>
          <label className="lbl">Password</label>
          <input className="inp" type="password" value={form.password} onChange={e=>setForm(p=>({...p,password:e.target.value}))} onKeyDown={e=>e.key==="Enter"&&submit()} />
        </div>
        <button className="btn btn-green" style={{ width:"100%", padding:"12px" }} onClick={submit} disabled={loading}>
          {loading ? <span className="pulse">Signing in…</span> : "Sign In →"}
        </button>

        <div style={{ marginTop:18, padding:14, background:"#0a110a", borderRadius:8, fontFamily:"'JetBrains Mono',monospace", fontSize:10, color:"#5a7a5a", lineHeight:1.9 }}>
          Demo accounts:<br/>
          <span style={{ color:"#4ade80" }}>ramesh_farmer</span> / demo123 &nbsp;(farmer)<br/>
          <span style={{ color:"#4ade80" }}>sarah_buyer</span> / demo123 &nbsp;(buyer)
        </div>
      </div>
    </div>
  );
}

// ── Main app ──────────────────────────────────────────────────────────────────
export default function App() {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("pg_user")); } catch { return null; }
  });
  if (!user) return <Login onLogin={setUser} />;
  return <Dashboard user={user} onLogout={()=>{ localStorage.clear(); setUser(null); }} />;
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
function Dashboard({ user, onLogout }) {
  const [tab, setTab] = useState("market");

  // — Marketplace —
  const [listings,     setListings]     = useState([]);
  const [listLoading,  setListLoading]  = useState(true);
  const [listError,    setListError]    = useState("");
  const [search,       setSearch]       = useState("");
  const [cropFilter,   setCropFilter]   = useState("all");
  const [selected,     setSelected]     = useState(null);
  const [orderQty,     setOrderQty]     = useState(1);
  const [orderMsg,     setOrderMsg]     = useState("");

  // — ML Prediction —
  const [predForm, setPredForm] = useState({
    crop_type:"wheat", area_hectares:5, planting_date:"2025-01-01",
    soil_type:"loam",  irrigation_type:"drip", rainfall_mm:550,
    temperature_avg:22, temperature_min:14, temperature_max:32,
    humidity_percent:65, solar_radiation:18, fertilizer_kg_per_ha:120,
    pesticide_applications:2,
  });
  const [predResult,  setPredResult]  = useState(null);
  const [predLoading, setPredLoading] = useState(false);
  const [predError,   setPredError]   = useState("");

  // — Disease Scan —
  const [scanResult,  setScanResult]  = useState(null);
  const [scanLoading, setScanLoading] = useState(false);
  const [scanImage,   setScanImage]   = useState(null);
  const [scanError,   setScanError]   = useState("");
  const fileRef = useRef();

  // ── Fetch listings ──────────────────────────────────────────────────────────
  const fetchListings = useCallback(async () => {
    setListLoading(true); setListError("");
    try {
      let url = "/api/listings?";
      if (cropFilter !== "all") url += "crop_type=" + cropFilter + "&";
      if (search.trim()) url += "search=" + encodeURIComponent(search.trim()) + "&";
      const data = await apiCall(url);
      setListings(data);
    } catch(e) { setListError(e.message); }
    finally    { setListLoading(false); }
  }, [cropFilter, search]);

  useEffect(() => { if (tab === "market") fetchListings(); }, [tab, fetchListings]);

  // ── Run yield prediction ────────────────────────────────────────────────────
  async function runPrediction() {
    setPredLoading(true); setPredError(""); setPredResult(null);
    try {
      const r = await apiCall("/api/predict/yield", { method:"POST", body:JSON.stringify(predForm) });
      setPredResult(r);
    } catch(e) { setPredError(e.message); }
    finally    { setPredLoading(false); }
  }

  // ── Scan disease image ──────────────────────────────────────────────────────
  async function handleScan(e) {
    const file = e.target.files[0];
    if (!file) return;
    setScanImage(URL.createObjectURL(file));
    setScanLoading(true); setScanError(""); setScanResult(null);
    try {
      const fd = new FormData();
      fd.append("image", file);
      const r = await apiCall("/api/scan/disease", { method:"POST", body:fd });
      setScanResult(r);
    } catch(e) { setScanError(e.message); }
    finally    { setScanLoading(false); e.target.value = ""; }
  }

  // ── Place order ─────────────────────────────────────────────────────────────
  async function placeOrder() {
    setOrderMsg("");
    try {
      const r = await apiCall("/api/orders", {
        method:"POST",
        body: JSON.stringify({ listing_id: selected.id, quantity_tons: orderQty }),
      });
      setOrderMsg("✅ Order " + r.order_id + " placed — Total $" + r.total_amount.toFixed(2));
    } catch(e) { setOrderMsg("⚠️ " + e.message); }
  }

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <div style={{ fontFamily:"'Cormorant Garamond',serif", background:"#080d08", minHeight:"100vh", color:"#e8f0e8" }}>
      <style>{css}</style>

      {/* Nav */}
      <nav style={{ borderBottom:"1px solid #1c2e1c", padding:"0 28px", display:"flex", alignItems:"center", justifyContent:"space-between", height:62, position:"sticky", top:0, background:"#080d08", zIndex:50 }}>
        <div style={{ display:"flex", alignItems:"center", gap:11 }}>
          <div style={{ width:34, height:34, borderRadius:9, background:"linear-gradient(135deg,#4ade80,#166534)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:17 }}>🌾</div>
          <div>
            <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:20, fontWeight:600, fontStyle:"italic", lineHeight:1 }}>PlantGuard</div>
            <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:9, color:"#5a7a5a", letterSpacing:".1em" }}>SMART AGRICULTURE PLATFORM</div>
          </div>
        </div>

        <div style={{ display:"flex", gap:3 }}>
          {[["market","🌐 Marketplace"],["predict","🔬 ML Pipeline"],["vision","👁️ Disease Scan"]].map(([k,lbl])=>(
            <button key={k} onClick={()=>setTab(k)} style={{ padding:"8px 16px", cursor:"pointer", fontFamily:"'JetBrains Mono',monospace", fontSize:11, letterSpacing:".05em", borderRadius:8, border:"none", background:tab===k?"#1c2e1c":"transparent", color:tab===k?"#4ade80":"#5a7a5a" }}>{lbl}</button>
          ))}
        </div>

        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:10, color:"#5a7a5a" }}>
            👤 {user.username} <span style={{ color:"#4ade80" }}>({user.role})</span>
          </div>
          <button className="btn btn-ghost" style={{ padding:"5px 12px", fontSize:10 }} onClick={onLogout}>Logout</button>
        </div>
      </nav>

      <div style={{ padding:"28px", maxWidth:1300, margin:"0 auto" }}>

        {/* ════ MARKETPLACE ════ */}
        {tab === "market" && (
          <div className="fade">
            <div style={{ marginBottom:22 }}>
              <h1 style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:36, fontStyle:"italic", fontWeight:400 }}>Crop Marketplace</h1>
              <p style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11, color:"#5a7a5a", marginTop:4 }}>Live data from Flask API · GET /api/listings</p>
            </div>

            <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:14, marginBottom:24 }}>
              <StatCard label="Listings"    value={listings.length}   sub="from Flask API"   icon="📋" />
              <StatCard label="Logged in"   value={user.username}     sub={user.role}         icon="👤" />
              <StatCard label="API"         value="● Live"            sub="localhost:5000"    icon="🔌" />
              <StatCard label="Database"    value="SQLite"            sub="agri.db"           icon="🗄️" />
            </div>

            <div style={{ display:"flex", gap:10, marginBottom:20, flexWrap:"wrap" }}>
              <input className="inp" placeholder="Search…" value={search}
                onChange={e=>setSearch(e.target.value)}
                onKeyDown={e=>e.key==="Enter"&&fetchListings()}
                style={{ maxWidth:260 }} />
              <select className="inp" value={cropFilter} onChange={e=>setCropFilter(e.target.value)} style={{ maxWidth:160 }}>
                <option value="all">All Crops</option>
                {["wheat","rice","corn","soybean","tomato","potato"].map(c=>(
                  <option key={c} value={c}>{CROP_ICON[c]} {c.charAt(0).toUpperCase()+c.slice(1)}</option>
                ))}
              </select>
              <button className="btn btn-green" style={{ padding:"8px 16px" }} onClick={fetchListings}>🔄 Refresh</button>
            </div>

            {listError && <div className="err">⚠️ {listError} — Make sure Flask is running: <code>python app.py</code></div>}

            {listLoading
              ? <div style={{ textAlign:"center", padding:60, fontFamily:"'JetBrains Mono',monospace", fontSize:12, color:"#4ade80" }} className="pulse">Fetching from API…</div>
              : <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(330px,1fr))", gap:14 }}>
                  {listings.map(l=>(
                    <div key={l.id} className="card" style={{ padding:18, cursor:"pointer" }} onClick={()=>{ setSelected(l); setOrderMsg(""); }}>
                      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:10 }}>
                        <div style={{ display:"flex", gap:10, alignItems:"center" }}>
                          <div style={{ width:38, height:38, borderRadius:9, background:`${CROP_COLOR[l.crop_type]||"#4ade80"}18`, border:`1px solid ${CROP_COLOR[l.crop_type]||"#4ade80"}33`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:19 }}>{CROP_ICON[l.crop_type]||"🌱"}</div>
                          <div>
                            <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:9, color:"#5a7a5a" }}>{l.crop_type.toUpperCase()}</div>
                            <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:15, fontStyle:"italic", lineHeight:1.2 }}>{l.title}</div>
                          </div>
                        </div>
                        <div style={{ textAlign:"right" }}>
                          <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:18, color:"#4ade80" }}>${l.price_per_ton}</div>
                          <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:9, color:"#5a7a5a" }}>per ton</div>
                        </div>
                      </div>
                      <p style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11, color:"#8aad8a", marginBottom:10, lineHeight:1.55 }}>{l.description}</p>
                      <div style={{ display:"flex", gap:5, flexWrap:"wrap", marginBottom:10 }}>
                        <Tag style={{ background:"#0a1f0a", color:"#4ade80" }}>⚖️ {l.quantity_tons}t</Tag>
                        <Tag style={{ background:"#1a1a09", color:"#fbbf24" }}>📍 {l.location}</Tag>
                        {l.verified ? <Tag style={{ background:"#090f1a", color:"#60a5fa" }}>✓ Verified</Tag> : null}
                        {(l.certifications||[]).map(c=><Tag key={c} style={{ background:"#150a1a", color:"#c084fc" }}>{c}</Tag>)}
                      </div>
                      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                        <span style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:10, color:"#5a7a5a" }}>👤 {l.farmer_name} · {l.views_count} views</span>
                        <button className="btn btn-green" style={{ padding:"5px 14px", fontSize:10 }}>View →</button>
                      </div>
                    </div>
                  ))}
                </div>
            }
          </div>
        )}

        {/* ════ ML PIPELINE ════ */}
        {tab === "predict" && (
          <div className="fade">
            <div style={{ marginBottom:22 }}>
              <h1 style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:36, fontStyle:"italic", fontWeight:400 }}>Yield Prediction</h1>
              <p style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11, color:"#5a7a5a", marginTop:4 }}>POST /api/predict/yield · Flask → Pandas feature engineering → TF model</p>
            </div>

            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:22, alignItems:"start" }}>
              <div className="card" style={{ padding:22 }}>
                <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:20, fontStyle:"italic", marginBottom:18 }}>Crop Parameters</div>
                <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
                  {[
                    { k:"crop_type",             lbl:"Crop Type",              t:"sel", o:["wheat","rice","corn","soybean","tomato","potato","other"] },
                    { k:"area_hectares",          lbl:"Area (ha)",              t:"num", min:0.1, step:0.5 },
                    { k:"planting_date",          lbl:"Planting Date",          t:"date" },
                    { k:"soil_type",              lbl:"Soil Type",              t:"sel", o:["loam","clay","sandy","silt","clay_loam"] },
                    { k:"irrigation_type",        lbl:"Irrigation",             t:"sel", o:["none","drip","sprinkler","flood"] },
                    { k:"rainfall_mm",            lbl:"Rainfall (mm)",          t:"num", min:0,   step:10 },
                    { k:"temperature_avg",        lbl:"Avg Temp (°C)",          t:"num", min:-10, step:0.5 },
                    { k:"humidity_percent",       lbl:"Humidity (%)",           t:"num", min:0,   max:100 },
                    { k:"fertilizer_kg_per_ha",   lbl:"Fertilizer (kg/ha)",     t:"num", min:0,   step:10 },
                    { k:"pesticide_applications", lbl:"Pesticide Apps",         t:"num", min:0,   step:1 },
                  ].map(f=>(
                    <div key={f.k}>
                      <label className="lbl">{f.lbl}</label>
                      {f.t==="sel"
                        ? <select className="inp" value={predForm[f.k]} onChange={e=>setPredForm(p=>({...p,[f.k]:e.target.value}))}>
                            {f.o.map(o=><option key={o} value={o}>{o}</option>)}
                          </select>
                        : <input className="inp" type={f.t} min={f.min} max={f.max} step={f.step}
                            value={predForm[f.k]}
                            onChange={e=>setPredForm(p=>({...p,[f.k]:f.t==="number"?parseFloat(e.target.value)||0:e.target.value}))} />
                      }
                    </div>
                  ))}
                </div>
                {predError && <div className="err" style={{ marginTop:14 }}>⚠️ {predError}</div>}
                <button className="btn btn-green" style={{ marginTop:18, width:"100%", padding:"11px" }} onClick={runPrediction} disabled={predLoading}>
                  {predLoading ? <span className="pulse">⚙️ Calling Flask API…</span> : "🔬 Run Yield Prediction"}
                </button>
              </div>

              <div>
                {!predResult && !predLoading && (
                  <div className="card" style={{ padding:48, textAlign:"center" }}>
                    <div style={{ fontSize:52, marginBottom:14 }}>🌱</div>
                    <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:22, fontStyle:"italic", color:"#5a7a5a" }}>Fill in parameters and run prediction</div>
                    <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:10, color:"#253525", marginTop:10 }}>Results come from your Flask API, not mock data</div>
                  </div>
                )}
                {predLoading && (
                  <div className="card" style={{ padding:48, textAlign:"center" }}>
                    <div style={{ fontSize:36, marginBottom:14 }} className="pulse">⚙️</div>
                    <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:12, color:"#4ade80" }}>Flask API processing…</div>
                  </div>
                )}
                {predResult && !predLoading && (
                  <div className="fade" style={{ display:"flex", flexDirection:"column", gap:14 }}>
                    <div className="card" style={{ padding:22 }}>
                      <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:9, color:"#5a7a5a", letterSpacing:".08em", marginBottom:6 }}>PREDICTED YIELD · FROM FLASK API</div>
                      <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:58, fontWeight:600, color:"#4ade80", lineHeight:1 }}>
                        {predResult.predicted_yield_tons}<span style={{ fontSize:22, color:"#5a7a5a" }}> tons</span>
                      </div>
                      <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11, color:"#8aad8a", marginTop:5 }}>
                        95% CI: [{predResult.lower_bound}t — {predResult.upper_bound}t]
                      </div>
                      <div style={{ display:"flex", gap:7, marginTop:10 }}>
                        <Tag style={{ background:"#0a1f0a", color:"#4ade80" }}>Confidence: {(predResult.confidence_score*100).toFixed(0)}%</Tag>
                        <Tag style={{ background:"#1a1509", color:"#fbbf24" }}>{predResult.model_version}</Tag>
                      </div>
                    </div>

                    <div className="card" style={{ padding:22 }}>
                      <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:18, fontStyle:"italic", marginBottom:14 }}>Feature Importance</div>
                      {Object.entries(predResult.feature_importance).sort((a,b)=>b[1]-a[1]).map(([k,v])=>(
                        <div key={k} style={{ marginBottom:9 }}>
                          <div style={{ display:"flex", justifyContent:"space-between", marginBottom:3 }}>
                            <span style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:10, color:"#8aad8a" }}>{k.replace(/_/g," ")}</span>
                            <span style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:10, color:"#4ade80" }}>{(v*100).toFixed(0)}%</span>
                          </div>
                          <div style={{ height:5, background:"#1c2e1c", borderRadius:3, overflow:"hidden" }}>
                            <div style={{ height:"100%", width:`${Math.min(100,v/0.28*100)}%`, background:"linear-gradient(90deg,#4ade80,#86efac)", borderRadius:3, transition:"width .8s ease" }} />
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="card" style={{ padding:22 }}>
                      <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:18, fontStyle:"italic", marginBottom:12 }}>Recommendations</div>
                      {predResult.recommendations.map((r,i)=>(
                        <div key={i} style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11, color:"#8aad8a", padding:"8px 0", borderBottom:i<predResult.recommendations.length-1?"1px solid #1c2e1c":"none", lineHeight:1.5 }}>{r}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ════ DISEASE SCAN ════ */}
        {tab === "vision" && (
          <div className="fade">
            <div style={{ marginBottom:22 }}>
              <h1 style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:36, fontStyle:"italic", fontWeight:400 }}>Crop Disease Detection</h1>
              <p style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11, color:"#5a7a5a", marginTop:4 }}>POST /api/scan/disease · Flask → OpenCV pipeline → annotated result</p>
            </div>

            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:22, alignItems:"start" }}>
              <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
                <div className="card" style={{ padding:28, textAlign:"center", cursor:"pointer", border:"2px dashed #253525" }}
                  onClick={()=>fileRef.current.click()}
                  onMouseEnter={e=>e.currentTarget.style.borderColor="#4ade80"}
                  onMouseLeave={e=>e.currentTarget.style.borderColor="#253525"}>
                  {scanImage
                    ? <img src={scanImage} alt="uploaded" style={{ maxHeight:240, maxWidth:"100%", borderRadius:8, objectFit:"contain" }} />
                    : <>
                        <div style={{ fontSize:48, marginBottom:10 }}>📸</div>
                        <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:20, fontStyle:"italic", marginBottom:5 }}>Upload crop photo</div>
                        <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:10, color:"#5a7a5a" }}>Sent to Flask → OpenCV pipeline</div>
                      </>
                  }
                  <input ref={fileRef} type="file" accept="image/*" style={{ display:"none" }} onChange={handleScan} />
                </div>

                <div className="card" style={{ padding:18 }}>
                  <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:17, fontStyle:"italic", marginBottom:12 }}>OpenCV Pipeline Stages</div>
                  {[
                    ["🔧","Pre-processing",    "CLAHE + NL-means denoising"],
                    ["🍃","Leaf Segmentation", "HSV green-range + morphological ops"],
                    ["🔬","Disease Detection", "Per-disease colour thresholds"],
                    ["📐","Bounding Boxes",    "findContours → BBox objects"],
                    ["🎨","Annotation",        "Overlay + base64 image export"],
                  ].map(([icon,s,d],i)=>(
                    <div key={s} style={{ display:"flex", gap:10, padding:"7px 0", borderBottom:i<4?"1px solid #1c2e1c":"none" }}>
                      <span style={{ fontSize:15 }}>{icon}</span>
                      <div style={{ flex:1 }}>
                        <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11 }}>{s}</div>
                        <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:9, color:"#5a7a5a", marginTop:2 }}>{d}</div>
                      </div>
                      <Tag style={{ background:"#0a1f0a", color:"#4ade80" }}>
                        {scanLoading&&i===2 ? <span className="pulse">⚙️</span> : "✓"}
                      </Tag>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                {scanError && <div className="err">⚠️ {scanError}</div>}
                {!scanResult && !scanLoading && !scanError && (
                  <div className="card" style={{ padding:48, textAlign:"center" }}>
                    <div style={{ fontSize:48, marginBottom:12 }}>🔎</div>
                    <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:22, fontStyle:"italic", color:"#5a7a5a" }}>Upload a crop image to scan</div>
                    <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:10, color:"#253525", marginTop:10 }}>Detects Leaf Blight · Rust · Mildew · Mosaic · Root Rot</div>
                  </div>
                )}
                {scanLoading && (
                  <div className="card" style={{ padding:48, textAlign:"center" }}>
                    <div style={{ fontSize:38, marginBottom:14 }} className="pulse">👁️</div>
                    <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:12, color:"#4ade80" }}>OpenCV pipeline running on Flask…</div>
                  </div>
                )}
                {scanResult && !scanLoading && (
                  <div className="fade" style={{ display:"flex", flexDirection:"column", gap:14 }}>
                    <div className="card" style={{ padding:22 }}>
                      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:8 }}>
                        <div>
                          <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:9, color:"#5a7a5a", letterSpacing:".08em", marginBottom:4 }}>OVERALL SEVERITY</div>
                          <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:38, fontWeight:600, color:SEV_COLOR[scanResult.overall_severity], lineHeight:1, textTransform:"capitalize" }}>
                            {scanResult.overall_severity==="none" ? "✅ Healthy" : scanResult.overall_severity}
                          </div>
                        </div>
                        <div style={{ textAlign:"right" }}>
                          <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:26, color:SEV_COLOR[scanResult.overall_severity] }}>{scanResult.total_affected_percent}%</div>
                          <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:9, color:"#5a7a5a" }}>affected area</div>
                        </div>
                      </div>
                      <div style={{ height:6, background:"#1c2e1c", borderRadius:3, overflow:"hidden" }}>
                        <div style={{ height:"100%", width:`${Math.min(100,scanResult.total_affected_percent*2)}%`, background:SEV_COLOR[scanResult.overall_severity], borderRadius:3, transition:"width 1s ease" }} />
                      </div>
                      <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:9, color:"#5a7a5a", marginTop:6 }}>
                        Processed in {scanResult.processing_time_ms}ms · {scanResult.opencv_metadata?.contour_count||0} contours
                      </div>
                    </div>

                    {scanResult.diseases?.length > 0 && (
                      <div className="card" style={{ padding:22 }}>
                        <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:18, fontStyle:"italic", marginBottom:12 }}>Detected Diseases</div>
                        {scanResult.diseases.map((d,i)=>(
                          <div key={i} style={{ padding:"10px 0", borderBottom:i<scanResult.diseases.length-1?"1px solid #1c2e1c":"none" }}>
                            <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:5 }}>
                              <div style={{ display:"flex", gap:9, alignItems:"center" }}>
                                <div style={{ width:11, height:11, borderRadius:"50%", background:d.color, flexShrink:0 }} />
                                <span style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:16, fontStyle:"italic" }}>{d.name}</span>
                              </div>
                              <div style={{ display:"flex", gap:6 }}>
                                <Tag style={{ background:"#0a1f0a", color:"#4ade80" }}>{(d.confidence*100).toFixed(0)}% conf</Tag>
                                <Tag style={{ background:"#1a1509", color:"#fbbf24" }}>{d.affected_area_percent}% area</Tag>
                              </div>
                            </div>
                            <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:10, color:"#8aad8a", lineHeight:1.55 }}>💊 {d.treatment}</div>
                          </div>
                        ))}
                      </div>
                    )}

                    {scanResult.annotated_image_b64 && (
                      <div className="card" style={{ padding:16 }}>
                        <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:16, fontStyle:"italic", marginBottom:10 }}>OpenCV Annotated Output</div>
                        <img src={"data:image/jpeg;base64,"+scanResult.annotated_image_b64} alt="annotated" style={{ width:"100%", borderRadius:8 }} />
                      </div>
                    )}

                    <div className="card" style={{ padding:22 }}>
                      <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:18, fontStyle:"italic", marginBottom:12 }}>Treatment Plan</div>
                      {(scanResult.recommendations||[]).map((r,i)=>(
                        <div key={i} style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11, color:"#8aad8a", padding:"8px 0", borderBottom:i<(scanResult.recommendations.length-1)?"1px solid #1c2e1c":"none", lineHeight:1.5 }}>{r}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Order modal */}
      {selected && (
        <div style={{ position:"fixed", inset:0, background:"rgba(0,0,0,.85)", display:"flex", alignItems:"center", justifyContent:"center", zIndex:100, padding:24 }} onClick={()=>setSelected(null)}>
          <div className="card fade" style={{ maxWidth:500, width:"100%", padding:26 }} onClick={e=>e.stopPropagation()}>
            <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:14 }}>
              <div style={{ display:"flex", gap:11, alignItems:"center" }}>
                <div style={{ width:44, height:44, borderRadius:10, background:`${CROP_COLOR[selected.crop_type]||"#4ade80"}18`, border:`1px solid ${CROP_COLOR[selected.crop_type]||"#4ade80"}33`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:22 }}>{CROP_ICON[selected.crop_type]||"🌱"}</div>
                <div>
                  <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:9, color:"#5a7a5a" }}>{selected.crop_type.toUpperCase()} · {selected.quality_grade}</div>
                  <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:19, fontStyle:"italic" }}>{selected.title}</div>
                </div>
              </div>
              <button className="btn btn-ghost" style={{ padding:"3px 9px", fontSize:11 }} onClick={()=>setSelected(null)}>✕</button>
            </div>

            <p style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11, color:"#8aad8a", marginBottom:14, lineHeight:1.6 }}>{selected.description}</p>

            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10, marginBottom:14 }}>
              {[["Price","$"+selected.price_per_ton+"/ton"],["Available",selected.quantity_tons+"t"],["Location",selected.location],["Harvest",selected.harvest_date||"TBD"]].map(([k,v])=>(
                <div key={k} style={{ background:"#0a110a", borderRadius:8, padding:"9px 13px" }}>
                  <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:9, color:"#5a7a5a", marginBottom:3 }}>{k.toUpperCase()}</div>
                  <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:13 }}>{v}</div>
                </div>
              ))}
            </div>

            {user.role === "buyer" && (
              <div style={{ marginBottom:14 }}>
                <label className="lbl">Quantity (tons)</label>
                <input className="inp" type="number" min={0.1} step={0.5} value={orderQty} onChange={e=>setOrderQty(parseFloat(e.target.value)||1)} />
                <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:10, color:"#4ade80", marginTop:4 }}>
                  Total: ${(orderQty * selected.price_per_ton).toFixed(2)}
                </div>
              </div>
            )}

            {orderMsg && (
              <div style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11, padding:"8px 12px", borderRadius:6, marginBottom:12,
                background:orderMsg.startsWith("✅")?"#0a1f0a":"#2a0a0a",
                color:orderMsg.startsWith("✅")?"#4ade80":"#f87171" }}>
                {orderMsg}
              </div>
            )}

            <div style={{ display:"flex", gap:8 }}>
              {user.role==="buyer"
                ? <button className="btn btn-green" style={{ flex:1, padding:"11px" }} onClick={placeOrder}>💼 Place Order via API</button>
                : <span style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:10, color:"#5a7a5a", alignSelf:"center" }}>Log in as buyer to place orders</span>
              }
              <button className="btn btn-ghost" style={{ padding:"11px 16px" }} onClick={()=>setSelected(null)}>Close</button>
            </div>
          </div>
        </div>
      )}

      <footer style={{ borderTop:"1px solid #1c2e1c", padding:"14px 28px", display:"flex", justifyContent:"space-between", alignItems:"center", marginTop:40 }}>
        <span style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:9, color:"#253525" }}>PLANTGUARD · FLASK :5000 ↔ REACT :5173</span>
        <div style={{ display:"flex", gap:8 }}>
          {["Flask API","OpenCV","TF Pipeline","SQLite"].map(t=>(
            <Tag key={t} style={{ background:"#0a110a", color:"#253525", border:"1px solid #1c2e1c" }}>{t}</Tag>
          ))}
        </div>
      </footer>
    </div>
  );
}
