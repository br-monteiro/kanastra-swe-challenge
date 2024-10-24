from fastapi import FastAPI
from src.api.health_check.routes import router as health_check_router


app = FastAPI()


app.include_router(health_check_router)
