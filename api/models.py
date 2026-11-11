from decimal import Decimal
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class Login(StrictModel):
    username: str = Field(min_length=3, max_length=80, pattern=r"^[a-z0-9_.@-]+$")
    password: str = Field(min_length=1, max_length=256)

class OrderCreate(StrictModel):
    customer_id: UUID
    description: str = Field(min_length=3, max_length=200)
    total: Decimal = Field(gt=0, le=1000000, max_digits=10, decimal_places=2)

class OrderStatus(StrictModel):
    status: Literal["approved", "shipped", "cancelled"]

class Product(StrictModel):
    name: str = Field(min_length=3, max_length=100)
    sku: str = Field(min_length=3, max_length=32, pattern=r"^[A-Z0-9-]+$")
    category: Literal["Equipamentos", "Software", "Serviços"]
    price_cents: StrictInt = Field(ge=1, le=100000000)
    active: bool = True

class Profile(StrictModel):
    name: str = Field(min_length=3, max_length=100)
    email: str = Field(max_length=150, pattern=r"^[A-Za-z0-9_.+-]+@example\.test$")
    segment: Literal["Essencial", "Corporativo", "Estratégico"]
    active: bool = True

class TextQuery(StrictModel):
    q: str = Field(default="", max_length=80)
    limit: int = Field(default=30, ge=1, le=100)

    @field_validator("q")
    @classmethod
    def no_operators(cls, value):
        if any(ch in value for ch in "${}[]"):
            raise ValueError("Use texto simples; objetos e operadores não são aceitos.")
        return value

class CatalogQuery(TextQuery):
    category: Literal["Equipamentos", "Software", "Serviços"] | None = None

class ProfileQuery(TextQuery):
    segment: Literal["Essencial", "Corporativo", "Estratégico"] | None = None
