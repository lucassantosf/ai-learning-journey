from fastapi import APIRouter
import time

router = APIRouter()

start_time = time.time()

@router.get("/health", tags=["Health"])
def health_check():
    uptime = round(time.time() - start_time, 2)
    return {"status": "ok", "uptime_seconds": uptime}