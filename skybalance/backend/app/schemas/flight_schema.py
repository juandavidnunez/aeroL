from pydantic import BaseModel, Field
from typing import Optional

class FlightCreate(BaseModel):
    code: str
    origin: str
    destination: str
    base_price: float = Field(gt=0)
    passengers: int = Field(ge=0)
    promotion: float = 0.0
    priority: int = Field(default=1, ge=1, le=5)

class FlightUpdate(BaseModel):
    code: Optional[str] = None  
    origin: Optional[str] = None
    destination: Optional[str] = None
    base_price: Optional[float] = None
    passengers: Optional[int] = None
    promotion: Optional[float] = None
    priority: Optional[int] = None

class FlightResponse(BaseModel):
    code: str
    origin: str
    destination: str
    base_price: float
    final_price: float
    passengers: int
    promotion: float
    penalty: float
    is_critical: bool
    priority: int
    alerts: list
    height: int
    balance_factor: int