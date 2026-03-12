"""
PlantGuard - Smart Agriculture Assistant
Flask REST API - Marketplace + ML + Vision
"""

import hashlib
import json
import os
import secrets
import sqlite3
import sys
from functools import wraps

from flask import Flask, g, jsonify, request
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E402

from ml_pipeline.yield_predictor import CropFeatures  # noqa: E402
from ml_pipeline.yield_predictor import YieldPredictor  # noqa: E402
from vision.disease_detector import scan_uploaded_image  # noqa: E402

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agri.db")


# ---------------------------------------------------------------------------
# Database Schema
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    UNIQUE NOT NULL,
    email         TEXT    UNIQUE NOT NULL,
    password_hash TEXT    NOT NULL,
    role          TEXT    DEFAULT 'farmer',
    location      TEXT,
    farm_size     REAL,
    bio           TEXT,
    verified      INTEGER DEFAULT 0,
    created_at    TEXT    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tokens (
    token      TEXT    PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    created_at TEXT    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS crops (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id       INTEGER NOT NULL,
    crop_type       TEXT    NOT NULL,
    variety         TEXT,
    field_name      TEXT,
    area_hectares   REAL,
    planting_date   TEXT,
    soil_type       TEXT,
    irrigation_type TEXT,
    location        TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(farmer_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS listings (
    id            TEXT    PRIMARY KEY,
    farmer_id     INTEGER NOT NULL,
    title         TEXT    NOT NULL,
    crop_type     TEXT    NOT NULL,
    quantity_tons REAL    NOT NULL,
    price_per_ton REAL    NOT NULL,
    currency      TEXT    DEFAULT 'USD',
    harvest_date  TEXT,
    quality_grade TEXT,
    description   TEXT,
    status        TEXT    DEFAULT 'active',
    location      TEXT,
    certifications TEXT   DEFAULT '[]',
    views_count   INTEGER DEFAULT 0,
    created_at    TEXT    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(farmer_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id               TEXT    PRIMARY KEY,
    listing_id       TEXT    NOT NULL,
    buyer_id         INTEGER NOT NULL,
    quantity_tons    REAL    NOT NULL,
    agreed_price     REAL    NOT NULL,
    total_amount     REAL    NOT NULL,
    status           TEXT    DEFAULT 'pending',
    notes            TEXT,
    delivery_address TEXT,
    placed_at        TEXT    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(listing_id) REFERENCES listings(id),
    FOREIGN KEY(buyer_id)   REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS predictions (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id          INTEGER NOT NULL,
    crop_type          TEXT,
    predicted_yield    REAL,
    confidence         REAL,
    lower_bound        REAL,
    upper_bound        REAL,
    recommendations    TEXT,
    feature_importance TEXT,
    model_version      TEXT,
    created_at         TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS disease_scans (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id          INTEGER,
    severity           TEXT,
    total_affected_pct REAL,
    diseases           TEXT,
    recommendations    TEXT,
    processing_ms      REAL,
    annotated_image    TEXT,
    scanned_at         TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)
    db.commit()
    _seed_demo_data(db)
    db.close()
    print("  Database initialised at %s" % DB_PATH)


def _seed_demo_data(db):
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        return

    users = [
        (
            "ramesh_farmer",
            "ramesh@farm.com",
            _hash("demo123"),
            "farmer",
            "Punjab, India",
            12.5,
        ),
        (
            "sarah_buyer",
            "sarah@agri.co",
            _hash("demo123"),
            "buyer",
            "Mumbai, India",
            None,
        ),
        (
            "carlos_grower",
            "carlos@finca.mx",
            _hash("demo123"),
            "farmer",
            "Jalisco, Mexico",
            8.0,
        ),
        (
            "amina_trade",
            "amina@trade.ng",
            _hash("demo123"),
            "buyer",
            "Lagos, Nigeria",
            None,
        ),
    ]
    db.executemany(
        "INSERT INTO users "
        "(username,email,password_hash,role,location,farm_size) "
        "VALUES (?,?,?,?,?,?)",
        users,
    )
    db.commit()

    listings = [
        (
            "lst-001",
            1,
            "Premium Basmati Rice - Punjab Harvest",
            "rice",
            45.0,
            380.0,
            "USD",
            "2025-02-15",
            "Grade A",
            "Freshly harvested long-grain basmati, pesticide-free.",
            "Punjab, India",
            '["organic"]',
        ),
        (
            "lst-002",
            3,
            "Yellow Corn - Jalisco Fields",
            "corn",
            120.0,
            195.0,
            "USD",
            "2025-01-20",
            "Grade B",
            "Non-GMO yellow corn, suitable for feed and processing.",
            "Jalisco, Mexico",
            "[]",
        ),
        (
            "lst-003",
            1,
            "Whole Wheat - Winter Harvest",
            "wheat",
            200.0,
            260.0,
            "USD",
            "2025-03-01",
            "Grade A",
            "Hard red winter wheat, protein content 12%+.",
            "Punjab, India",
            '["fair-trade"]',
        ),
        (
            "lst-004",
            3,
            "Cherry Tomatoes - Greenhouse Grown",
            "tomato",
            8.5,
            1200.0,
            "USD",
            "2025-01-10",
            "Premium",
            "Vine-ripened cherry tomatoes, year-round supply.",
            "Jalisco, Mexico",
            '["organic","fair-trade"]',
        ),
    ]
    db.executemany(
        "INSERT INTO listings "
        "(id,farmer_id,title,crop_type,quantity_tons,price_per_ton,"
        "currency,harvest_date,quality_grade,description,location,certifications) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        listings,
    )
    db.commit()
    print("  Demo data seeded (4 users, 4 listings)")


# ---------------------------------------------------------------------------
# Auth Helpers
# ---------------------------------------------------------------------------


def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def _gen_token():
    return secrets.token_hex(32)


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
        if not token:
            return jsonify({"error": "Missing Authorization header"}), 401
        db = get_db()
        row = db.execute(
            "SELECT u.* FROM users u " "JOIN tokens t ON u.id=t.user_id WHERE t.token=?",
            (token,),
        ).fetchone()
        if not row:
            return jsonify({"error": "Invalid or expired token"}), 401
        g.user = dict(row)
        return f(*args, **kwargs)

    return decorated


# ---------------------------------------------------------------------------
# Auth Routes
# ---------------------------------------------------------------------------


@app.post("/api/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    for field in ("username", "email", "password", "role"):
        if not data.get(field):
            return jsonify({"error": "Missing field: %s" % field}), 400

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users "
            "(username,email,password_hash,role,location,farm_size,bio) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                data["username"],
                data["email"],
                _hash(data["password"]),
                data["role"],
                data.get("location", ""),
                data.get("farm_size"),
                data.get("bio", ""),
            ),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username or email already exists"}), 409

    user = db.execute("SELECT * FROM users WHERE username=?", (data["username"],)).fetchone()
    token = _gen_token()
    db.execute("INSERT INTO tokens (token,user_id) VALUES (?,?)", (token, user["id"]))
    db.commit()
    return jsonify({"token": token, "user": _user_dict(user)}), 201


@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    db = get_db()
    user = db.execute(
        "SELECT * FROM users " "WHERE (username=? OR email=?) AND password_hash=?",
        (
            data.get("username", ""),
            data.get("username", ""),
            _hash(data.get("password", "")),
        ),
    ).fetchone()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    token = _gen_token()
    db.execute("INSERT INTO tokens (token,user_id) VALUES (?,?)", (token, user["id"]))
    db.commit()
    return jsonify({"token": token, "user": _user_dict(user)})


# ---------------------------------------------------------------------------
# Marketplace Routes
# ---------------------------------------------------------------------------


@app.get("/api/listings")
def get_listings():
    db = get_db()
    args = request.args
    query = (
        "SELECT l.*, u.username AS farmer_name, "
        "u.location AS farmer_location, u.verified "
        "FROM listings l JOIN users u ON l.farmer_id=u.id "
        "WHERE l.status='active'"
    )
    params = []

    if args.get("crop_type"):
        query += " AND l.crop_type=?"
        params.append(args["crop_type"])
    if args.get("max_price"):
        query += " AND l.price_per_ton<=?"
        params.append(float(args["max_price"]))
    if args.get("min_qty"):
        query += " AND l.quantity_tons>=?"
        params.append(float(args["min_qty"]))
    if args.get("search"):
        s = "%" + args["search"] + "%"
        query += " AND (l.title LIKE ? OR l.description LIKE ?)"
        params += [s, s]

    query += " ORDER BY l.created_at DESC LIMIT 50"
    rows = db.execute(query, params).fetchall()
    return jsonify([_listing_dict(r) for r in rows])


@app.get("/api/listings/<listing_id>")
def get_listing(listing_id):
    db = get_db()
    db.execute(
        "UPDATE listings SET views_count=views_count+1 WHERE id=?",
        (listing_id,),
    )
    db.commit()
    row = db.execute(
        "SELECT l.*, u.username AS farmer_name, u.verified "
        "FROM listings l JOIN users u ON l.farmer_id=u.id WHERE l.id=?",
        (listing_id,),
    ).fetchone()
    if not row:
        return jsonify({"error": "Listing not found"}), 404
    return jsonify(_listing_dict(row))


@app.post("/api/listings")
@require_auth
def create_listing():
    if g.user["role"] != "farmer":
        return jsonify({"error": "Only farmers can create listings"}), 403

    data = request.get_json(silent=True) or {}
    for field in ("title", "crop_type", "quantity_tons", "price_per_ton"):
        if not data.get(field):
            return jsonify({"error": "Missing field: %s" % field}), 400

    import uuid

    lid = "lst-%s" % uuid.uuid4().hex[:8]
    db = get_db()
    db.execute(
        "INSERT INTO listings "
        "(id,farmer_id,title,crop_type,quantity_tons,price_per_ton,"
        "currency,harvest_date,quality_grade,description,location,certifications) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            lid,
            g.user["id"],
            data["title"],
            data["crop_type"],
            data["quantity_tons"],
            data["price_per_ton"],
            data.get("currency", "USD"),
            data.get("harvest_date"),
            data.get("quality_grade", ""),
            data.get("description", ""),
            data.get("location", ""),
            json.dumps(data.get("certifications", [])),
        ),
    )
    db.commit()
    row = db.execute(
        "SELECT l.*, u.username AS farmer_name, u.verified "
        "FROM listings l JOIN users u ON l.farmer_id=u.id WHERE l.id=?",
        (lid,),
    ).fetchone()
    return jsonify(_listing_dict(row)), 201


@app.post("/api/orders")
@require_auth
def place_order():
    if g.user["role"] != "buyer":
        return jsonify({"error": "Only buyers can place orders"}), 403

    data = request.get_json(silent=True) or {}
    db = get_db()
    listing = db.execute(
        "SELECT * FROM listings WHERE id=? AND status='active'",
        (data.get("listing_id"),),
    ).fetchone()
    if not listing:
        return jsonify({"error": "Listing not found or no longer active"}), 404

    qty = float(data.get("quantity_tons", 0))
    price = float(listing["price_per_ton"])
    total = qty * price

    import uuid

    oid = "ord-%s" % uuid.uuid4().hex[:8]
    db.execute(
        "INSERT INTO orders "
        "(id,listing_id,buyer_id,quantity_tons,agreed_price,"
        "total_amount,notes,delivery_address) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (
            oid,
            data["listing_id"],
            g.user["id"],
            qty,
            price,
            total,
            data.get("notes", ""),
            data.get("delivery_address", ""),
        ),
    )
    db.commit()
    return (
        jsonify({"order_id": oid, "total_amount": total, "status": "pending"}),
        201,
    )


@app.get("/api/dashboard")
@require_auth
def dashboard():
    db = get_db()
    user = g.user

    if user["role"] == "farmer":
        listings = db.execute("SELECT * FROM listings WHERE farmer_id=?", (user["id"],)).fetchall()
        preds = db.execute(
            "SELECT * FROM predictions WHERE farmer_id=? " "ORDER BY created_at DESC LIMIT 5",
            (user["id"],),
        ).fetchall()
        scans = db.execute(
            "SELECT id,severity,total_affected_pct,scanned_at "
            "FROM disease_scans WHERE farmer_id=? "
            "ORDER BY scanned_at DESC LIMIT 5",
            (user["id"],),
        ).fetchall()
        return jsonify(
            {
                "role": "farmer",
                "listings": [_listing_dict(r) for r in listings],
                "predictions": [dict(r) for r in preds],
                "disease_scans": [dict(r) for r in scans],
            }
        )

    orders = db.execute(
        "SELECT o.*, l.title, l.crop_type FROM orders o "
        "JOIN listings l ON o.listing_id=l.id "
        "WHERE o.buyer_id=? ORDER BY o.placed_at DESC",
        (user["id"],),
    ).fetchall()
    return jsonify({"role": "buyer", "orders": [dict(r) for r in orders]})


# ---------------------------------------------------------------------------
# ML Yield Prediction
# ---------------------------------------------------------------------------

predictor = YieldPredictor()


@app.post("/api/predict/yield")
@require_auth
def predict_yield():
    data = request.get_json(silent=True) or {}
    try:
        cf = CropFeatures(
            crop_type=data["crop_type"],
            area_hectares=float(data["area_hectares"]),
            planting_date=data["planting_date"],
            soil_type=data.get("soil_type", "loam"),
            irrigation_type=data.get("irrigation_type", "none"),
            rainfall_mm=float(data.get("rainfall_mm", 600)),
            temperature_avg=float(data.get("temperature_avg", 22)),
            temperature_min=float(data.get("temperature_min", 15)),
            temperature_max=float(data.get("temperature_max", 30)),
            humidity_percent=float(data.get("humidity_percent", 65)),
            solar_radiation=float(data.get("solar_radiation", 18)),
            fertilizer_kg_per_ha=float(data.get("fertilizer_kg_per_ha", 0)),
            pesticide_applications=int(data.get("pesticide_applications", 0)),
            historical_yield_avg=data.get("historical_yield_avg"),
        )
    except KeyError as e:
        return jsonify({"error": "Missing required field: %s" % e}), 400

    try:
        result = predictor.predict(cf)
    except Exception as e:
        return jsonify({"error": "Prediction error: %s" % str(e)}), 500

    db = get_db()
    db.execute(
        "INSERT INTO predictions "
        "(farmer_id,crop_type,predicted_yield,confidence,lower_bound,"
        "upper_bound,recommendations,feature_importance,model_version) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (
            g.user["id"],
            data["crop_type"],
            result.predicted_yield_tons,
            result.confidence_score,
            result.lower_bound,
            result.upper_bound,
            json.dumps(result.recommendations),
            json.dumps(result.feature_importance),
            result.model_version,
        ),
    )
    db.commit()

    return jsonify(
        {
            "predicted_yield_tons": result.predicted_yield_tons,
            "confidence_score": result.confidence_score,
            "lower_bound": result.lower_bound,
            "upper_bound": result.upper_bound,
            "feature_importance": result.feature_importance,
            "recommendations": result.recommendations,
            "model_version": result.model_version,
        }
    )


# ---------------------------------------------------------------------------
# Computer Vision Disease Scan
# ---------------------------------------------------------------------------


@app.post("/api/scan/disease")
@require_auth
def scan_disease():
    try:
        if request.files.get("image"):
            image_data = request.files["image"].read()
        elif request.is_json and request.json.get("image_b64"):
            import base64

            image_data = base64.b64decode(request.json["image_b64"])
        else:
            return (
                jsonify({"error": ("Provide image as multipart file or image_b64 in JSON")}),
                400,
            )

        result = scan_uploaded_image(image_data)

        db = get_db()
        db.execute(
            "INSERT INTO disease_scans "
            "(farmer_id,severity,total_affected_pct,diseases,"
            "recommendations,processing_ms,annotated_image) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                g.user["id"],
                result["overall_severity"],
                result["total_affected_percent"],
                json.dumps(result["diseases"]),
                json.dumps(result["recommendations"]),
                result["processing_time_ms"],
                result.get("annotated_image_b64", ""),
            ),
        )
        db.commit()
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _user_dict(row):
    d = dict(row)
    d.pop("password_hash", None)
    return d


def _listing_dict(row):
    d = dict(row)
    if isinstance(d.get("certifications"), str):
        try:
            d["certifications"] = json.loads(d["certifications"])
        except Exception:
            d["certifications"] = []
    return d


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("PlantGuard - Smart Agriculture API")
    print("------------------------------------")
    init_db()
    print("  Server starting on http://localhost:5000")
    print("  Demo login -> ramesh_farmer / demo123  (farmer)")
    print("             -> sarah_buyer   / demo123  (buyer)")
    print("------------------------------------")
    app.run(debug=True, port=5000)
