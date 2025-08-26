from pydantic import BaseModel


class Client(BaseModel):
    client_id: str
    name: str
    email: str
    phone: str
    address: str
    created_at: str
    updated_at: str
