# DevKor 회원관리 시스템
from fastapi.models import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

USER_DB = {}  # 추후 DB 연결 예정 (NAME 을 KEY 로 설정)
USER_NOT_FOUND = HTTPException(
    status_code=400, detail="User not found.")  # FAIL

# Input/Output Schema 정의


class CreateUser(BaseModel):
    id: int
    name: str
    age: int
    role: str

# 전체 조회


@app.get("/users")
def read_users():
    all_users = []
    for user_info in USER_DB.values():
        all_users.append(
            {
                "id": user_info["id"],
                "name": user_info["name"],
                "age": user_info["age"],
                "role": user_info["role"]
            }
        )

# 특정 조회


@app.get("/user")
def read_user(id: int):
    if id not in USER_DB:
        raise USER_NOT_FOUND
    user_info = USER_DB[id]
    return {
        "id": id,
        "name": user_info["name"],
        "age": user_info["age"],
        "role": user_info["role"]
    }

# 특정 수정 (id 는 수정 불가)


@app.put("/user")
def update_user(id: int, name: str, age: int, role: str):
    if id not in USER_DB:
        raise USER_NOT_FOUND
    user_info = USER_DB[id]
    user_info["name"] = name
    user_info["age"] = age
    user_info["role"] = role
    return {"status": "success"}

# 특정 삭제


@app.delete("/user")
def delete_user(id: int):
    if id not in USER_DB:
        raise USER_NOT_FOUND
    del USER_DB[id]
    return {"status": "success"}

# 특정 추가


@app.post("/user", response_model=CreateUser)
def create_user(user: CreateUser) -> CreateUser:
    user_id = len(USER_DB) + 1
    user.id = user_id
    USER_DB[user_id] = user.model_dump()
    return user
