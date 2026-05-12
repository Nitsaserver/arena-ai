from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.responses import FileResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List
import csv, io, json, time, os, random, numpy as np
import uvicorn

# ✅ Internal imports
from .database import init_db, get_db, SessionLocal
from .crud import (
    insert_event, list_events, add_block, list_blocks, remove_block,
    latest_report, insert_training_record, list_training_records
)
from backend.detector import detector, ISLDetector
from .models import User, Team, Match
from .simulation import simulate_round

import asyncio
from datetime import datetime


from .trainer import train_from_rows, load_saved_detector
import pickle

from backend.rag.service import rag_service

from backend.api import explain
from backend.api.rag import router as rag_router

# --------------------------------------
# ⚙️ App Initialization
# --------------------------------------
app = FastAPI(title="Arena API")
app.include_router(
    rag_router,
    prefix="/rag",
    tags=["RAG"]
)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}

# --------------------------------------
# 🌐 CORS + Frontend Mount

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your frontend dev port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------
# 🩺 Health & Dashboard Routes
# --------------------------------------



@app.get("/dashboard", response_class=FileResponse)
@app.get("/dashboard/", response_class=FileResponse)
def serve_dashboard():
    return frontend_path / "index.html"

@app.get("/")
def root():
    return RedirectResponse(url="/dashboard")

# ==========================================
# 🔁 Background Retraining Loop (Improved + Logged)
# ==========================================
import threading

async def retrain_loop():
    """
    Continuously retrains the ML detector every 5 minutes,
    logs results to DB (training_runs), and saves model.
    """
    await asyncio.sleep(10)  # wait for DB + app startup

    while True:
        try:
            db = SessionLocal()
            rows = list_training_records(db, limit=5000)

            if not rows:
                print("⚠️ No training data available for retraining.")
            else:
                X = []
                for r in rows:
                    try:
                        meta = eval(r.meta_data) if r.meta_data else {}
                        X.append([
                            len(meta.get("path", "")),
                            len(str(meta.get("payload", ""))),
                            1 if any(c.isdigit() for c in str(meta.get("payload", ""))) else 0,
                            0.0
                        ])
                    except Exception:
                        continue

                if X:
                    # 🧠 Retrain the in-memory model
                    detector.train(np.array(X))
                    model_path = "/app/backend/detector.pkl"

                    # 💾 Try saving the model
                    try:
                        import trainer
                        trainer.save_detector(detector, model_path)
                        print(f"💾 Model saved to {model_path}")
                    except Exception:
                        print("⚠️ Could not explicitly save model (may already be persisted).")

                    # 🧾 Log this training run in DB
                    try:
                        from .crud import insert_training_run
                        insert_training_run(
                            db,
                            n_samples=len(X),
                            contamination=0.01,
                            model_path=model_path,
                            notes="auto-retrain"
                        )
                    except Exception as log_err:
                        print(f"⚠️ Failed to record training run: {log_err}")

                    print(f"✅ Retrained on {len(X)} samples at {datetime.utcnow()}")

            db.close()

        except Exception as e:
            print(f"⚠️ Retrain loop error: {e}")

        # Wait 5 minutes before next retrain cycle
        await asyncio.sleep(300)


# --------------------------------------
# 🚀 Startup Logic
# --------------------------------------
@app.on_event("startup")
def startup():
    """Initialize database, load detector, and start retraining loop."""
    init_db()
    detector.load()

    # ✅ Start retraining loop safely in background thread
    threading.Thread(
        target=lambda: asyncio.run(retrain_loop()),
        daemon=True
    ).start()

    print("🚀 Arena backend started successfully with auto-retrain enabled.")

# --------------------------------------
# 🧠 ML Training Data Endpoints
# =======================================
# 🧠 ML TRAINING DATA ENDPOINTS (FINAL)
# =======================================

@app.post("/train/data", status_code=201)
def add_training_data(payload: dict, db: Session = Depends(get_db)):
    """
    Accept a single training record as JSON.
    """
    rec = insert_training_record(db, payload)
    return {"id": rec.id}


