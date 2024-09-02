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
        values = data.__dict__["_values"].copy()

        for field in ["created_at", "updated_at"]:
            if field in values and isinstance(values[field], str):
                values[field] = datetime.fromisoformat(values[field].rstrip("Z"))

        return cls(**values)


class CompanyView(BaseModel):
    id: int
    name: str


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


class UserView(BasecampObject):
    name: str
    email_address: str
    admin: bool
    company: Optional[CompanyView] = None
    attachable_sgid: Optional[str] = None
    personable_type: Optional[str] = None
    owner: Optional[bool] = None
    client: Optional[bool] = None
    employee: Optional[bool] = None
    time_zone: Optional[str] = None
    avatar_url: Optional[str] = None
    can_ping: Optional[bool] = None
    can_manage_projects: Optional[bool] = None
    can_manage_people: Optional[bool] = None
    can_access_timesheet: Optional[bool] = None
