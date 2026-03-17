from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List, Dict


# --- Schools ---

class SchoolCreate(BaseModel):
    name: str
    district: Optional[str] = None
    address: Optional[str] = None
    student_count: Optional[int] = None


class SchoolResponse(BaseModel):
    id: int
    name: str
    district: Optional[str]
    address: Optional[str]
    student_count: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Reports ---

class ReportResponse(BaseModel):
    id: int
    school_id: int
    filename: str
    file_type: Optional[str]
    status: str
    extracted_data: Optional[str]
    ai_analysis: Optional[str]
    uploaded_at: datetime
    processed_at: Optional[datetime]

    model_config = {"from_attributes": True}


# --- Menu Items ---

class MenuItemResponse(BaseModel):
    id: int
    report_id: int
    name: str
    category: Optional[str]
    servings_prepared: Optional[int]
    servings_served: Optional[int]
    servings_wasted: Optional[int]
    cost_per_serving: Optional[float]
    date_served: Optional[date]

    model_config = {"from_attributes": True}


# --- Waste Records ---

class WasteRecordResponse(BaseModel):
    id: int
    school_id: int
    report_id: Optional[int]
    date: date
    total_prepared_lbs: Optional[float]
    total_served_lbs: Optional[float]
    total_wasted_lbs: Optional[float]
    waste_percentage: Optional[float]
    predicted_waste_level: Optional[str]
    waste_drivers: Optional[str]
    recommendations: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Analysis ---

class AnalysisResponse(BaseModel):
    report_id: int
    waste_level: str
    waste_percentage: float
    drivers: List[str]
    recommendations: List[str]
    menu_items: List[MenuItemResponse]


class DashboardStats(BaseModel):
    total_schools: int
    total_reports: int
    avg_waste_percentage: float
    total_waste_lbs: float
    trend: List[Dict]
    school_comparison: List[Dict]