@app.get("/train/data/export")
def export_training_data_csv(db: Session = Depends(get_db), limit: int = 10000):
    """
    Streams all training data as CSV (for local ML analysis).
    """
    rows = list_training_records(db, limit=limit) or []

    def get_field(r, names, default=""):
        for n in names:
            if isinstance(r, dict):
                if n in r:
                    return r[n]
            elif hasattr(r, n):
                return getattr(r, n)
        return default

    def generator():
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            "id", "round_id", "attacker_action", "defender_action",
            "outcome", "reward", "meta_data", "timestamp"
        ])
        yield buf.getvalue()
        buf.seek(0); buf.truncate(0)

        for r in reversed(rows):
            id_ = get_field(r, ("id",))
            round_id = get_field(r, ("round_id", "round"))
            attacker = get_field(r, ("attacker_action",))
            defender = get_field(r, ("defender_action",))
            outcome = get_field(r, ("outcome",))
            reward = get_field(r, ("reward",))
            meta = get_field(r, ("meta_data", "metadata"))
            ts = get_field(r, ("timestamp", "ts"))
            ts_val = ts.isoformat() if hasattr(ts, "isoformat") else str(ts or "")
            writer.writerow([id_, round_id, attacker, defender, outcome, reward, meta, ts_val])
            yield buf.getvalue()
            buf.seek(0); buf.truncate(0)

    return StreamingResponse(
        generator(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=training_data.csv"},
    )


# --------------------------------------
# 🧠 AUTO TRAIN FROM DB
# --------------------------------------
@app.post("/train/auto")
def train_auto(contamination: float = 0.01, limit: int = 10000, db: Session = Depends(get_db)):
    """
    Train detector from DB training_data and save model.
    """
    rows = list_training_records(db, limit=limit)
    if not rows:
        raise HTTPException(status_code=404, detail="No training data available")

    try:
        det, summary = train_from_rows(rows, contamination=contamination)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")

    try:
        import detector as detector_module
        detector_module.detector = det
    except Exception:
        pass

    return {"status": "trained", **summary}


# --------------------------------------
# 🧾 TRAINING RUN HISTORY
# --------------------------------------
@app.get("/train/history")
def get_training_history(limit: int = 20, db: Session = Depends(get_db)):
    """
    Returns recent retraining runs stored in `training_runs` table.
    """
    from .models import TrainingRun
    runs = (
        db.query(TrainingRun)
        .order_by(TrainingRun.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            "n_samples": r.n_samples,
            "contamination": r.contamination,
            "model_path": r.model_path,
            "notes": r.notes,
        }
        for r in runs
    ]


# --------------------------------------
# 🔁 MANUAL RETRAIN
# --------------------------------------
@app.post("/train/retrain")
def manual_retrain(db: Session = Depends(get_db)):
    """
    Manually retrains the anomaly detector immediately.
    """
    rows = list_training_records(db, limit=5000)
    if not rows:
        raise HTTPException(status_code=404, detail="No training data")

    X = []
    for r in rows:
        try:
            meta = eval(r.meta_data) if r.meta_data else {}
            X.append([
                len(meta.get("path", "")),
                len(str(meta.get("payload", ""))),
                1 if any(c.isdigit() for c in str(meta.get("payload", ""))) else 0,
                0.0
            ])
        except Exception:
            continue

    if X:
        detector.train(np.array(X))
        return {"status": "retrained", "samples": len(X)}

    return {"status": "no_valid_data"}


# --------------------------------------
# 📊 MODEL STATUS
# --------------------------------------
@app.get("/ml/status")
def ml_status():
    return {
        "trained": detector.is_trained,
        "samples": detector.n_samples,
        "last_trained": str(detector.last_trained) if detector.last_trained else None,
        "model_path": "/app/backend/detector.pkl"
    }









# --------------------------------------
# 🧩 Event & Block Management
# --------------------------------------
class EventIn(BaseModel):
    ip: str
    path: str
    payload: dict
    agent: Optional[str] = None
    ts: Optional[float] = None


class EventOut(BaseModel):
    id: int
    ts: float
    src_ip: str
    dest_ip: Optional[str] = None
    action: str
    details: Optional[str] = None
    score: float = 0.0
    flagged: bool





class BlockIn(BaseModel):
    ip: str
    reason: Optional[str] = "manual"
    expires_at: Optional[float] = None

THRESHOLD = float(os.getenv("DETECTOR_THRESHOLD", "-0.15"))


@app.post("/event")
def post_event(ev: EventIn, db: Session = Depends(get_db)):
    obj = ev.dict()
    obj["ts"] = obj.get("ts", time.time())
    obj["rate"] = 0.0

    try:
        score = detector.score(obj)
    except Exception:
        score = 0.0

    flagged = (score < THRESHOLD)

    db_obj = {
    "src_ip": obj.get("ip"),                     # ✅ map correctly
    "dest_ip": None,
    "action": obj.get("path", "unknown"),
    "ts": obj["ts"],
    "flagged": int(flagged),
    "details": json.dumps(obj.get("payload", {})),  # ✅ keep small
    }



    # ✅ Store the event in DB
    insert_event(db_obj)

    # ✅ NEW: Log training data automatically
   # ⚡ FAST, non-blocking training insert (safe)
    train_sample = {
        "round_id": random.randint(1, 10),
        "attacker_action": obj.get("path", "unknown"),
        "defender_action": "block" if flagged else "allow",
        "outcome": "failure" if flagged else "success",
        "reward": -1.0 if flagged else 1.0,
        "meta_data": None,  # 🚨 KEEP THIS SMALL
    }

    try:
        from .models import TrainingData
        db.add(TrainingData(**train_sample))
    except Exception:
        pass


    # ✅ Handle anomaly blocking
    action = None
    if flagged:
        add_block(obj["ip"], reason="auto:anomaly")
        action = "block"

    return {"status": "ok", "score": score, "flagged": flagged, "action": action}


@app.get("/events", response_model=List[EventOut])
def get_events(limit: int = 100):
    rows = list_events(limit)
    return [
        {
            "id": r.id,
            "ts": r.ts,
            "src_ip": r.src_ip,          # ✅ FIX
            "dest_ip": r.dest_ip,
            "action": r.action,
            "details": r.details,
            "score": getattr(r, "score", 0.0),
            "flagged": bool(r.flagged),
        }
        for r in rows
    ]






@app.get("/blocks")
def get_blocks():
    rows = list_blocks()
    return [
        {"ip": b.ip, "blocked_at": b.blocked_at, "reason": b.reason, "expires_at": b.expires_at}
        for b in rows
    ]

@app.post("/blocks")
def post_block(b: BlockIn):
    add_block(b.ip, b.reason, b.expires_at)
    return {"status": "ok"}

@app.delete("/blocks/{ip}")
def delete_block(ip: str):
    remove_block(ip)
    return {"status": "ok"}

# --------------------------------------
# 🤖 ML Training Simulation Endpoint
# --------------------------------------
@app.post("/train")
def train(n_samples: int = 1000, contamination: float = 0.01):
    X = []
    for _ in range(n_samples):
        path = "/search"
        payload = {"q": "hello world " + str(random.randint(1, 1000))}
        e = {"path": path, "payload": payload, "rate": random.random() * 0.1}
        X.append([
            len(e["path"]),
            len(str(e["payload"])),
            1 if any(c.isdigit() for c in str(payload)) else 0,
            e["rate"],
        ])
    det = ISLDetector(contamination=contamination)
    det.train(np.array(X))
    global detector
    detector = det
    return {"status": "trained", "samples": n_samples, "contamination": contamination}

@app.post("/train/auto")
def auto_train(db: Session = Depends(get_db)):
    records = list_training_records(db)
    if not records:
        raise HTTPException(status_code=400, detail="No training data available")

    # Convert to numpy for ML
    X = []
    for r in records:
        X.append([
            len(r.attacker_action or ""),
            len(r.defender_action or ""),
            r.reward or 0.0
        ])
    X = np.array(X)

    # Train new IsolationForest
    from sklearn.ensemble import IsolationForest
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)

    # Save model state (pickle to /app/models/detector.pkl)
    import joblib
    joblib.dump(model, "/app/backend/detector.pkl")

    return {"status": "trained", "samples": len(X)}

