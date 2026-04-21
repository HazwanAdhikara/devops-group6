import csv
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator

router = APIRouter(tags=["Users"])

class UserCreate(BaseModel):
    name: str
    email: str

    @field_validator("name", "email")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("must not be empty")
        return cleaned_value

    @field_validator("email")
    @classmethod
    def must_be_valid_email(cls, value: str) -> str:
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("must be a valid email address")
        local_part, domain_part = value.rsplit("@", 1)
        if not local_part or "." not in domain_part:
            raise ValueError("must be a valid email address")
        return value

class User(BaseModel):
    id: str
    name: str
    email: str

class UsersResponse(BaseModel):
    data: list[User]
    total: int

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "users.csv"
FIELDNAMES = ("id", "name", "email")
WRITE_LOCK = Lock()

def load_users() -> list[User]:
    with DATA_FILE.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [
            User(
                id=row["id"],
                name=row["name"],
                email=row["email"],
            )
            for row in reader
        ]

def append_user(user: User) -> None:
    with WRITE_LOCK:
        with DATA_FILE.open("a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writerow(user.model_dump())

@router.get("/users")
async def list_users() -> UsersResponse:
    users = load_users()
    return UsersResponse(data=users, total=len(users))

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate) -> User:
    users = load_users()
    normalized_email = payload.email.lower()
    if any(existing_user.email.lower() == normalized_email for existing_user in users):
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(id=str(uuid4()), name=payload.name, email=normalized_email)
    append_user(user)
    return user
