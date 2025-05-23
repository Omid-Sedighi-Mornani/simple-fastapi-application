from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

# import routes
from api.api import router as main_router
from api.routes.user import router as user_router

app = FastAPI()
app.include_router(main_router)
app.include_router(user_router, prefix="/users", tags=["users"])
