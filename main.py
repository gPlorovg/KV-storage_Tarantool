import asyncio
import asynctnt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# db = asynctnt.Connection(host="127.0.0.1", port=3301, username="api", password="api")
db = dict()
# db = {
#     "tim": {
#         "username": "tim",
#         "full_name": "Tim Ruscica",
#         "email": "tim@gmail.com",
#         "hashed_password": "$2b$12$HxWHkvMuL7WrZad6lcCfluNFj1/Zp63lvP5aUrKlSTYtoFzPXHOtu",
#         "disabled": False
#     }
# }


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    login: str or None = None


class User(BaseModel):
    login: str


class UserInDB(User):
    hashed_password: str


class WriteData(BaseModel):
    to_write: dict


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def add_user(login: str, password: str):
    db.update({login: {"login": login, "password": pwd_context.hash(password)}})


add_user("admin", "presale")

# @app.on_event("startup")
# async def startup():
#     await db.connect()
#
#
# @app.on_event("shutdown")
# async def shutdown():
#     await db.disconnect()

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)
#
#
# def get_password_hash(password):
#     return pwd_context.hash(password)
#
#
# def get_user(db, username: str):
#     if username in db:
#         user_data = db[username]
#         return UserInDB(**user_data)
#
#
# def authenticate_user(db, username: str, password: str):
#     user = get_user(db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#
#     return user
#
#
# def create_access_token(data: dict, expires_delta: timedelta or None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt
#
#
# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                          detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credential_exception
#
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credential_exception
#
#     user = get_user(db, username=token_data.username)
#     if user is None:
#         raise credential_exception
#
#     return user


# async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#
#     return current_user


# @app.post("/token", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires)
#     return {"access_token": access_token, "token_type": "bearer"}
#
#
# @app.get("/users/me/", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user
#
#
# @app.get("/users/me/items")
# async def read_own_items(current_user: User = Depends(get_current_user)):
#     return [{"item_id": 1, "owner": current_user}]

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user_from_db(login: str) -> UserInDB or None:
    # user_data = await db.select("users", [login])
    user_data = db.get(login, None)

    if user_data:
        return UserInDB(login=user_data["login"], hashed_password=user_data["password"])

    return None


async def authenticate_user(login: str, password: str) -> User or None:
    user_in_db = await get_user_from_db(login)

    if user_in_db and verify_password(password, user_in_db.hashed_password):
        return User(login=user_in_db.login)

    return None


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


@app.post("/api/login", response_model=Token)
async def login_to_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: Token) -> User:
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials",
                                         headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token.access_token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credential_exception

        token_data = TokenData(login=login)
    except JWTError:
        raise credential_exception

    user_in_db = await get_user_from_db(token_data.login)
    if user_in_db is None:
        raise credential_exception

    return User(login=user_in_db.login)


@app.post("/api/write")
def write_to_db(data: WriteData, current_user: User = Depends(get_current_user)):
    return {"status_code": 200}


@app.post("/api/read")
def read_from_db():
    pass
