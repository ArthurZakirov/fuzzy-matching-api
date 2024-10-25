from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI()

# Include routes from the routes file
app.include_router(api_router)
