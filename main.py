import asyncio
import asynctnt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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


class ReadData(BaseModel):
    keys: list


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
users_db = asynctnt.Connection(host="127.0.0.1", port=3349, username="api", password="xxx")
data_db = asynctnt.Connection(host="127.0.0.1", port=3330, username="api", password="xxx")

app = FastAPI()


async def add_user(login: str, password: str):
    space_name = 'users'
    tuple_data = (None, login, pwd_context.hash(password))

    result = await users_db.call("crud.insert", [space_name, tuple_data])
    if result[0]:
        print(result[0]["rows"][0])
    else:
        print(result[1])


@app.on_event("startup")
async def startup():
    await users_db.connect()
    await data_db.connect()
    await add_user("admin", "presale")


@app.on_event("shutdown")
async def shutdown():
    await users_db.disconnect()
    await data_db.disconnect()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user_from_db(login: str) -> UserInDB or None:
    space_name = 'users'

    result = await users_db.call("crud.get", [space_name, [login]])
    print(result)
    if result[0]:
        if result[0]["rows"]:
            print(result[0]["rows"][0])
        else:
            return None
    else:
        return None
    # user_data = await users_db.select("users", [login])
    user_data = {"login": result[0]["rows"][0][1], "password": result[0]["rows"][0][2]}

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


async def write_token_to_db(login: str, token: str):
    space_name = 'tokens'
    tuple_data = (None, login, token)

    result = await users_db.call("crud.insert", [space_name, tuple_data])

    if result[0]:
        print(result[0]["rows"][0])
    else:
        print(result[1])


@app.post("/api/login", response_model=Token)
async def login_to_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires)

    await write_token_to_db(user.login, access_token)

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
async def write_to_db(data: WriteData, current_user: User = Depends(get_current_user)):
    space_name = 'data'

    try:
        operations = [(None, k, v) for k, v in data.to_write.items()]
        await asyncio.gather(
            *[data_db.call("crud.insert", [space_name, operation]) for operation in operations]
        )
        return {"message": "Items inserted successfully", "count": len(operations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/read")
async def read_from_db(data: ReadData, current_user: User = Depends(get_current_user)):
    space_name = 'data'
    try:
        results = await asyncio.gather(
            *[data_db.call("crud.get", [space_name, key]) for key in data.keys]
        )
        items = {row[1]: row[2] for row in results[0]["rows"]}
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

