from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from contextlib import asynccontextmanager
from deps.db import init_db
from models.user import User
from models.item import Item

# import routes
from api.api import router as main_router
from api.routes.user import router as user_router


# lifespan before and after the run of the application
@asynccontextmanager
async def lifespan(app: FastAPI):
    # before startup
    await init_db()
    yield
    # after shutdown


app = FastAPI(lifespan=lifespan)

app.include_router(main_router)
app.include_router(user_router, prefix="/users", tags=["users"])
