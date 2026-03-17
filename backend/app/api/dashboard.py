import json
from typing import Optional, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.schemas import School, Report, WasteRecord
from app.models.api_models import DashboardStats, WasteRecordResponse
from app.services.prediction import get_historical_trend

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_schools = db.query(School).count()
    total_reports = db.query(Report).count()

    avg_waste = (
        db.query(func.avg(WasteRecord.waste_percentage)).scalar() or 0.0
    )
    total_waste = (
        db.query(func.sum(WasteRecord.total_wasted_lbs)).scalar() or 0.0
    )

    # Trend: average waste per date (last 30 entries)
    trend_rows = (
        db.query(
            WasteRecord.date,
            func.avg(WasteRecord.waste_percentage).label("avg_waste"),
        )
        .group_by(WasteRecord.date)
        .order_by(WasteRecord.date.desc())
        .limit(30)
        .all()
    )
    trend = [
        {"date": str(row.date), "waste_percentage": round(float(row.avg_waste), 1)}
        for row in reversed(trend_rows)
    ]

    # School comparison
    school_rows = (
        db.query(
            School.name,
            func.avg(WasteRecord.waste_percentage).label("avg_waste"),
            func.count(WasteRecord.id).label("report_count"),
        )
        .join(WasteRecord, WasteRecord.school_id == School.id)
        .group_by(School.name)
        .all()
    )
    school_comparison = [
        {
            "school": row.name,
            "avg_waste_percentage": round(float(row.avg_waste), 1),
            "report_count": row.report_count,
        }
        for row in school_rows
    ]

    return DashboardStats(
        total_schools=total_schools,
        total_reports=total_reports,
        avg_waste_percentage=round(float(avg_waste), 1),
        total_waste_lbs=round(float(total_waste), 1),
        trend=trend,
        school_comparison=school_comparison,
    )


@router.get("/school/{school_id}/trend")
def get_school_trend(school_id: int, db: Session = Depends(get_db)):
    return get_historical_trend(db, school_id)


@router.get("/waste-records", response_model=List[WasteRecordResponse])
def list_waste_records(
    school_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(WasteRecord)
    if school_id:
        query = query.filter(WasteRecord.school_id == school_id)
    return query.order_by(WasteRecord.date.desc()).limit(limit).all()
