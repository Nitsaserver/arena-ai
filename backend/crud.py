from .database import SessionLocal
from .models import Event, Block
from sqlalchemy.orm import Session
import time
from . import models
from sqlalchemy.orm import Session
import json
from sqlalchemy.orm import Session
from .models import TrainingRun
from datetime import datetime
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def insert_event(data: dict):
    db = next(get_db())
    ev = Event(**data)
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev

def list_events(limit: int = 100):
    db = next(get_db())
    return db.query(Event).order_by(Event.ts.desc()).limit(limit).all()

def add_block(ip: str, reason: str = "manual", expires_at: float = None):
    db = next(get_db())
    block = db.query(Block).filter_by(ip=ip).first()
    if not block:
        block = Block(ip=ip, reason=reason, blocked_at=time.time(), expires_at=expires_at)
        db.add(block)
        db.commit()
        db.refresh(block)
    return block

def list_blocks():
    db = next(get_db())
    return db.query(Block).all()

def remove_block(ip: str):
    db = next(get_db())
    block = db.query(Block).filter_by(ip=ip).first()
    if block:
        db.delete(block)
        db.commit()

def latest_report():
    db = next(get_db())
    # Example: get last event flagged as anomaly
    return db.query(Event).filter(Event.flagged==1).order_by(Event.ts.desc()).first()


def insert_training_record(db: Session, record: dict):
    td = models.TrainingData(
        round_id=record.get("round_id"),
        attacker_action=record.get("attacker_action"),
        defender_action=record.get("defender_action"),
        outcome=record.get("outcome"),
        reward=record.get("reward"),
        meta_data=json.dumps(record.get("metadata")) if record.get("metadata") else None,
    )
    db.add(td)
    db.commit()
    db.refresh(td)
    return td

def list_training_records(db: Session, limit: int = 1000):
    return db.query(models.TrainingData).order_by(models.TrainingData.id.desc()).limit(limit).all()

def insert_training_run(db: Session, n_samples: int, contamination: float, model_path: str, notes: str = None):
    tr = TrainingRun(
        timestamp=datetime.utcnow(),
        n_samples=n_samples,
        contamination=contamination,
        model_path=model_path,
        notes=notes
    )
    db.add(tr)
    db.commit()
    db.refresh(tr)
    return tr

def list_training_runs(db: Session, limit: int = 100):
    return db.query(TrainingRun).order_by(TrainingRun.id.desc()).limit(limit).all()