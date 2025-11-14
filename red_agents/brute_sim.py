#!/usr/bin/env python3
"""
Improved BruteForceAgent (Docker-ready)
- waits for backend readiness before sending events
- configurable via env vars (ARENA_EVENT_URL, BRUTE_ATTEMPTS, etc.)
- simple retries + exponential backoff
"""
import os
import time
import random
import logging
import requests
from dataclasses import dataclass
from typing import List, Dict

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("BruteForceAgent")

# Config (env-friendly)
DEFAULT_URL = os.getenv("ARENA_EVENT_URL", "http://backend:8000/event")
HEALTH_CHECK = os.getenv("ARENA_HEALTH_PATH", "http://backend:8000/events")
DEFAULT_PAUSE = float(os.getenv("BRUTE_PAUSE", "0.3"))
DEFAULT_ATTEMPTS = int(os.getenv("BRUTE_ATTEMPTS", "40"))
DEFAULT_TIMEOUT = float(os.getenv("BRUTE_TIMEOUT", "3.0"))
DEFAULT_RETRIES = int(os.getenv("BRUTE_RETRIES", "3"))
DEFAULT_WAIT_RETRIES = int(os.getenv("BACKEND_WAIT_RETRIES", "15"))
DEFAULT_WAIT_INTERVAL = float(os.getenv("BACKEND_WAIT_INTERVAL", "2.0"))

@dataclass
class BruteForceAgent:
    combos: List[str] = None
    url: str = DEFAULT_URL
    pause: float = DEFAULT_PAUSE
    attempts: int = DEFAULT_ATTEMPTS
    timeout: float = DEFAULT_TIMEOUT
    retries: int = DEFAULT_RETRIES

    def __post_init__(self):
        if self.combos is None:
            self.combos = ["admin:admin", "admin:123456", "user:user", "test:1234"]

    def make_event(self) -> Dict:
        ip = f"10.0.1.{random.randint(2,254)}"
        payload = {"auth": random.choice(self.combos)}
        body = {"ip": ip, "path": "/auth", "payload": payload, "agent": "brute_sim"}
        return body

    def post_event(self, body: Dict) -> Dict:
        # retry with exponential backoff
        backoff = 0.5
        for attempt in range(1, self.retries + 2):
            try:
                r = requests.post(self.url, json=body, timeout=self.timeout)
                r.raise_for_status()
                try:
                    return {"status": "ok", "code": r.status_code, "json": r.json()}
                except Exception:
                    return {"status": "ok", "code": r.status_code, "json": None}
            except requests.RequestException as e:
                log.warning(f"Attempt {attempt} failed: {e}")
                if attempt <= self.retries:
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    return {"status": "error", "error": str(e)}
        return {"status": "error", "error": "unreachable"}

    def run(self):
        log.info(f"Starting BruteForceAgent -> {self.attempts} attempts to {self.url}")
        results = []
        for i in range(self.attempts):
            ev = self.make_event()
            resp = self.post_event(ev)
            results.append(resp)
            if resp.get("status") == "ok":
                log.info(f"[{i+1}/{self.attempts}] posted, code={resp.get('code')}")
            else:
                log.error(f"[{i+1}/{self.attempts}] failed -> {resp.get('error')}")
            time.sleep(self.pause)
        log.info("BruteForceAgent finished")
        return results

# --- helper: wait for backend ---
def wait_for_backend(url: str = HEALTH_CHECK, max_retries: int = DEFAULT_WAIT_RETRIES, interval: float = DEFAULT_WAIT_INTERVAL) -> bool:
    log.info(f"Waiting for backend health at {url} (max {max_retries} attempts)...")
    for i in range(1, max_retries + 1):
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                log.info("✅ Backend is ready.")
                return True
            else:
                log.warning(f"Health check returned {r.status_code}. attempt {i}/{max_retries}")
        except Exception as e:
            log.debug(f"Health check attempt {i} failed: {e}")
        time.sleep(interval)
    log.error("❌ Backend did not become ready in time.")
    return False

# --- CLI runner ---
if __name__ == "__main__":
    # allow overriding via env at container runtime
    url = os.getenv("ARENA_EVENT_URL", DEFAULT_URL)
    attempts = int(os.getenv("BRUTE_ATTEMPTS", DEFAULT_ATTEMPTS))
    pause = float(os.getenv("BRUTE_PAUSE", DEFAULT_PAUSE))

    # Wait for backend before starting attacks
    if not wait_for_backend():
        log.error("Exiting: backend not available.")
        raise SystemExit(1)

    agent = BruteForceAgent(url=url, attempts=attempts, pause=pause)
    agent.run()
