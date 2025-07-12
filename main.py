from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api import api_router
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sharq Admissions API", description="API for the Admissions system")

# Mount the uploads directory to serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