# --------------------------------------
# 📊 Analytics & Reports
# --------------------------------------
@app.get("/report/latest")
def get_latest_report():
    r = latest_report()
    if not r:
        raise HTTPException(status_code=404, detail="no report")
    return {"id": r.id, "ts": r.ts, "summary": r.summary}

@app.get("/analytics")
def get_analytics():
    events = list_events(1000)
    blocks = list_blocks()
    total_events = len(events)
    flagged_events = len([e for e in events if e.flagged])
    blocked_ips = len(blocks)
    flagged_percentage = (flagged_events / total_events * 100) if total_events > 0 else 0
    return {
        "total_events": total_events,
        "flagged_events": flagged_events,
        "blocked_ips": blocked_ips,
        "flagged_percentage": round(flagged_percentage, 2),
    }

# --------------------------------------
# 🧩 CRUD Endpoints: Users, Teams, Matches
# --------------------------------------
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "email": u.email} for u in users]

@app.post("/users")
def create_user(user: dict = Body(...), db: Session = Depends(get_db)):
    allowed_fields = {"username", "email"}
    valid_data = {k: v for k, v in user.items() if k in allowed_fields}
    if "username" not in valid_data or "email" not in valid_data:
        raise HTTPException(status_code=400, detail="Missing 'username' or 'email'")
    new_user = User(**valid_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created", "user": valid_data}

@app.put("/users/{user_id}")
def update_user(user_id: int, updated_data: dict = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in updated_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return {"message": "User updated", "user": {"id": user.id, "username": user.username}}

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@app.get("/teams")
def get_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    return [{"id": t.id, "name": t.name, "description": t.description} for t in teams]

@app.post("/teams")
def create_team(team: dict = Body(...), db: Session = Depends(get_db)):
    allowed_fields = {"name", "description"}
    valid_data = {k: v for k, v in team.items() if k in allowed_fields}
    if "name" not in valid_data:
        raise HTTPException(status_code=400, detail="Missing 'name'")
    new_team = Team(**valid_data)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return {"message": "Team created", "team": valid_data}

@app.get("/matches")
def get_matches(db: Session = Depends(get_db)):
    matches = db.query(Match).all()
    return [{"id": m.id, "team_a": m.team_a, "team_b": m.team_b, "score": m.score} for m in matches]

@app.post("/matches")
def create_match(match: dict = Body(...), db: Session = Depends(get_db)):
    allowed_fields = {"team_a", "team_b", "score"}
    valid_data = {k: v for k, v in match.items() if k in allowed_fields}
    if "team_a" not in valid_data or "team_b" not in valid_data:
        raise HTTPException(status_code=400, detail="Missing required fields: team_a or team_b")
    new_match = Match(**valid_data)
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return {"message": "Match created", "match": valid_data}

# --------------------------------------
# 🎮 Simulation Endpoint
# --------------------------------------
@app.post("/simulate")
def run_simulation(rounds: int = 5):
    results = []
    for i in range(1, rounds + 1):
        r = simulate_round(i)
        results.append({
            "round": r.round_number,
            "attacker_action": r.attacker_action,
            "defender_action": r.defender_action,
            "outcome": r.outcome,
            "reasoning": r.reasoning_log,
            "scores": {"red": r.score_red, "blue": r.score_blue},
        })
        time.sleep(0.5)
    return {"message": "Simulation completed", "rounds": results}

class DetectIn(BaseModel):
    ip: str
    path: Optional[str] = None
    payload: Optional[dict] = None
    ml: Optional[float] = None
    rep: Optional[float] = None

    class Config:
        extra = "allow"   # 👈 THIS is the key

from fastapi import Request

@app.post("/detect")
async def detect(request: Request, db: Session = Depends(get_db)):
    data = {}

    try:
        data = await request.json()
    except:
        pass

    data.update(dict(request.query_params))

    ip = (
        data.get("ip")
        or request.headers.get("x-forwarded-for")
        or request.client.host
    )

    obj = {
        "ip": ip,
        "path": data.get("path", "/detect"),
        "payload": data,
        "rate": float(data.get("ml", 0.0)),
    }

    try:
        score = detector.score(obj)
    except Exception:
        score = 0.0

    flagged = score < THRESHOLD

    safe_details = {
    "path": data.get("path"),
    "ml": data.get("ml"),
    "rep": data.get("rep"),
    "flagged": flagged,
    }

    insert_event({
        "src_ip": ip,
        "dest_ip": None,
        "action": "detect",
        "ts": time.time(),
        "flagged": flagged,
        "details": json.dumps(safe_details),
    })


    if flagged:
        add_block(ip, reason="auto:detect")

    return {
        "ip": ip,
        "flagged": flagged,
        "score": score,
        "action": "block" if flagged else "allow",
    }





# --------------------------------------
BASE_DIR = Path(__file__).resolve().parent
frontend_path = BASE_DIR / "frontend_dist"

app.include_router(explain.router, prefix="/api")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


# --------------------------------------
# 🚀 Main Entrypoint
# --------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

