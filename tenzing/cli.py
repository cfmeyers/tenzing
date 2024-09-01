# -*- coding: utf-8 -*-

"""Console script for tenzing."""
import sys

import click
from rich import print as rprint
from rich.table import Table
from .basecamp_api import BasecampAPI

@click.group()
def main():
    pass

@main.command()
def list_projects():
    """List all projects in the user's Basecamp instance."""
    api = BasecampAPI()
    projects = api.list_projects()

    table = Table(title="Basecamp Projects")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Description", style="green")

    for project in projects:
        table.add_row(str(project.id), project.name, project.description or "")

    rprint(table)

# You can add more commands here in the future, for example:
# @main.command()
# def another_command():
#     pass

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
