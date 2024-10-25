from fastapi import FastAPI
from src.api.health_check.routes import router as health_check_router
from src.api.importer_file.routes import router as importer_router
from src.api.metrics.routes import router as metrics_router


app = FastAPI()


app.include_router(health_check_router)
app.include_router(importer_router)
app.include_router(metrics_router)
