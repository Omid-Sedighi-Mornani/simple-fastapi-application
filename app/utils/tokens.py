import jwt
import os
from datetime import datetime, timedelta, timezone


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_IN_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expires_in = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_IN_MINUTES)
    )

    to_encode.update({"exp": expires_in})

    return jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
