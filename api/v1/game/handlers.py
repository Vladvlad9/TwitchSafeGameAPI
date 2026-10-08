from fastapi import APIRouter

router = APIRouter(tags=['Game'])


@router.get("/")
async def game():
    pass
