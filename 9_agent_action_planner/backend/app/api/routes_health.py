from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["Health"])
async def healthcheck():
    return {"status": "healthy"}