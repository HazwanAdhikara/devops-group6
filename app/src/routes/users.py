from uuid import uuid4

from fastapi import APIRouter, status
from pydantic import BaseModel


router = APIRouter(tags=["Users"])


class UserCreate(BaseModel):
    name: str
    email: str


class User(BaseModel):
    id: str
    name: str
    email: str


class UsersResponse(BaseModel):
    data: list[User]
    total: int


def build_default_users() -> list[User]:
    default_users = (
        ("Alice Johnson", "alice@example.com"),
        ("Brandon Lee", "brandon@example.com"),
        ("Carla Mendes", "carla@example.com"),
        ("Dimas Pratama", "dimas@example.com"),
        ("Eka Sari", "eka@example.com"),
        ("Fajar Nugroho", "fajar@example.com"),
        ("Gita Putri", "gita@example.com"),
        ("Hendra Saputra", "hendra@example.com"),
        ("Intan Permata", "intan@example.com"),
        ("Joko Santoso", "joko@example.com"),
    )
    return [User(id=str(uuid4()), name=name, email=email) for name, email in default_users]


users: list[User] = build_default_users()


@router.get("/users")
async def list_users() -> UsersResponse:
    return UsersResponse(data=users, total=len(users))


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate) -> User:
    user = User(id=str(uuid4()), name=payload.name, email=payload.email)
    users.append(user)
    return user
