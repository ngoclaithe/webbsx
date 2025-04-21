from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
import os
from typing import Optional

image_router = APIRouter(
    prefix="/images",
    tags=["images"]
)

@image_router.get("/view/{image_path:path}")
async def view_image(image_path: str):
    """
    Hiển thị ảnh từ đường dẫn được cung cấp
    """
    full_path = f"static/{image_path}"
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Ảnh không tồn tại")
    
    return FileResponse(full_path)

@image_router.get("/result/{image_id}")
async def view_result_image(image_id: str):
    """
    Hiển thị ảnh kết quả theo ID
    """
    image_path = f"static/results/{image_id}"
    
    if not os.path.exists(image_path):
        for ext in ['.jpg', '.jpeg', '.png']:
            if os.path.exists(f"{image_path}{ext}"):
                return FileResponse(f"{image_path}{ext}")
        
        raise HTTPException(status_code=404, detail="Ảnh kết quả không tồn tại")
    
    return FileResponse(image_path)

@image_router.get("/preview/{image_id}", response_class=HTMLResponse)
async def preview_image(image_id: str):
    """
    Tạo trang HTML để xem trước ảnh kết quả với biển số đã nhận dạng
    """
    image_path = None
    for ext in ['.jpg', '.jpeg', '.png']:
        if os.path.exists(f"static/results/{image_id}{ext}"):
            image_path = f"/images/view/results/{image_id}{ext}"
            break
            
    if not image_path:
        raise HTTPException(status_code=404, detail="Ảnh kết quả không tồn tại")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kết quả nhận dạng biển số xe</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                text-align: center;
            }}
            h1 {{
                color: #333;
            }}
            .result-container {{
                margin: 20px auto;
                max-width: 800px;
                border: 1px solid #ddd;
                padding: 15px;
                border-radius: 5px;
            }}
            img {{
                max-width: 100%;
                height: auto;
                border: 1px solid #eee;
                margin-top: 15px;
            }}
        </style>
    </head>
    <body>
        <h1>Kết quả nhận dạng biển số xe</h1>
        <div class="result-container">
            <h3>Ảnh đã xử lý:</h3>
            <img src="{image_path}" alt="Kết quả nhận dạng biển số xe">
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)