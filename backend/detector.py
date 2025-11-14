import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime

MODEL_PATH = "/app/backend/detector.pkl"

class ISLDetector:
    def __init__(self, contamination=0.01):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.is_trained = False
        self.last_trained = None
        self.n_samples = 0

    def train(self, X: np.ndarray):
        if X.shape[0] < 5:
            print("⚠️ Not enough data to train.")
            return
        self.model.fit(X)
        self.is_trained = True
        self.last_trained = datetime.utcnow()
        self.n_samples = X.shape[0]
        self.save()
        print(f"✅ Model trained on {X.shape[0]} samples.")

    def score(self, event):
        if not self.is_trained:
            return 0.0
        try:
            features = np.array([
                len(event.get("path", "")),
                len(str(event.get("payload", ""))),
                1 if any(c.isdigit() for c in str(event.get("payload", ""))) else 0,
                event.get("rate", 0.0)
            ]).reshape(1, -1)
            return float(self.model.score_samples(features)[0])
        except Exception as e:
            print(f"⚠️ Scoring failed: {e}")
            return 0.0

    def save(self):
        joblib.dump(self, MODEL_PATH)
        print(f"💾 Saved model to {MODEL_PATH}")

    def load(self):
        if os.path.exists(MODEL_PATH):
            print(f"📦 Loading model from {MODEL_PATH}")
            obj = joblib.load(MODEL_PATH)
            self.model = obj.model
            self.is_trained = obj.is_trained
            self.last_trained = obj.last_trained
            self.n_samples = obj.n_samples
        else:
            print("⚙️ No saved model found, using new detector.")
 # Global instance
detector = ISLDetector()