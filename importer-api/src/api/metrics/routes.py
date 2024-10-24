from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


router = APIRouter()


@router.get("/metrics")
async def get_metrics():
    data = generate_latest()
    return Response(data, media_type=CONTENT_TYPE_LATEST)
