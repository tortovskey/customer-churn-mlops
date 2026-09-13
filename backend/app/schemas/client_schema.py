from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TariffType = Literal["basic", "standard", "premium", "enterprise"]


class ClientBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    age: int = Field(..., ge=18, le=100)
    tenure_months: int = Field(..., ge=0, le=360)
    monthly_payment: float = Field(..., ge=0, le=100000)
    support_requests: int = Field(..., ge=0, le=1000)
    tariff_type: TariffType
    last_month_activity: float = Field(..., ge=0, le=100)
    has_debt: bool = False


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    age: int | None = Field(default=None, ge=18, le=100)
    tenure_months: int | None = Field(default=None, ge=0, le=360)
    monthly_payment: float | None = Field(default=None, ge=0, le=100000)
    support_requests: int | None = Field(default=None, ge=0, le=1000)
    tariff_type: TariffType | None = None
    last_month_activity: float | None = Field(default=None, ge=0, le=100)
    has_debt: bool | None = None


class ClientRead(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

