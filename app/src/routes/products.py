import csv
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator

router = APIRouter(tags=["Products"])

class Product(BaseModel):
    id: str
    name: str
    price: float
    category: str

class ProductCreate(BaseModel):
    name: str
    price: float
    category: str

    @field_validator("name", "category")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("must not be empty")
        return cleaned_value

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("must be greater than 0")
        return value


class ProductsResponse(BaseModel):
    data: list[Product]
    total: int

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "products.csv"
FIELDNAMES = ("id", "name", "price", "category")
WRITE_LOCK = Lock()

def load_products() -> list[Product]:
    with DATA_FILE.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [
            Product(
                id=row["id"],
                name=row["name"],
                price=float(row["price"]),
                category=row["category"],
            )
            for row in reader
        ]

def append_product(product: Product) -> None:
    with WRITE_LOCK:
        with DATA_FILE.open("a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writerow(product.model_dump())

@router.get("/products")
async def list_products() -> ProductsResponse:
    products = load_products()
    return ProductsResponse(data=products, total=len(products))

@router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate) -> Product:
    product = Product(
        id=str(uuid4()),
        name=payload.name,
        price=payload.price,
        category=payload.category,
    )
    append_product(product)
    return product

@router.get("/products/{product_id}")
async def get_product(product_id: str) -> Product:
    products = load_products()
    for product in products:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")