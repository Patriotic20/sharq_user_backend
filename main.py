from fastapi import FastAPI
from src.api import api_router
import uvicorn


app = FastAPI(title="Sharq Admissions API",description="API for the Admissions system")
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=False)
