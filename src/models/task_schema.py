
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    priority: str = "Medium"


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    status: str | None = None
    priority: str | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    priority: str

    model_config = {"from_attributes": True}
