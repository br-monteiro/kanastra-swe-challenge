from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api.metrics.routes import router


app = FastAPI()
app.include_router(router)

client = TestClient(app)


@patch('src.api.metrics.routes.generate_latest')
def test_metrics(generate_latest):
    generate_latest.return_value = b'my_custom_metric 1.0\n'
    response = client.get('/metrics')

    assert response.status_code == 200
    assert response.text == 'my_custom_metric 1.0\n'
    assert response.headers['content-type'] == 'text/plain; version=0.0.4; charset=utf-8'
