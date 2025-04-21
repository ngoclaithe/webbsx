import os
import shutil
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Query
from fastapi.responses import FileResponse
from service import LicensePlateDetectionService
from schemas import DetectionResponse
from typing import Optional

router = APIRouter(
    prefix="/api/license-plate",
    tags=["license-plate"]
)

license_plate_service = LicensePlateDetectionService()

@router.post("/detect/", response_model=DetectionResponse)
async def detect_license_plate(
    file: UploadFile = File(...),
    confidence: Optional[float] = Query(None, description="Confidence threshold (default 0.8 if not provided)")
):
    """
    Upload an image to detect license plates
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = f"static/uploads/{unique_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        license_plates, result_image_path = license_plate_service.process_image(file_path, confidence)
        
        return DetectionResponse(
            license_plates=license_plates,
            processed_image_path=result_image_path
        )
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@router.get("/")
async def root():
    return {"message": "License Plate Detection API. Go to /docs for API documentation."}