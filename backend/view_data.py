# backend/view_data.py

from .database import SessionLocal
from .models import User, Team, Match

def view_data():
    db = SessionLocal()

    print("\n--- USERS ---")
    for user in db.query(User).all():
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")

    print("\n--- TEAMS ---")
    for team in db.query(Team).all():
        print(f"ID: {team.id}, Name: {team.name}, Description: {team.description}")

    print("\n--- MATCHES ---")
    for match in db.query(Match).all():
        print(f"ID: {match.id}, {match.team_a} vs {match.team_b}, Score: {match.score}")

    db.close()


if __name__ == "__main__":
    view_data()
