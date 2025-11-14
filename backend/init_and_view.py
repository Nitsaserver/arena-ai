import argparse
from rich.console import Console
from rich.table import Table
from .database import engine, SessionLocal, Base
from .models import User, Team, Match

console = Console()

def init_db(reset=False):
    if reset:
        console.print("[red]Dropping all tables...[/red]")
        Base.metadata.drop_all(bind=engine)
        console.print("[red]Tables dropped.[/red]\n")

    console.print("[green]Creating tables...[/green]")
    Base.metadata.create_all(bind=engine)
    console.print("[green]Tables created.[/green]\n")


def seed_data():
    db = SessionLocal()
    if db.query(User).first():
        console.print("[yellow]Database already has data — skipping seeding.[/yellow]\n")
        db.close()
        return

    console.print("[cyan]Seeding initial data...[/cyan]")

    users = [
        User(username="nitsa", email="nitsa@example.com"),
        User(username="arnav", email="arnav@example.com"),
        User(username="priya", email="priya@example.com"),
    ]

    teams = [
        Team(name="Red Hawks", description="Offensive cyber team"),
        Team(name="Blue Shields", description="Defensive security team"),
    ]

    matches = [
        Match(team_a="Red Hawks", team_b="Blue Shields", score="3-2"),
        Match(team_a="Blue Shields", team_b="Red Hawks", score="4-1"),
    ]

    db.add_all(users + teams + matches)
    db.commit()
    db.close()
    console.print("[cyan]Seeding complete![/cyan]\n")


def view_data():
    db = SessionLocal()

    # --- USERS ---
    users = db.query(User).all()
    if users:
        table = Table(title="USERS", header_style="bold green")
        table.add_column("ID", justify="right")
        table.add_column("Username", justify="left")
        table.add_column("Email", justify="left")
        for u in users:
            table.add_row(str(u.id), u.username, u.email)
        console.print(table)

    # --- TEAMS ---
    teams = db.query(Team).all()
    if teams:
        table = Table(title="TEAMS", header_style="bold blue")
        table.add_column("ID", justify="right")
        table.add_column("Name", justify="left")
        table.add_column("Description", justify="left")
        for t in teams:
            table.add_row(str(t.id), t.name, t.description)
        console.print(table)

    # --- MATCHES ---
    matches = db.query(Match).all()
    if matches:
        table = Table(title="MATCHES", header_style="bold magenta")
        table.add_column("ID", justify="right")
        table.add_column("Team A", justify="left")
        table.add_column("Team B", justify="left")
        table.add_column("Score", justify="center")
        for m in matches:
            table.add_row(str(m.id), m.team_a, m.team_b, m.score)
        console.print(table)

    db.close()
    console.print("\n[bold green]All data displayed successfully.[/bold green]\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize, seed, and view the arena database.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop all tables before creating new ones and seeding fresh data."
    )
    args = parser.parse_args()

    init_db(reset=args.reset)
    seed_data()
    view_data()


