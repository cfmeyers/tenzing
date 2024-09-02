from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BaseCampEntityView(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_api_data(cls, data: object):
        values = data.__dict__["_values"].copy()

        for field in ["created_at", "updated_at"]:
            if field in values and isinstance(values[field], str):
                values[field] = datetime.fromisoformat(values[field].rstrip("Z"))

        return cls(**values)


class ProjectView(BaseCampEntityView):
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


class UserView(BaseCampEntityView):
    name: str
    email_address: str
    admin: bool
    company: Optional[dict] = None
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


class TodoListView(BaseCampEntityView):
    status: str
    visible_to_clients: bool
    title: str
    inherits_status: bool
    type: str
    url: str
    app_url: str
    bookmark_url: str
    subscription_url: str
    comments_count: int
    comments_url: str
    position: int
    parent: dict
    bucket: dict
    creator: dict
    description: str
    completed: bool
    completed_ratio: str
    name: str
    todos_url: str
    groups_url: str
    app_todos_url: str

    class Config:
        populate_by_name = True
