from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from typing import List, Dict, Any

class TransportData(BaseModel):
    """Transport-related data for carbon footprint calculation"""
    car_miles_per_week: Optional[float] = Field(default=0.0, description="Miles driven per week")
    public_transit_trips_per_week: Optional[int] = Field(default=0, description="Public transit trips per week")
    flights_per_year: Optional[int] = Field(default=0, description="Number of flights per year")


class ElectricityUsage(BaseModel):
    """Electricity usage data"""
    monthly_kwh: Optional[float] = Field(default=0.0, description="Monthly electricity usage in kWh")
    energy_source: Optional[str] = Field(default="grid", description="Energy source: grid, solar, wind, etc.")


class DietHabits(BaseModel):
    """Diet-related data"""
    meals_per_week: Optional[int] = Field(default=21, description="Number of meals per week")
    meat_percentage: Optional[float] = Field(default=0.0, description="Percentage of meals with meat (0-100)")
    vegetarian_percentage: Optional[float] = Field(default=0.0, description="Percentage of vegetarian meals (0-100)")
    vegan_percentage: Optional[float] = Field(default=0.0, description="Percentage of vegan meals (0-100)")


class AnalyzeRequest(BaseModel):
    """Request model for /analyze endpoint"""
    transport: TransportData = Field(..., description="Transport data")
    electricity: ElectricityUsage = Field(..., description="Electricity usage data")
    diet: DietHabits = Field(..., description="Diet habits data")


class CategoryEmissions(BaseModel):
    """Category-wise carbon emissions breakdown"""
    transport: float = Field(..., description="Transport emissions in kg CO2/year")
    electricity: float = Field(..., description="Electricity emissions in kg CO2/year")
    diet: float = Field(..., description="Diet emissions in kg CO2/year")


class Recommendation(BaseModel):
    """Personalized recommendation"""
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed recommendation description")
    potential_savings: float = Field(..., description="Potential CO2 savings in kg/year")
    category: str = Field(..., description="Category: transport, electricity, or diet")


class AnalyzeResponse(BaseModel):
    """Response model for /analyze and /calculate endpoints"""
    total_carbon_footprint: float = Field(..., description="Total estimated carbon footprint in kg CO2/year")
    category_emissions: CategoryEmissions = Field(..., description="Category-wise emissions breakdown")
    top_recommendations: List[Recommendation] = Field(..., description="Top 3 personalized recommendations")
    explanation: str = Field(..., description="Explanation text about the carbon footprint analysis")
    user_id: Optional[str] = Field(default=None, description="User ID injected at API layer")


class HistoryItem(BaseModel):
    id: str
    user_id: str
    input_data: Dict[str, Any]
    ai_output: Dict[str, Any]
    created_at: datetime
