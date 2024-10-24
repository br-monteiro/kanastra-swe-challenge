from fastapi.testclient import TestClient
from src.main import app
from src.api.health_check.routes import router as health_check_router

client = TestClient(app)


def test_app_creation():
    assert app.title == "FastAPI"


def test_included_routers():
    for route in health_check_router.routes:
        assert route in app.routes
