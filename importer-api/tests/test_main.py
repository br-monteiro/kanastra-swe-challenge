from fastapi.testclient import TestClient
from src.main import app
from src.api.file_importer.routes import router as file_importer_router
from src.api.health_check.routes import router as health_check_router
from src.api.metrics.routes import router as metrics_router

client = TestClient(app)


def test_app_creation():
    assert app.title == "FastAPI"


def test_included_routers():
    for route in health_check_router.routes:
        assert route in app.routes

    for route in metrics_router.routes:
        assert route in app.routes

    for route in file_importer_router.routes:
        assert route in app.routes
