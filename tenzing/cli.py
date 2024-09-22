# -*- coding: utf-8 -*-

"""Console script for tenzing."""
import sys
import click
from rich import print as rprint
from rich.table import Table
import json

from tenzing.basecamp_api import BasecampAPI, RawProject
from tenzing.config import read_config
from tenzing.models import ProjectView, TodoListView, UserView, TodoItemView
from tenzing.persist import save_to_db, get_todos_for_user_from_db, fully_refresh_db


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
@click.argument("project", type=str)
def list_todolists(project):
    """List all todo lists for a specified project ID or name."""
    api = BasecampAPI()
    raw_projects: list[RawProject] = api.get_raw_projects()

    # Find the project by ID or name
    target_project = next(
        (
            p
            for p in raw_projects
            if str(p.id) == project or p.name.lower() == project.lower()
        ),
        None,
    )

    if not target_project:
        rprint(f"[red]Error:[/red] Project '{project}' not found.")
        return

    try:
        todolists: list[TodoListView] = api.get_todolists_for_project(target_project)
    except Exception as e:
        rprint(
            f"[red]Error:[/red] Failed to fetch todo lists for project '{target_project.name}'. {str(e)}"
        )
        return

    table = Table(
        title=f"Todo Lists for Project: {target_project.name} (ID: {target_project.id})"
    )
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Description", style="green")
    table.add_column("Completed", style="yellow")
    table.add_column("Completed Ratio", style="blue")

    for todolist in todolists:
        table.add_row(
            str(todolist.id),
            todolist.name,
            todolist.description or "",
            "Yes" if todolist.completed else "No",
            todolist.completed_ratio,
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
def get_todos_for_user(cached, output_json):
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
        # print(type(todos[0]))
        save_to_db(todos)

    if output_json:
        click.echo(json.dumps([todo.model_dump() for todo in todos], indent=2))
    else:
        table = Table(title="Todos for User")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Due Date", style="yellow")
        # table.add_column("Project", style="blue")

        for todo in todos:
            table.add_row(
                str(todo.id),
                todo.title,
                "Completed" if todo.completed else "Active",
                todo.due_on.strftime("%Y-%m-%d") if todo.due_on else "N/A",
                # f"{todo.project_name} ({todo.project_id})",
            )

        rprint(table)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
