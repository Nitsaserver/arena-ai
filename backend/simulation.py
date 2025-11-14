import random
import time
from .models import ArenaRound
from .database import SessionLocal

# Simple simulation logic (we’ll replace with AI later)
RED_ACTIONS = ["Phishing Attack", "SQL Injection", "DDoS", "Brute Force"]
BLUE_ACTIONS = ["Firewall Block", "Input Sanitization", "Rate Limit", "Patch Deployment"]

def simulate_round(round_number: int):
    db = SessionLocal()
    red_action = random.choice(RED_ACTIONS)
    blue_action = random.choice(BLUE_ACTIONS)

    # Simple win logic
    outcome = random.choice(["Red Wins", "Blue Wins"])
    score_red = 1 if outcome == "Red Wins" else 0
    score_blue = 1 if outcome == "Blue Wins" else 0

    reasoning = f"Red tried {red_action}. Blue responded with {blue_action}. Outcome: {outcome}."

    round_entry = ArenaRound(
        round_number=round_number,
        attacker_action=red_action,
        defender_action=blue_action,
        outcome=outcome,
        score_red=score_red,
        score_blue=score_blue,
        reasoning_log=reasoning,
    )

    db.add(round_entry)
    db.commit()
    db.refresh(round_entry)
    db.close()

    return round_entry
