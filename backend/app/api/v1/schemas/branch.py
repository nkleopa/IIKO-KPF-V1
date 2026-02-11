from pydantic import BaseModel


class BranchResponse(BaseModel):
    id: int
    name: str
    city: str | None = None
    territory: str | None = None
    is_active: bool
