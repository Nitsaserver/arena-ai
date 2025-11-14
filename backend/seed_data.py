# backend/seed_data.py

from .database import SessionLocal
from .models import User, Team, Match


def seed_data():
    db = SessionLocal()

    # ✅ Check if already seeded
    if db.query(User).first():
        print("Database already has data — skipping seeding.")
        db.close()
        return

    print("Seeding initial data...")

    # --- Users ---
    users = [
        User(username="nitsa", email="nitsa@example.com"),
        User(username="arnav", email="arnav@example.com"),
        User(username="priya", email="priya@example.com"),
    ]

    # --- Teams ---
    teams = [
        Team(name="Red Hawks", description="Offensive cyber team"),
        Team(name="Blue Shields", description="Defensive security team"),
    ]

    # --- Matches ---
    matches = [
        Match(team_a="Red Hawks", team_b="Blue Shields", score="3-2"),
        Match(team_a="Blue Shields", team_b="Red Hawks", score="4-1"),
    ]

    # ✅ Add all to DB
    db.add_all(users + teams + matches)
    db.commit()
    db.close()
    print("Seeding complete!")

