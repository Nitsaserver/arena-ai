from sqlalchemy.orm import Session
from datetime import datetime
import time
import json

from .database import SessionLocal
from .models import Event, Block, TrainingData, TrainingRun


# ==========================================================
# DB SESSION HELPER (DO NOT USE next(get_db()) ANYWHERE)
# ==========================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================================
# EVENTS
# ==========================================================

def insert_event(data: dict):
    """
    data MUST match Event model fields exactly
    """
    db = SessionLocal()
    try:
        ev = Event(**data)
        db.add(ev)
        db.commit()
        db.refresh(ev)
        return ev
    finally:
        db.close()


def list_events(limit: int = 100):
    db = SessionLocal()
    try:
        return (
            db.query(Event)
            .order_by(Event.ts.desc())
            .limit(limit)
            .all()
        )
    finally:
        db.close()


def latest_report():
    db = SessionLocal()
    try:
        return (
            db.query(Event)
            .filter(Event.flagged == 1)
            .order_by(Event.ts.desc())
            .first()
        )
    finally:
        db.close()


# ==========================================================
# BLOCKS
# ==========================================================

def add_block(ip: str, reason: str = "manual", expires_at: float | None = None):
    db = SessionLocal()
    try:
        block = db.query(Block).filter_by(ip=ip).first()
        if not block:
            block = Block(
                ip=ip,
                reason=reason,
                blocked_at=time.time(),
                expires_at=expires_at
            )
            db.add(block)
            db.commit()
            db.refresh(block)
        return block
    finally:
        db.close()


def list_blocks():
    db = SessionLocal()
    try:
        return db.query(Block).all()
    finally:
        db.close()


def remove_block(ip: str):
    db = SessionLocal()
    try:
        block = db.query(Block).filter_by(ip=ip).first()
        if block:
            db.delete(block)
            db.commit()
    finally:
        db.close()


# ==========================================================
# TRAINING DATA
# ==========================================================

def insert_training_record(db: Session, record: dict):
    """
    Uses an EXISTING session.
    Safe for background jobs / high-frequency inserts.
    """
    td = TrainingData(
        round_id=record.get("round_id"),
        attacker_action=record.get("attacker_action"),
        defender_action=record.get("defender_action"),
        outcome=record.get("outcome"),
        reward=record.get("reward"),
        meta_data=json.dumps(record.get("meta_data"))
        if record.get("meta_data") else None,
    )
    db.add(td)
    db.commit()
    db.refresh(td)
    return td


def list_training_records(db: Session, limit: int = 1000):
    return (
        db.query(TrainingData)
        .order_by(TrainingData.id.desc())
        .limit(limit)
        .all()
    )


# ==========================================================
# TRAINING RUNS
# ==========================================================

def insert_training_run(
    db: Session,
    n_samples: int,
    contamination: float,
    model_path: str,
    notes: str | None = None,
):
    tr = TrainingRun(
        timestamp=datetime.utcnow(),
        n_samples=n_samples,
        contamination=contamination,
        model_path=model_path,
        notes=notes,
    )
    db.add(tr)
    db.commit()
    db.refresh(tr)
    return tr


def list_training_runs(db: Session, limit: int = 100):
    return (
        db.query(TrainingRun)
        .order_by(TrainingRun.id.desc())
        .limit(limit)
        .all()
    )
