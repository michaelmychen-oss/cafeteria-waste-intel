"""
Prediction engine: starts with rule-based heuristics, upgradable to ML models.
"""

import json
import numpy as np
from sqlalchemy.orm import Session

from app.models.schemas import WasteRecord, WasteLevel


def predict_waste_level(waste_percentage: float) -> WasteLevel:
    """Rule-based waste level classification."""
    if waste_percentage < 10:
        return WasteLevel.LOW
    elif waste_percentage < 20:
        return WasteLevel.MEDIUM
    elif waste_percentage < 35:
        return WasteLevel.HIGH
    else:
        return WasteLevel.CRITICAL


def identify_waste_drivers(menu_items: list) -> list:
    """Identify likely drivers of waste from menu item data."""
    drivers = []

    for item in menu_items:
        prepared = item.get("servings_prepared") or 0
        served = item.get("servings_served") or 0
        wasted = item.get("servings_wasted") or 0

        if prepared == 0:
            continue

        item_waste_pct = (wasted / prepared) * 100 if prepared > 0 else 0

        if item_waste_pct > 40:
            drivers.append(
                f"High waste item: {item['name']} ({item_waste_pct:.0f}% wasted) — "
                f"consider reducing portions or replacing"
            )

        if prepared > 0 and served / prepared < 0.5:
            drivers.append(
                f"Low uptake: {item['name']} — only {served}/{prepared} servings taken"
            )

    # Check for overproduction pattern
    total_prepared = sum(i.get("servings_prepared") or 0 for i in menu_items)
    total_served = sum(i.get("servings_served") or 0 for i in menu_items)
    if total_prepared > 0 and total_served / total_prepared < 0.7:
        drivers.append(
            f"Systematic overproduction: only {total_served}/{total_prepared} "
            f"total servings consumed ({total_served/total_prepared*100:.0f}%)"
        )

    return drivers


def generate_recommendations(
    waste_level: WasteLevel, drivers: list, menu_items: list
) -> list:
    """Generate actionable recommendations based on waste analysis."""
    recs = []

    if waste_level in (WasteLevel.HIGH, WasteLevel.CRITICAL):
        recs.append(
            "URGENT: Conduct an immediate review of production quantities. "
            "Reduce batch sizes by 15-25% for the next service period."
        )

    # Item-specific recommendations
    for item in menu_items:
        prepared = item.get("servings_prepared") or 0
        wasted = item.get("servings_wasted") or 0
        if prepared > 0 and wasted / prepared > 0.3:
            recs.append(
                f"Reduce production of '{item['name']}' by "
                f"{int((wasted / prepared) * 50)}% next cycle."
            )

    if waste_level == WasteLevel.MEDIUM:
        recs.append(
            "Implement an offer-vs-serve model to give students more choice "
            "and reduce tray waste."
        )

    if waste_level != WasteLevel.LOW:
        recs.append(
            "Start a student taste-testing program for new menu items "
            "before full rollout."
        )
        recs.append(
            "Track waste daily for 2 weeks to identify day-of-week patterns."
        )

    if not recs:
        recs.append(
            "Waste levels are within acceptable range. Continue current practices "
            "and monitor weekly."
        )

    return recs


def calculate_waste_stats(menu_items: list) -> dict:
    """Calculate aggregate waste statistics from menu item data."""
    total_prepared = sum(i.get("servings_prepared") or 0 for i in menu_items)
    total_served = sum(i.get("servings_served") or 0 for i in menu_items)
    total_wasted = sum(i.get("servings_wasted") or 0 for i in menu_items)

    waste_pct = (total_wasted / total_prepared * 100) if total_prepared > 0 else 0

    return {
        "total_prepared": total_prepared,
        "total_served": total_served,
        "total_wasted": total_wasted,
        "waste_percentage": round(waste_pct, 1),
    }


def get_historical_trend(db: Session, school_id: int, limit: int = 30) -> list:
    """Pull recent waste records for trend analysis."""
    records = (
        db.query(WasteRecord)
        .filter(WasteRecord.school_id == school_id)
        .order_by(WasteRecord.date.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "date": str(r.date),
            "waste_percentage": r.waste_percentage,
            "waste_level": r.predicted_waste_level.value if r.predicted_waste_level else None,
            "total_wasted_lbs": r.total_wasted_lbs,
        }
        for r in reversed(records)
    ]
