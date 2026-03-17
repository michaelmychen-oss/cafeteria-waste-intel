"""
Seed script: creates sample schools and demo data for development.
Run: python seed_data.py
"""

import json
from datetime import date, timedelta
import random

from app.core.database import SessionLocal, engine, Base
from app.models.schemas import School, Report, MenuItem, WasteRecord, ReportStatus, WasteLevel

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Clear existing data
for table in [WasteRecord, MenuItem, Report, School]:
    db.query(table).delete()
db.commit()

# Create schools
schools = [
    School(name="Lincoln Elementary", district="Metro Unified", address="100 Main St", student_count=450),
    School(name="Washington Middle School", district="Metro Unified", address="200 Oak Ave", student_count=620),
    School(name="Jefferson High School", district="Metro Unified", address="300 Elm Blvd", student_count=980),
    School(name="Roosevelt Elementary", district="Metro Unified", address="400 Pine Dr", student_count=380),
]
db.add_all(schools)
db.commit()
for s in schools:
    db.refresh(s)

# Generate 30 days of waste records per school
menu_options = [
    ("Chicken Tenders", "entree"), ("Pizza Slice", "entree"), ("Hamburger", "entree"),
    ("Grilled Cheese", "entree"), ("Pasta & Sauce", "entree"),
    ("Green Beans", "vegetable"), ("Corn", "vegetable"), ("Salad", "vegetable"),
    ("Apple Slices", "fruit"), ("Orange", "fruit"), ("Banana", "fruit"),
    ("Milk (1%)", "dairy"), ("Chocolate Milk", "dairy"),
    ("Roll", "grain"), ("Rice", "grain"),
    ("Cookie", "dessert"),
]

for school in schools:
    base_waste_pct = random.uniform(8, 30)  # Each school has a baseline

    for day_offset in range(30):
        record_date = date.today() - timedelta(days=30 - day_offset)

        # Create a report
        report = Report(
            school_id=school.id,
            filename=f"daily_report_{record_date}.csv",
            file_type="csv",
            status=ReportStatus.COMPLETED,
            uploaded_at=record_date,
            processed_at=record_date,
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        # Pick 6-8 random menu items for the day
        day_items = random.sample(menu_options, random.randint(6, 8))
        total_prepared = 0
        total_served = 0
        total_wasted = 0

        for name, category in day_items:
            prepared = random.randint(
                int(school.student_count * 0.3), int(school.student_count * 0.6)
            )
            waste_factor = base_waste_pct / 100 + random.uniform(-0.1, 0.1)
            waste_factor = max(0.02, min(waste_factor, 0.5))
            wasted = int(prepared * waste_factor)
            served = prepared - wasted

            mi = MenuItem(
                report_id=report.id,
                name=name,
                category=category,
                servings_prepared=prepared,
                servings_served=served,
                servings_wasted=wasted,
                cost_per_serving=round(random.uniform(0.5, 3.0), 2),
                date_served=record_date,
            )
            db.add(mi)
            total_prepared += prepared
            total_served += served
            total_wasted += wasted

        waste_pct = (total_wasted / total_prepared * 100) if total_prepared > 0 else 0

        if waste_pct < 10:
            level = WasteLevel.LOW
        elif waste_pct < 20:
            level = WasteLevel.MEDIUM
        elif waste_pct < 35:
            level = WasteLevel.HIGH
        else:
            level = WasteLevel.CRITICAL

        wr = WasteRecord(
            school_id=school.id,
            report_id=report.id,
            date=record_date,
            total_prepared_lbs=round(total_prepared * 0.35, 1),  # approx lbs
            total_served_lbs=round(total_served * 0.35, 1),
            total_wasted_lbs=round(total_wasted * 0.35, 1),
            waste_percentage=round(waste_pct, 1),
            predicted_waste_level=level,
            waste_drivers=json.dumps(["overproduction", "unpopular items"]),
            recommendations=json.dumps(["Reduce batch sizes", "Survey students"]),
        )
        db.add(wr)

    db.commit()

print(f"Seeded {len(schools)} schools with 30 days of data each.")
db.close()
