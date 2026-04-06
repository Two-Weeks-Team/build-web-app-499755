import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ai_service import generate_fitness_blueprint, generate_plan_insights
from models import FitnessBrief, SavedBlueprint, SessionLocal, WorkoutBlock


router = APIRouter()


class PlanRequest(BaseModel):
    query: str
    preferences: str


class InsightsRequest(BaseModel):
    selection: str
    context: str


class SaveBlueprintRequest(BaseModel):
    brief_id: int
    name: str
    scenario: Optional[str] = "default"


class ReshapeRequest(BaseModel):
    brief_id: int
    equipment: Optional[str] = None
    injury_notes: Optional[str] = None
    session_minutes: Optional[int] = None
    frequency_per_week: Optional[int] = None
    training_level: Optional[str] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/plan")
@router.post("/plan")
async def plan(request: PlanRequest, db: Session = Depends(get_db)):
    ai_result = await generate_fitness_blueprint(request.query, request.preferences)

    brief_obj = ai_result.get("brief", {})
    title = f"Blueprint {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    frequency = int(brief_obj.get("frequency_per_week", 3) or 3)
    minutes = int(brief_obj.get("session_minutes", 45) or 45)

    brief = FitnessBrief(
        title=title,
        raw_input=request.query,
        primary_goal=str(brief_obj.get("primary_goal", "general fitness")),
        frequency_per_week=frequency,
        session_minutes=minutes,
        equipment=str(brief_obj.get("equipment", "full_gym")),
        injury_notes=str(brief_obj.get("injury_notes", "none")),
        training_level=str(brief_obj.get("training_level", "beginner")),
        style_preference=str(brief_obj.get("style_preference", "balanced")),
        assumptions=str(brief_obj.get("assumptions", "progressive overload")),
        viability_score=int(ai_result.get("score", 75)),
        viability_rationale="; ".join(ai_result.get("rationale", [])) if isinstance(ai_result.get("rationale", []), list) else str(ai_result.get("rationale", "")),
    )
    db.add(brief)
    db.flush()

    items = ai_result.get("items", [])
    persisted_items = []
    for idx, item in enumerate(items):
        exercises = item.get("exercises", [])
        wb = WorkoutBlock(
            brief_id=brief.id,
            day_label=str(item.get("day", f"Day {idx+1}")),
            focus=str(item.get("focus", "Training")),
            duration_minutes=int(item.get("duration_minutes", minutes)),
            intensity_cue=str(item.get("intensity", "moderate")),
            recovery_note=str(item.get("recovery_note", "")),
            exercises_json=json.dumps(exercises),
            sort_order=idx,
        )
        db.add(wb)
        persisted_items.append(
            {
                "day": wb.day_label,
                "focus": wb.focus,
                "duration_minutes": wb.duration_minutes,
                "intensity": wb.intensity_cue,
                "recovery_note": wb.recovery_note,
                "exercises": exercises,
            }
        )

    db.commit()

    return {
        "summary": ai_result.get("summary", "Training blueprint generated."),
        "items": persisted_items,
        "score": int(ai_result.get("score", 75)),
        "brief_id": brief.id,
        "brief": {
            "title": brief.title,
            "primary_goal": brief.primary_goal,
            "frequency_per_week": brief.frequency_per_week,
            "session_minutes": brief.session_minutes,
            "equipment": brief.equipment,
            "injury_notes": brief.injury_notes,
            "training_level": brief.training_level,
            "style_preference": brief.style_preference,
            "assumptions": brief.assumptions,
        },
        "rationale": ai_result.get("rationale", []),
        "clarifying_questions": ai_result.get("clarifying_questions", []),
        "note": ai_result.get("note", ""),
    }


@router.post("/insights")
@router.post("/insights")
async def insights(request: InsightsRequest):
    result = await generate_plan_insights(request.selection, request.context)
    return {
        "insights": result.get("insights", []),
        "next_actions": result.get("next_actions", []),
        "highlights": result.get("highlights", []),
        "note": result.get("note", ""),
    }


@router.get("/blueprints")
@router.get("/blueprints")
def list_blueprints(db: Session = Depends(get_db)):
    rows: List[FitnessBrief] = db.query(FitnessBrief).order_by(FitnessBrief.updated_at.desc()).all()
    out = []
    for row in rows:
        out.append(
            {
                "brief_id": row.id,
                "title": row.title,
                "primary_goal": row.primary_goal,
                "score": row.viability_score,
                "updated_at": row.updated_at.isoformat(),
            }
        )
    return {"items": out}


@router.post("/blueprints/save")
@router.post("/blueprints/save")
def save_blueprint(request: SaveBlueprintRequest, db: Session = Depends(get_db)):
    brief = db.query(FitnessBrief).filter(FitnessBrief.id == request.brief_id).first()
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")

    blocks = db.query(WorkoutBlock).filter(WorkoutBlock.brief_id == brief.id).order_by(WorkoutBlock.sort_order.asc()).all()
    board_snapshot = []
    for b in blocks:
        board_snapshot.append(
            {
                "day": b.day_label,
                "focus": b.focus,
                "duration_minutes": b.duration_minutes,
                "intensity": b.intensity_cue,
                "recovery_note": b.recovery_note,
                "exercises": json.loads(b.exercises_json),
            }
        )

    snapshot_constraints = {
        "equipment": brief.equipment,
        "injury_notes": brief.injury_notes,
        "session_minutes": brief.session_minutes,
        "frequency_per_week": brief.frequency_per_week,
        "training_level": brief.training_level,
    }

    db.query(SavedBlueprint).filter(SavedBlueprint.brief_id == brief.id, SavedBlueprint.is_active_version.is_(True)).update({"is_active_version": False})

    version = SavedBlueprint(
        brief_id=brief.id,
        name=request.name,
        scenario=request.scenario or "default",
        constraints_snapshot_json=json.dumps(snapshot_constraints),
        board_snapshot_json=json.dumps(board_snapshot),
        rationale_snapshot=brief.viability_rationale,
        is_active_version=True,
    )
    db.add(version)
    db.commit()
    db.refresh(version)

    return {
        "saved": True,
        "blueprint_version_id": version.id,
        "brief_id": brief.id,
        "name": version.name,
        "scenario": version.scenario,
        "timestamp": version.created_at.isoformat(),
    }
