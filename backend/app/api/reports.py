import json
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.schemas import Report, ReportStatus, MenuItem, WasteRecord, School
from app.models.api_models import ReportResponse, AnalysisResponse, MenuItemResponse
from app.services.parser import parse_file
from app.services.ai_service import classify_document, extract_structured_data, analyze_waste
from app.services.prediction import (
    predict_waste_level,
    identify_waste_drivers,
    generate_recommendations,
    calculate_waste_stats,
)

router = APIRouter(prefix="/reports", tags=["reports"])

ALLOWED_EXTENSIONS = {"pdf", "csv", "xlsx", "xls", "png", "jpg", "jpeg"}


@router.post("/upload", response_model=AnalysisResponse)
async def upload_and_analyze(
    file: UploadFile = File(...),
    school_id: int = Form(...),
    db: Session = Depends(get_db),
):
    # Validate school exists
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    # Validate file type
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not supported. Use: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Save file
    file_path = settings.upload_path / f"{datetime.utcnow().timestamp()}_{file.filename}"
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Create report record
    report = Report(
        school_id=school_id,
        filename=file.filename,
        file_type=ext,
        file_path=str(file_path),
        status=ReportStatus.PROCESSING,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    try:
        # Step 1: Parse document
        raw_text = parse_file(str(file_path), ext)
        report.raw_text = raw_text

        # Step 2: Extract structured data via Claude
        structured_data = extract_structured_data(raw_text)
        report.extracted_data = json.dumps(structured_data)

        # Step 3: Analyze waste via Claude
        ai_analysis = analyze_waste(structured_data)
        report.ai_analysis = json.dumps(ai_analysis)

        # Step 4: Save menu items
        menu_items_data = structured_data.get("menu_items", [])
        db_menu_items = []
        for item in menu_items_data:
            mi = MenuItem(
                report_id=report.id,
                name=item["name"],
                category=item.get("category"),
                servings_prepared=item.get("servings_prepared"),
                servings_served=item.get("servings_served"),
                servings_wasted=item.get("servings_wasted"),
                cost_per_serving=item.get("cost_per_serving"),
                date_served=_parse_date(item.get("date_served")),
            )
            db.add(mi)
            db_menu_items.append(mi)

        # Step 5: Calculate stats and predict
        stats = calculate_waste_stats(menu_items_data)
        waste_level = predict_waste_level(stats["waste_percentage"])
        drivers = identify_waste_drivers(menu_items_data)
        recommendations = generate_recommendations(waste_level, drivers, menu_items_data)

        # Merge AI recommendations with rule-based ones
        ai_recs = ai_analysis.get("recommendations", [])
        all_recs = recommendations + [
            r["action"] if isinstance(r, dict) else r for r in ai_recs
        ]
        # Deduplicate
        seen = set()
        unique_recs = []
        for r in all_recs:
            if r not in seen:
                seen.add(r)
                unique_recs.append(r)

        # Step 6: Save waste record
        totals = structured_data.get("totals", {})
        report_date = _parse_date(structured_data.get("report_date")) or date.today()

        waste_record = WasteRecord(
            school_id=school_id,
            report_id=report.id,
            date=report_date,
            total_prepared_lbs=totals.get("total_prepared_lbs"),
            total_served_lbs=totals.get("total_served_lbs"),
            total_wasted_lbs=totals.get("total_wasted_lbs"),
            waste_percentage=stats["waste_percentage"],
            predicted_waste_level=waste_level,
            waste_drivers=json.dumps(drivers),
            recommendations=json.dumps(unique_recs),
        )
        db.add(waste_record)

        report.status = ReportStatus.COMPLETED
        report.processed_at = datetime.utcnow()
        db.commit()

        # Refresh menu items to get IDs
        for mi in db_menu_items:
            db.refresh(mi)

        return AnalysisResponse(
            report_id=report.id,
            waste_level=waste_level.value,
            waste_percentage=stats["waste_percentage"],
            drivers=drivers + [
                d["driver"] if isinstance(d, dict) else d
                for d in ai_analysis.get("waste_drivers", [])
            ],
            recommendations=unique_recs,
            menu_items=[
                MenuItemResponse.model_validate(mi) for mi in db_menu_items
            ],
        )

    except Exception as e:
        report.status = ReportStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/", response_model=list[ReportResponse])
def list_reports(school_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Report)
    if school_id:
        query = query.filter(Report.school_id == school_id)
    return query.order_by(Report.uploaded_at.desc()).all()


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


def _parse_date(date_str: str | None) -> date | None:
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None
