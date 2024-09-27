from typing import Type, List
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy import func

from tenzing.db import Project, User, TodoList, TodoItem, get_session
from tenzing.models import ProjectView, UserView, TodoListView, TodoItemView
from tenzing.basecamp_api import BasecampAPI
from tenzing.config import read_config, Config


def pydantic_to_sqlalchemy(pydantic_instance: BaseModel) -> DeclarativeBase:
    """
    Convert a Pydantic model instance to its corresponding SQLAlchemy model instance.
    """
    match type(pydantic_instance).__name__:
        case "ProjectView":
            sqlalchemy_model = Project
        case "UserView":
            sqlalchemy_model = User
        case "TodoListView":
            sqlalchemy_model = TodoList
        case "TodoItemView":
            sqlalchemy_model = TodoItem
        case _:
            raise ValueError(f"Unsupported Pydantic model: {type(pydantic_instance)}")

    return sqlalchemy_model(**pydantic_instance.model_dump(exclude_unset=True))


def sqlalchemy_to_pydantic(sqlalchemy_instance: DeclarativeBase) -> BaseModel:
    """
    Convert a SQLAlchemy model instance to its corresponding Pydantic model instance.
    """
    match type(sqlalchemy_instance).__name__:
        case "Project":
            pydantic_model = ProjectView
        case "User":
            pydantic_model = UserView
        case "TodoList":
            pydantic_model = TodoListView
        case "TodoItem":
            pydantic_model = TodoItemView
        case _:
            raise ValueError(
                f"Unsupported SQLAlchemy model: {type(sqlalchemy_instance)}"
            )

    return pydantic_model.model_validate(sqlalchemy_instance)


def save_to_db(items: List[BaseModel]) -> None:
    """
    Save a list of Pydantic model instances to the database.
    """
    session = get_session()
    try:
        new_items = 0
        updated_items = 0
        for item in items:
            db_item = pydantic_to_sqlalchemy(item)
            existing_item = (
                session.query(type(db_item)).filter_by(id=db_item.id).first()
            )
            if existing_item:
                session.merge(db_item)
                updated_items += 1
            else:
                session.add(db_item)
                new_items += 1
        session.commit()
        print(
            f"Saved {len(items)} {type(items[0]).__name__}s to db ({new_items} new, {updated_items} updated)"
        )
    except Exception as e:
        session.rollback()
        print(f"Error saving to database: {str(e)}")
    finally:
        session.close()


def fully_refresh_db(api: BasecampAPI) -> None:
    config: Config = read_config()

    users = api.get_users()
    save_to_db(users)

    projects = api.get_projects()
    save_to_db(projects)

    todo_lists = api.get_todolists()
    save_to_db(todo_lists)

    todo_items = api.get_todo_items(project_ids=config.project_ids)
    save_to_db(todo_items)


def get_todos_for_user_from_db() -> list[TodoItemView]:
    config = read_config()
    user_id = config.user_id
    if user_id is None:
        raise ValueError("User ID not found in configuration")

    session = get_session()
    try:
        db_todos = (
            session.query(TodoItem)
            .filter(TodoItem.assignee_ids.like(f'%"{user_id}"%'))
            .all()
        )

        return [sqlalchemy_to_pydantic(db_todo) for db_todo in db_todos]
    finally:
        session.close()


def get_todolist_from_db(todolist_id: int) -> TodoListView | None:
    """
    Retrieve a specific TodoList from the database by its ID.

    Args:
        todolist_id (int): The ID of the TodoList to retrieve.

    Returns:
        TodoListView | None: The TodoList as a TodoListView if found, None otherwise.
    """
    session = get_session()
    try:
        db_todolist = session.query(TodoList).filter(TodoList.id == todolist_id).first()
        return sqlalchemy_to_pydantic(db_todolist) if db_todolist else None
    finally:
        session.close()


def get_project_from_db(project_id: int) -> ProjectView | None:
    """
    Retrieve a specific Project from the database by its ID.

    Args:
        project_id (int): The ID of the Project to retrieve.

    Returns:
        ProjectView | None: The Project as a ProjectView if found, None otherwise.
    """
    session = get_session()
    try:
        db_project = session.query(Project).filter(Project.id == project_id).first()
        return sqlalchemy_to_pydantic(db_project) if db_project else None
    finally:
        session.close()
