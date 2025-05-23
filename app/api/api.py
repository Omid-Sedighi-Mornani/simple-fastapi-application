from fastapi import APIRouter


router = APIRouter()


@router.get("/")
def home():
    return {"message": "This is a simple FastAPI-Application for testing purposes!"}
