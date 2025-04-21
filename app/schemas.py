from pydantic import BaseModel
from typing import List, Optional

class LicensePlateResponse(BaseModel):
    license_plate: str
    confidence: float
    coordinates: Optional[dict] = None
    
class DetectionResponse(BaseModel):
    license_plates: List[LicensePlateResponse]
    processed_image_path: str