import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime

# Create a base class for declarative models
Base = declarative_base()

# Define the path for the database
DB_PATH = os.path.expanduser("~/.config/tenzing/tenzing.db")

# Ensure the directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Create an engine and session
engine = create_engine(f"sqlite:///{DB_PATH}")
Session = sessionmaker(bind=engine)


class BaseCampEntity(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Project(BaseCampEntity):
    __tablename__ = "projects"

    status = Column(String)
    name = Column(String)
    description = Column(String)
    purpose = Column(String)
    clients_enabled = Column(Boolean)
    timesheet_enabled = Column(Boolean)
    color = Column(String)
    bookmark_url = Column(String)
    url = Column(String)
    app_url = Column(String)
    dock = Column(JSON)
    bookmarked = Column(Boolean)


class User(BaseCampEntity):
    __tablename__ = "users"

    name = Column(String)
    email_address = Column(String)
    admin = Column(Boolean)
    company = Column(JSON)
    attachable_sgid = Column(String)
    personable_type = Column(String)
    owner = Column(Boolean)
    client = Column(Boolean)
    employee = Column(Boolean)
    time_zone = Column(String)
    avatar_url = Column(String)
    can_ping = Column(Boolean)
    can_manage_projects = Column(Boolean)
    can_manage_people = Column(Boolean)
    can_access_timesheet = Column(Boolean)


class TodoList(BaseCampEntity):
    __tablename__ = "todolists"

    parent_id = Column(Integer)
    parent_type = Column(String)
    status = Column(String)
    visible_to_clients = Column(Boolean)
    title = Column(String)
    inherits_status = Column(Boolean)
    type = Column(String)
    url = Column(String)
    app_url = Column(String)
    bookmark_url = Column(String)
    subscription_url = Column(String)
    comments_count = Column(Integer)
    comments_url = Column(String)
    position = Column(Integer)
    parent = Column(JSON)  # Keep this field
    bucket = Column(JSON)
    creator = Column(JSON)
    description = Column(String)
    completed = Column(Boolean)
    completed_ratio = Column(String)
    name = Column(String)
    todos_url = Column(String)
    groups_url = Column(String)
    app_todos_url = Column(String)


class TodoItem(BaseCampEntity):
    __tablename__ = "todoitems"

    parent_id = Column(Integer)
    parent_type = Column(String)
    status = Column(String)
    visible_to_clients = Column(Boolean)
    title = Column(String)
    inherits_status = Column(Boolean)
    type = Column(String)
    url = Column(String)
    app_url = Column(String)
    bookmark_url = Column(String)
    subscription_url = Column(String)
    comments_count = Column(Integer)
    comments_url = Column(String)
    position = Column(Integer)
    parent = Column(JSON)
    bucket = Column(JSON)
    creator = Column(JSON)
    description = Column(String)
    completed = Column(Boolean)
    content = Column(String)
    starts_on = Column(Date)
    due_on = Column(Date)
    assignees = Column(JSON)
    assignee_ids = Column(JSON)
    completion_subscribers = Column(JSON)
    completion_url = Column(String)


class CurrentTodoHistory(Base):
    __tablename__ = "current_todo_history"

    todo_id = Column(Integer, primary_key=True)
    made_current_todo_at = Column(DateTime, default=datetime.now)


def init_db():
    Base.metadata.create_all(engine)


# Update these functions to use get_session()
def insert_current_todo(todo_id: int) -> None:
    with get_session() as session:
        current_todo = CurrentTodoHistory(
            todo_id=todo_id, made_current_todo_at=datetime.now()
        )
        session.merge(current_todo)
        session.commit()


def get_current_todo() -> int | None:
    with get_session() as session:
        current_todo = (
            session.query(CurrentTodoHistory)
            .order_by(CurrentTodoHistory.made_current_todo_at.desc())
            .first()
        )
    return current_todo.todo_id if current_todo else None


def get_session():
    """Get a new database session, creating the database if it doesn't exist."""
    init_db()  # Always call init_db to ensure all tables exist
    return Session()
