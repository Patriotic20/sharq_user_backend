from fastapi import FastAPI
from src.api import api_router
import uvicorn


app = FastAPI()

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app" , reload=True)    
