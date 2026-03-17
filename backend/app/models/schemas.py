from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, Date, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class WasteLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReportStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    district = Column(String(255))
    address = Column(String(500))
    student_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    reports = relationship("Report", back_populates="school")
    waste_records = relationship("WasteRecord", back_populates="school")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_path = Column(String(1000))
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.UPLOADED)
    raw_text = Column(Text)
    extracted_data = Column(Text)  # JSON string of structured data
    ai_analysis = Column(Text)  # JSON string of Claude's analysis
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))

    school = relationship("School", back_populates="reports")
    menu_items = relationship("MenuItem", back_populates="report")
    waste_records = relationship("WasteRecord", back_populates="report")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100))  # entree, side, beverage, dessert
    servings_prepared = Column(Integer)
    servings_served = Column(Integer)
    servings_wasted = Column(Integer)
    cost_per_serving = Column(Float)
    date_served = Column(Date)

    report = relationship("Report", back_populates="menu_items")


class WasteRecord(Base):
    __tablename__ = "waste_records"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("reports.id"))
    date = Column(Date, nullable=False)
    total_prepared_lbs = Column(Float)
    total_served_lbs = Column(Float)
    total_wasted_lbs = Column(Float)
    waste_percentage = Column(Float)
    predicted_waste_level = Column(SQLEnum(WasteLevel))
    waste_drivers = Column(Text)  # JSON list of identified drivers
    recommendations = Column(Text)  # JSON list of recommendations
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    school = relationship("School", back_populates="waste_records")
    report = relationship("Report", back_populates="waste_records")
