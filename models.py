import os
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))

if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

is_sqlite = DATABASE_URL.startswith("sqlite")
is_local_pg = "localhost" in DATABASE_URL or "127.0.0.1" in DATABASE_URL

engine_kwargs = {}
if (not is_sqlite) and (not is_local_pg):
    engine_kwargs["connect_args"] = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, future=True, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class FitnessBrief(Base):
    __tablename__ = "ff_fitness_briefs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    raw_input = Column(Text, nullable=False)
    primary_goal = Column(String(200), nullable=False)
    frequency_per_week = Column(Integer, nullable=False, default=3)
    session_minutes = Column(Integer, nullable=False, default=45)
    equipment = Column(String(200), nullable=False, default="full_gym")
    injury_notes = Column(String(500), nullable=False, default="none")
    training_level = Column(String(50), nullable=False, default="beginner")
    style_preference = Column(String(100), nullable=False, default="balanced")
    assumptions = Column(Text, nullable=False, default="")
    viability_score = Column(Integer, nullable=False, default=70)
    viability_rationale = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    workout_blocks = relationship("WorkoutBlock", back_populates="brief", cascade="all, delete-orphan")
    blueprint_versions = relationship("SavedBlueprint", back_populates="brief", cascade="all, delete-orphan")


class WorkoutBlock(Base):
    __tablename__ = "ff_workout_blocks"

    id = Column(Integer, primary_key=True, index=True)
    brief_id = Column(Integer, ForeignKey("ff_fitness_briefs.id"), nullable=False, index=True)
    day_label = Column(String(30), nullable=False)
    focus = Column(String(120), nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=45)
    intensity_cue = Column(String(50), nullable=False, default="moderate")
    recovery_note = Column(String(250), nullable=False, default="")
    exercises_json = Column(Text, nullable=False, default="[]")
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    brief = relationship("FitnessBrief", back_populates="workout_blocks")


class SavedBlueprint(Base):
    __tablename__ = "ff_saved_blueprints"

    id = Column(Integer, primary_key=True, index=True)
    brief_id = Column(Integer, ForeignKey("ff_fitness_briefs.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    scenario = Column(String(200), nullable=False, default="default")
    constraints_snapshot_json = Column(Text, nullable=False, default="{}")
    board_snapshot_json = Column(Text, nullable=False, default="[]")
    rationale_snapshot = Column(Text, nullable=False, default="")
    is_active_version = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    brief = relationship("FitnessBrief", back_populates="blueprint_versions")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def seed_demo_data() -> None:
    from sqlalchemy.orm import Session
    import json

    db: Session = SessionLocal()
    try:
        existing = db.query(FitnessBrief).count()
        if existing > 0:
            return

        seeds = [
            {
                "title": "Maya Chen - Fat Loss Consistency",
                "raw_input": "Maya Chen - 29 - wants fat loss and consistency with 4 workouts per week and full gym access",
                "primary_goal": "fat loss and consistency",
                "frequency": 4,
                "minutes": 50,
                "equipment": "full_gym",
                "injury": "mild knee sensitivity",
                "level": "intermediate",
                "style": "strength + conditioning",
                "score": 86,
                "rationale": "Strong frequency and equipment fit. Add knee-aware lower body progressions.",
                "blocks": [
                    ("Mon", "Lower Strength", 50, "moderate-high", "Leave 1 day before next lower focus", ["Goblet Squat", "Romanian Deadlift", "Split Squat", "Bike Intervals"]),
                    ("Tue", "Upper Push/Pull", 50, "moderate", "Shoulder mobility cooldown", ["Incline DB Press", "Lat Pulldown", "Seated Row", "Face Pull"]),
                    ("Thu", "Conditioning + Core", 45, "moderate", "Keep impact low", ["Sled Push", "Kettlebell Swing", "Plank Variations", "Farmer Carry"]),
                    ("Sat", "Full Body Hypertrophy", 55, "moderate", "RPE 7-8", ["Leg Press", "DB Bench", "Cable Row", "Hip Thrust"]),
                ],
            },
            {
                "title": "Foundation Reset - 6 Weeks",
                "raw_input": "6-week Foundation Reset - a saved blueprint focused on habit building, full-body training, and recovery",
                "primary_goal": "habit building and general fitness",
                "frequency": 3,
                "minutes": 40,
                "equipment": "home_dumbbells",
                "injury": "none",
                "level": "beginner",
                "style": "full-body",
                "score": 90,
                "rationale": "Excellent recovery spacing and adherence-friendly session length.",
                "blocks": [
                    ("Mon", "Full Body A", 40, "moderate", "Focus on technique", ["DB Squat", "Push-up", "One-arm Row", "Dead Bug"]),
                    ("Wed", "Full Body B", 40, "moderate", "Mobility finisher", ["Reverse Lunge", "DB Overhead Press", "Glute Bridge", "Side Plank"]),
                    ("Fri", "Full Body C", 40, "moderate", "Easy weekend recovery walk", ["DB RDL", "Floor Press", "Band Pull Apart", "Carry"]),
                ],
            },
        ]

        for seed in seeds:
            brief = FitnessBrief(
                title=seed["title"],
                raw_input=seed["raw_input"],
                primary_goal=seed["primary_goal"],
                frequency_per_week=seed["frequency"],
                session_minutes=seed["minutes"],
                equipment=seed["equipment"],
                injury_notes=seed["injury"],
                training_level=seed["level"],
                style_preference=seed["style"],
                assumptions="Progressive overload with recovery-first spacing.",
                viability_score=seed["score"],
                viability_rationale=seed["rationale"],
            )
            db.add(brief)
            db.flush()

            board_snapshot = []
            for idx, (day, focus, mins, intensity, recovery, exercises) in enumerate(seed["blocks"]):
                wb = WorkoutBlock(
                    brief_id=brief.id,
                    day_label=day,
                    focus=focus,
                    duration_minutes=mins,
                    intensity_cue=intensity,
                    recovery_note=recovery,
                    exercises_json=json.dumps(exercises),
                    sort_order=idx,
                )
                db.add(wb)
                board_snapshot.append(
                    {
                        "day": day,
                        "focus": focus,
                        "duration_minutes": mins,
                        "intensity": intensity,
                        "exercises": exercises,
                    }
                )

            bp = SavedBlueprint(
                brief_id=brief.id,
                name=seed["title"],
                scenario="seed_demo",
                constraints_snapshot_json=json.dumps(
                    {
                        "equipment": seed["equipment"],
                        "injury_notes": seed["injury"],
                        "session_minutes": seed["minutes"],
                        "frequency_per_week": seed["frequency"],
                        "training_level": seed["level"],
                    }
                ),
                board_snapshot_json=json.dumps(board_snapshot),
                rationale_snapshot=seed["rationale"],
                is_active_version=True,
            )
            db.add(bp)

        db.commit()
    finally:
        db.close()
