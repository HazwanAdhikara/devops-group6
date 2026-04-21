from uuid import uuid4

from fastapi import APIRouter, status
from pydantic import BaseModel


router = APIRouter()


class UserCreate(BaseModel):
    name: str
    email: str


class User(BaseModel):
    id: str
    name: str
    email: str


users: list[User] = [
    User(id=str(uuid4()), name="Alice Johnson", email="alice@example.com"),
    User(id=str(uuid4()), name="Brandon Lee", email="brandon@example.com"),
    User(id=str(uuid4()), name="Carla Mendes", email="carla@example.com"),
    User(id=str(uuid4()), name="Dimas Pratama", email="dimas@example.com"),
    User(id=str(uuid4()), name="Eka Sari", email="eka@example.com"),
    User(id=str(uuid4()), name="Fajar Nugroho", email="fajar@example.com"),
    User(id=str(uuid4()), name="Gita Putri", email="gita@example.com"),
    User(id=str(uuid4()), name="Hendra Saputra", email="hendra@example.com"),
    User(id=str(uuid4()), name="Intan Permata", email="intan@example.com"),
    User(id=str(uuid4()), name="Joko Santoso", email="joko@example.com"),
]


@router.get("/users")
async def list_users() -> dict[str, object]:
    return {"data": users, "total": len(users)}


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate) -> User:
    user = User(id=str(uuid4()), name=payload.name, email=payload.email)
    users.append(user)
    return user
