from pydantic import BaseModel, Field
from typing import Optional, ClassVar, Type, TypeVar
from datetime import datetime

T = TypeVar("T", bound="BasecampObject")


class BasecampObject(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_api_data(cls: Type[T], data: object) -> T:
        values = data.__dict__["_values"].copy()  # Create a copy of the dictionary

        # Parse datetime strings
        for field in ["created_at", "updated_at"]:
            if field in values and isinstance(values[field], str):
                values[field] = datetime.fromisoformat(values[field].rstrip("Z"))

        return cls(**values)


class ProjectView(BasecampObject):
    status: str
    name: str
    description: str
    purpose: str
    clients_enabled: bool
    timesheet_enabled: bool
    color: Optional[str] = None
    bookmark_url: str
    url: str
    app_url: str
    dock: list[dict]
    bookmarked: bool

    class Config:
        populate_by_name = True
