from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(tags=["Products"])


class Product(BaseModel):
    id: str
    name: str
    price: float
    category: str


class ProductsResponse(BaseModel):
    data: list[Product]
    total: int


def build_default_products() -> list[Product]:
    return [
        Product(id="prod-001", name="Macbook Pro M5", price=1599.0, category="electronics"),
        Product(id="prod-002", name="Razer Huntsman V3 PRO", price=219.9, category="accessories"),
        Product(id="prod-003", name="Bose Mini Soundlink 2", price=179.9, category="audio"),
        Product(id="prod-004", name="Logitech G PRO X Superlight 2", price=159.9, category="accessories"),
        Product(id="prod-005", name="USB-C Dock", price=129.0, category="peripherals"),
    ]


products: list[Product] = build_default_products()


@router.get("/products")
async def list_products() -> ProductsResponse:
    return ProductsResponse(data=products, total=len(products))


@router.get("/products/{product_id}")
async def get_product(product_id: str) -> Product:
    for product in products:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")
