from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
async def healthcheck():
    return {"status": "healthy"}