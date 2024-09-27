# -*- coding: utf-8 -*-

"""Console script for tenzing."""
import sys
import click
from rich import print as rprint
from rich.table import Table
import json
from datetime import datetime, date

from tenzing.basecamp_api import BasecampAPI, RawProject
from tenzing.config import read_config
from tenzing.models import ProjectView, TodoListView, UserView, TodoItemView
from tenzing.persist import (
    save_to_db,
    get_todos_for_user_from_db,
    fully_refresh_db,
    sqlalchemy_to_pydantic,
)
from tenzing.db import (
    get_current_todo as get_current_todo_id,
    insert_current_todo,
    get_session,
    init_db,
    TodoItem,
)
from tenzing.models import TodoItemView
from tenzing.edit import create_todo_from_editor


@click.group()
def main():
    pass


@main.command()
def list_projects():
    """List all projects in the user's Basecamp instance."""
    api = BasecampAPI()
    projects: list[ProjectView] = api.get_projects()

    table = Table(title="Basecamp Projects")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Description", style="green")
    table.add_column("Created At", style="yellow")

    for project in projects:
        table.add_row(
            str(project.id),
            project.name,
            project.description or "",
            project.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    rprint(table)


@main.command()
def list_users():
    """List all users in the user's Basecamp instance."""
    api = BasecampAPI()
    users: list[UserView] = api.get_users()

    table = Table(title="Basecamp Users")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Email Address", style="green")
    table.add_column("Admin", style="yellow")
    table.add_column("Company", style="blue")

    for user in users:
        table.add_row(
            str(user.id),
            user.name,
            user.email_address,
            "Yes" if user.admin else "No",
            user.company.get("name", "N/A") if user.company else "N/A",
        )

    rprint(table)


@main.command()
@click.option(
    "--project-id",
    type=str,
    default=None,
    help="Project ID. If not provided, lists todos for all configured projects.",
)
@click.option(
    "--json", "output_json", is_flag=True, help="Output todo lists in JSON format"
)
def list_todolists(project_id, output_json):
    """List all todo lists for a specified project ID, or for all configured projects if not specified."""
    api = BasecampAPI()
    config = read_config()

    if project_id:
        target_project = api.get_raw_project(project_id)
        if not target_project:
            rprint(f"[red]Error:[/red] Project with ID '{project_id}' not found.")
            return

        project_ids = [target_project.id]
        table_title = (
            f"Todo Lists for Project: {target_project.name} (ID: {target_project.id})"
        )
    else:
        project_ids = config.project_ids
        table_title = "Todo Lists for All Configured Projects"

    todolists = []
    for pid in project_ids:
        try:
            project_todolists = api.get_todolists_for_project(api.get_raw_project(pid))
            todolists.extend(project_todolists)
        except Exception as e:
            rprint(
                f"[red]Error:[/red] Failed to fetch todo lists for project ID {pid}. {str(e)}"
            )

    if output_json:
        todolists_json = [todolist.model_dump(mode="json") for todolist in todolists]
        click.echo(json.dumps(todolists_json, indent=2))
    else:
        table = Table(title=table_title)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Completed", style="yellow")
        table.add_column("Completed Ratio", style="blue")
        table.add_column("Project ID", style="cyan")

        for todolist in todolists:
            table.add_row(
                str(todolist.id),
                todolist.name,
                todolist.description or "",
                "Yes" if todolist.completed else "No",
                todolist.completed_ratio,
                str(todolist.parent_id),
            )

        rprint(table)


@main.command()
@click.argument("project_id", type=str)
@click.argument("todo_list_id", type=str)
def list_todo_items(project_id, todo_list_id):
    """List all todo items for a specified project ID and todo list ID."""
    api = BasecampAPI()

    # Find the project
    target_project = api.get_raw_project(project_id)
    if not target_project:
        rprint(f"[red]Error:[/red] Project with ID '{project_id}' not found.")
        return

    # Find the todo list within the project
    todolists = api.get_raw_todolists_for_project(target_project)
    target_todolist = next((tl for tl in todolists if str(tl.id) == todo_list_id), None)

    if not target_todolist:
        rprint(
            f"[red]Error:[/red] Todo list with ID '{todo_list_id}' not found in project '{target_project.name}'."
        )
        return

    try:
        todo_items: list[TodoItemView] = api.get_todo_items_for_todo_list(
            target_todolist
        )
    except Exception as e:
        rprint(
            f"[red]Error:[/red] Failed to fetch todo items for todo list '{todo_list_id}' in project '{target_project.name}'. {str(e)}"
        )
        return

    table = Table(
        title=f"Todo Items for Todo List: {target_todolist.title} (ID: {target_todolist.id}) in Project: {target_project.name} (ID: {target_project.id})"
    )
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Description", style="green")
    table.add_column("Assignees", style="yellow")
    table.add_column("Due Date", style="blue")
    table.add_column("Completed", style="red")

    for todo_item in todo_items:
        assignees = ", ".join([assignee["name"] for assignee in todo_item.assignees])
        due_date = todo_item.due_on.strftime("%Y-%m-%d") if todo_item.due_on else "N/A"
        description = todo_item.description or ""
        # Truncate description if it's too long
        if len(description) > 50:
            description = description[:47] + "..."
        table.add_row(
            str(todo_item.id),
            todo_item.title,
            description,
            assignees,
            due_date,
            "Yes" if todo_item.completed else "No",
        )

    rprint(table)


@main.command()
def refresh_db():
    """Fetch all projects from Basecamp API and refresh the local database."""
    api = BasecampAPI()
    try:
        fully_refresh_db(api)
        rprint(
            "[green]Successfully refreshed the database with latest Basecamp data.[/green]"
        )
    except Exception as e:
        rprint(f"[red]Error:[/red] Failed to refresh the database. {str(e)}")


@main.command()
@click.option("--cached", is_flag=True, help="Get todos from the local database")
@click.option("--json", "output_json", is_flag=True, help="Output todos in JSON format")
@click.option("--active-only", is_flag=True, help="Only show active todos")
def get_todos_for_user(cached, output_json, active_only):
    """Get todos for the configured user from the projects specified in the config."""
    api = BasecampAPI()

    if cached:
        todos = get_todos_for_user_from_db()
    else:
        config = read_config()
        user_id = config.user_id
        if user_id is None:
            raise ValueError("User ID not found in configuration")
        todos = api.get_todos_for_user(user_id)
        save_to_db(todos)

    if active_only:
        todos = [
            todo for todo in todos if not todo.completed and todo.status != "trashed"
        ]

    todos.sort(key=lambda todo: todo.get_todo_list_name())

    if output_json:
        todos_as_list_of_dicts = [todo.model_dump(mode="json") for todo in todos]
        json_data = json.dumps(todos_as_list_of_dicts, indent=2)
        click.echo(json_data)
    else:
        table = Table(title="Todos for User")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("List", style="blue")

        for todo in todos:
            parent_list_name = f"{todo.get_todo_list_name()[:30]} ({todo.parent_id})"

            if todo.status == "trashed":
                status = "Deleted"
            elif todo.completed:
                status = "Completed"
            else:
                status = "Active"

            table.add_row(
                str(todo.id),
                todo.title,
                status,
                parent_list_name,
            )

        rprint(table)


@main.command()
@click.option(
    "--json", "output_json", is_flag=True, help="Output current todo in JSON format"
)
def get_current_todo(output_json):
    """Get the current todo item."""
    current_todo_id = get_current_todo_id()
    if current_todo_id is None:
        if output_json:
            click.echo(json.dumps({"error": "No current todo set"}))
        else:
            rprint("[yellow]No current todo set.[/yellow]")
        return

    with get_session() as session:
        todo_sqlalchemy = (
            session.query(TodoItem).filter(TodoItem.id == current_todo_id).first()
        )
        if todo_sqlalchemy:
            todo_item_view = sqlalchemy_to_pydantic(todo_sqlalchemy)
            if output_json:
                click.echo(todo_item_view.model_dump_json(indent=2))
            else:
                table = Table(title="Current Todo")
                table.add_column("ID", style="cyan")
                table.add_column("Title", style="magenta")
                table.add_column("Status", style="green")
                table.add_column("Due Date", style="yellow")

                table.add_row(
                    str(todo_item_view.id),
                    todo_item_view.title,
                    "Completed" if todo_item_view.completed else "Not Completed",
                    str(todo_item_view.due_on) if todo_item_view.due_on else "Not set",
                )

                rprint(table)
        else:
            if output_json:
                click.echo(
                    json.dumps(
                        {
                            "error": f"Todo with ID {current_todo_id} not found in the database"
                        }
                    )
                )
            else:
                rprint(
                    f"[red]Todo with ID {current_todo_id} not found in the database.[/red]"
                )


@main.command()
@click.argument("todo_id", type=int)
def set_current_todo(todo_id):
    """Set the current todo item."""
    with get_session() as session:
        todo = session.query(TodoItem).filter(TodoItem.id == todo_id).first()
        if todo:
            insert_current_todo(todo_id)
            rprint(
                f"[green]Set todo '{todo.title}' (ID: {todo_id}) as the current todo.[/green]"
            )
        else:
            rprint(f"[red]Todo with ID {todo_id} not found in the database.[/red]")


@main.command()
def init_database():
    """Initialize the database and create all tables."""
    init_db()
    rprint("[green]Database initialized successfully.[/green]")


@main.command()
@click.option("--title", prompt=True, help="The title of the todo")
@click.option("--body", prompt=True, help="The detailed description of the todo")
@click.option("--todolist-id", type=int, prompt=True, help="The ID of the todolist")
@click.option("--project-id", type=int, prompt=True, help="The ID of the project")
def create_todo(title, body, todolist_id, project_id):
    """Create a new todo in Basecamp and save it to the local database."""
    api = BasecampAPI()
    config = read_config()

    # Use the current user's ID from config.toml
    assignee_id = config.user_id

    # Call the Basecamp API to create the todo
    new_todo = api.create_todo(project_id, todolist_id, title, body, assignee_id)

    if new_todo:
        # Save the new todo to the local database
        todo_view = TodoItemView.from_api_data(new_todo)
        save_to_db([todo_view])

        # Display success message with the new todo's details
        table = Table(title="New Todo Created")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("ID", str(todo_view.id))
        table.add_row("Title", todo_view.title)
        table.add_row(
            "Body",
            (
                todo_view.description[:50] + "..."
                if len(todo_view.description) > 50
                else todo_view.description
            ),
        )
        table.add_row("Project ID", str(project_id))
        table.add_row("Todolist ID", str(todo_view.parent_id))
        table.add_row("Assignee ID", str(assignee_id))

        rprint("[green]Todo created successfully![/green]")
        rprint(table)
    else:
        rprint("[red]Failed to create todo.[/red]")


@main.command()
@click.option(
    "--todolist-id",
    type=int,
    help="The ID of the todolist to create the todo in",
    default=None,
)
def create_todo_editor(todolist_id):
    """Create a new todo using the default editor."""
    new_todo = create_todo_from_editor(todolist_id)
    if new_todo:
        click.echo(
            f"Todo '{new_todo.title}' created successfully in todolist {new_todo.parent_id}"
        )
    else:
        click.echo("Failed to create todo")


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
