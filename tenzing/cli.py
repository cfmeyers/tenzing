# -*- coding: utf-8 -*-

"""Console script for tenzing."""
import sys

import click
from rich import print as rprint
from rich.table import Table

from tenzing.basecamp_api import BasecampAPI
from tenzing.models import ProjectView


@click.group()
def main():
    pass


@main.command()
def list_projects():
    """List all projects in the user's Basecamp instance."""
    api = BasecampAPI()
    projects: list[ProjectView] = api.list_projects()

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


# You can add more commands here in the future, for example:
# @main.command()
# def another_command():
#     pass

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

# project = projects[0]

# dir(project)
# project.__dict__

# dump project.__dict__ as json to a file
# import json

# with open("example-entities/project.json", "w") as f:
#     json.dump(project.__dict__["_values"], f, indent=4)
