from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.ml_predict import predict_risk

router = APIRouter()


class RiskInput(BaseModel):
    rainfall_mm: float = Field(..., ge=0, description="Recent rainfall in mm")
    slope_angle: float = Field(..., ge=0, le=90, description="Slope angle in degrees")
    soil_moisture_pct: float = Field(..., ge=0, le=100, description="Soil saturation %")
    elevation_m: float = Field(..., ge=0, description="Elevation in meters")
    distance_to_fault_km: float = Field(..., ge=0, description="Distance to nearest fault line, km")
    prev_landslide_count: int = Field(..., ge=0, description="Past landslide events nearby")
    vegetation_cover_pct: float = Field(..., ge=0, le=100, description="Vegetation cover %")


class RiskOutput(BaseModel):
    risk_probability: float
    risk_level: str


@router.post("/predict", response_model=RiskOutput)
def predict(input: RiskInput):
    """Takes a single set of terrain/sensor readings and returns a landslide risk score."""
    prob, level = predict_risk(
        rainfall_mm=input.rainfall_mm,
        slope_angle=input.slope_angle,
        soil_moisture_pct=input.soil_moisture_pct,
        elevation_m=input.elevation_m,
        distance_to_fault_km=input.distance_to_fault_km,
        prev_landslide_count=input.prev_landslide_count,
        vegetation_cover_pct=input.vegetation_cover_pct,
    )
    return RiskOutput(risk_probability=prob, risk_level=level)
