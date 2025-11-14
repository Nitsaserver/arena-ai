# backend/trainer.py
import os
import pickle
import time
import numpy as np
from pathlib import Path
from typing import Tuple, Dict

# reuse your detector class
from backend.detector import ISLDetector

MODEL_PATH = Path(__file__).resolve().parent / "detector.pkl"

def featurize_rows(rows):
    """
    rows: iterable of objects/rows with attributes:
      attacker_action, defender_action, outcome, reward, meta_data
    Returns: numpy array (n_samples, n_features)
    Simple featurization:
      - attacker_action: hash -> bucket -> int
      - defender_action: hash -> bucket -> int
      - outcome: mapped to 0/1
      - reward: numeric
      - metadata length (string length)
    """
    def action_to_int(a):
        return abs(hash(a)) % 1000  # keep small integer buckets

    X = []
    for r in rows:
        aa = getattr(r, "attacker_action", "") or ""
        da = getattr(r, "defender_action", "") or ""
        out = getattr(r, "outcome", "") or ""
        reward = getattr(r, "reward", 0.0) or 0.0
        meta = getattr(r, "meta_data", "") or getattr(r, "metadata", "") or ""
        X.append([
            action_to_int(aa),
            action_to_int(da),
            1 if out.lower() in ("success","ok","allowed") else 0,
            float(reward),
            len(str(meta))
        ])
    return np.array(X, dtype=float)

def train_from_rows(rows, contamination=0.01) -> Tuple[ISLDetector, Dict]:
    """
    Train a new ISLDetector from rows (SQLAlchemy objects or simple dicts).
    Returns (detector_instance, summary_dict)
    """
    X = featurize_rows(rows)
    summary = {"n_samples": int(X.shape[0])}
    if X.shape[0] == 0:
        raise ValueError("No training rows")

    det = ISLDetector(contamination=contamination)
    det.train(X)

    # persist
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"detector": det, "trained_at": time.time(), "n_samples": int(X.shape[0])}, f)

    summary.update({
        "saved_to": str(MODEL_PATH),
        "contamination": contamination,
    })
    return det, summary

def load_saved_detector():
    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as f:
            payload = pickle.load(f)
            return payload.get("detector"), payload
    return None, None
