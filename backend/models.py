from pydantic import BaseModel, EmailStr, Field, constr
from datetime import datetime


ISO8601 = "%Y-%m-%dT%H:%M:%SZ"


class Client(BaseModel):
    client_id: str
    name: str = Field(min_length=1)
    email: EmailStr | None = None
    phone: constr(strip_whitespace=True, min_length=3) | None = None
    address: str | None = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "Client":
        return cls(**data)
