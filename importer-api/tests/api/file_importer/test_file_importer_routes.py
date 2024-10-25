from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.api.file_importer.routes import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)


@patch("boto3.client")
def test_upload_file(boto3_client):
    boto3_client.return_value.send_message_batch = MagicMock()
    messages = ["line1", "line2", "line3"]
    entries = [
        {"Id": str(i), "MessageBody": message} for i, message in enumerate(messages)
    ]

    response = client.post(
        "/v1/upload", files={"file": ("test.csv", b"line1\nline2\nline3")})
    assert response.status_code == 200
    assert response.json() == {
        "message": "File received. Processing in background."}

    boto3_client.return_value.send_message_batch.assert_called_with(
        QueueUrl="",
        Entries=entries
    )
