from fastapi import UploadFile, BackgroundTasks, APIRouter
from src.api.importer_file.tasks import process_file_task


router = APIRouter()


@router.post('/v1/upload')
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    file_content = await file.read()
    background_tasks.add_task(process_file_task, file_content)
    return {"message": "File received. Processing in background."}
