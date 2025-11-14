#!/usr/bin/env python3
import requests
import time
import random
import os

BACKEND = os.getenv("ARENA_API", "http://backend:8000")
PAUSE = float(os.getenv("BLUE_PAUSE", 5))
BLOCK_EXPIRE_MINUTES = 30  # configurable

# Reputation table in memory
reputation = {}   # { ip: score }
blocked_cache = set()


# -------------------------------------------
# Helper: Fetch latest events
# -------------------------------------------
def get_latest_events():
    try:
        r = requests.get(f"{BACKEND}/events?limit=10", timeout=5)
        if r.ok:
            return r.json()
    except Exception as e:
        print("❌ Error fetching events:", e)
    return []


# -------------------------------------------
# Helper: Fetch ML anomaly score
# -------------------------------------------
def get_anomaly_score(event):
    """Ask the backend ML model to score an event"""
    try:
        r = requests.post(f"{BACKEND}/detect", json=event, timeout=5)
        if r.ok:
            return r.json().get("score", 0.0)
    except Exception as e:
        print("❌ Error calling ML detector:", e)
    return 0.0


# -------------------------------------------
# Helper: Block IP
# -------------------------------------------
def block_ip(ip, reason):
    if ip in blocked_cache:
        print(f"⚠️  Already blocked: {ip}")
        return

    payload = {
        "ip": ip,
        "reason": reason,
        "expires_in": BLOCK_EXPIRE_MINUTES,
    }

    try:
        res = requests.post(f"{BACKEND}/blocks", json=payload, timeout=5)
        if res.ok:
            print(f"🛡️  Blocked {ip} — reason: {reason}")
            blocked_cache.add(ip)
        else:
            print(f"❌ Error blocking IP {ip}: {res.text}")
    except Exception as e:
        print(f"❌ Exception while blocking IP {ip}:", e)


# -------------------------------------------
# Reputation scoring
# -------------------------------------------
def update_reputation(ip, flagged, ml_score):
    """Simple reputation scoring system"""
    if ip not in reputation:
        reputation[ip] = 0.0

    # Flags increase reputation faster
    if flagged:
        reputation[ip] += 2.0

    # ML score contributes
    reputation[ip] += ml_score * 1.5

    # Decay to avoid permanent scores
    reputation[ip] *= 0.95

    return reputation[ip]


# -------------------------------------------
# Decision Engine
# -------------------------------------------
def should_block(ip, rep_score, flagged, ml_score):
    """
    Very simple decision logic:
    - If ML score > 0.85 => immediate block
    - If event flagged + rep score > 2.5
    - If rep score > 4 overall
    """

    if ml_score > 0.85:
        return True, "High ML anomaly score"

    if flagged and rep_score > 2.5:
        return True, "Flagged + reputation threshold"

    if rep_score > 4:
        return True, "Reputation threshold exceeded"

    return False, ""


# -------------------------------------------
# Main loop
# -------------------------------------------
if __name__ == "__main__":
    print("🧱 Blue Agent 2.0 — AI-Assisted Defense Starting...")

    while True:
        events = get_latest_events()

        for ev in events:
            try:
                ip = ev.get("src_ip") or ev.get("dest_ip")
                if not ip:
                    continue

                flagged = ev.get("flagged", False)

                # ---------------- ML Prediction ----------------
                ml_score = get_anomaly_score(ev)

                # ---------------- Reputation Update ------------
                rep_score = update_reputation(ip, flagged, ml_score)

                # Debug Log
                print(f"[BLUE] IP={ip} | flagged={flagged} | ml={ml_score:.2f} | rep={rep_score:.2f}")

                # ---------------- Decision Engine --------------
                block, reason = should_block(ip, rep_score, flagged, ml_score)

                if block:
                    block_ip(ip, reason)

            except Exception as e:
                print("❌ Error processing event:", e)

        time.sleep(PAUSE)
