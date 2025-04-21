from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from router import router
from router_image import image_router

app = FastAPI(title="License Plate Detection API")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)
app.include_router(image_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)