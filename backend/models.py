from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
import time
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

# ----------------------------
# USERS TABLE
# ----------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)


# ----------------------------
# TEAMS TABLE
# ----------------------------
class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)


# ----------------------------
# MATCHES TABLE
# ----------------------------
class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    team_a = Column(String(50), nullable=False)
    team_b = Column(String(50), nullable=False)
    score = Column(String(20), nullable=True)


# ----------------------------
# EVENTS TABLE
# ----------------------------
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    src_ip = Column(String(45), nullable=True)       # IPv4/IPv6 safe
    dest_ip = Column(String(45), nullable=True)
    action = Column(String(100), nullable=False)
    ts = Column(Float, default=lambda: time.time())
    flagged = Column(Boolean, default=False)
    details = Column(String(255), nullable=True)


# ----------------------------
# BLOCKS TABLE
# ----------------------------
class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(45), unique=True, nullable=False)  # consistent with src_ip
    reason = Column(String(255), nullable=True)
    blocked_at = Column(Float, default=lambda: time.time())
    expires_at = Column(Float, nullable=True)


# ----------------------------
# ARENA ROUNDS TABLE
# ----------------------------
class ArenaRound(Base):
    __tablename__ = "arena_rounds"

    id = Column(Integer, primary_key=True)
    round_number = Column(Integer, nullable=False)
    attacker_action = Column(String(255), nullable=True)
    defender_action = Column(String(255), nullable=True)
    outcome = Column(String(50), nullable=True)
    score_red = Column(Integer, default=0)
    score_blue = Column(Integer, default=0)
    reasoning_log = Column(Text, nullable=True)  # AI thoughts / reasoning trace
    timestamp = Column(DateTime, default=datetime.utcnow)


class TrainingData(Base):
    __tablename__ = "training_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    round_id = Column(Integer, nullable=True)            # optional FK to arena_rounds.id
    attacker_action = Column(String(255), nullable=True)
    defender_action = Column(String(255), nullable=True)
    outcome = Column(String(50), nullable=True)
    reward = Column(Float, nullable=True)
    meta_data = Column(Text, nullable=True)               # store JSON string if needed
    timestamp = Column(DateTime, server_default=func.now())

class TrainingRun(Base):
    __tablename__ = "training_runs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    n_samples = Column(Integer, nullable=False)
    contamination = Column(Float, nullable=True)
    model_path = Column(String(255), nullable=True)
    notes = Column(String(512), nullable=True)