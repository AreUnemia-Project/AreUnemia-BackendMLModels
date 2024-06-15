from datetime import datetime, timedelta
from typing import Union
import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY")

def decode_jwt(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token if decoded_token["exp"] >= datetime.utcnow().timestamp() else None
    except jwt.PyJWTError:
        return None