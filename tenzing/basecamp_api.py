from basecampy3 import Basecamp3
from basecampy3.endpoints.projects import Project as RawProject
from basecampy3.endpoints.todolists import TodoList as RawTodoList
from basecampy3.endpoints.people import Person as RawPerson

from tenzing.models import (
    ProjectView,
    UserView,
    TodoListView,
    TodoItemView,
)
from tenzing.config import read_config


class BasecampAPI:
    def __init__(self) -> None:
        self.bc3 = Basecamp3.from_environment()

    def get_raw_projects(self) -> list[RawProject]:
        return list(self.bc3.projects.list())

    def get_raw_project(self, id: str) -> RawProject | None:
        return self.bc3.projects.get(id)

    def get_raw_users(self) -> list[RawPerson]:
        return list(self.bc3.people.list())

    def get_raw_todos_for_todolist(self, todolist: RawTodoList) -> list[dict]:
        return list(self.bc3.todos.list(todolist=todolist))

    def get_raw_todolists_for_project(self, project: RawProject) -> list[RawTodoList]:
        return list(self.bc3.todolists.list(project=project))

    def get_raw_todo_lists(self) -> list[RawTodoList]:
        raw_projects = self.get_raw_projects()
        all_todolists = []
        for project in raw_projects:
            project_todolists = self.get_raw_todolists_for_project(project)
            all_todolists.extend(project_todolists)
        return all_todolists

    def get_projects(self) -> list[ProjectView]:
        raw_projects = self.get_raw_projects()
        return [ProjectView.from_api_data(project) for project in raw_projects]

    def get_users(self) -> list[UserView]:
        raw_users = self.get_raw_users()
        return [UserView.from_api_data(user) for user in raw_users]

    def get_todolists_for_project(self, project: RawProject) -> list[TodoListView]:
        raw_todolists = self.get_raw_todolists_for_project(project)
        return [TodoListView.from_api_data(todolist) for todolist in raw_todolists]

    def get_todolists(self) -> list[TodoListView]:
        raw_todolists = self.get_raw_todo_lists()
        return [TodoListView.from_api_data(todolist) for todolist in raw_todolists]

    def get_todo_items_for_todo_list(self, todolist: RawTodoList) -> list[TodoItemView]:
        raw_todos = self.get_raw_todos_for_todolist(todolist)
        return [TodoItemView.from_api_data(todo) for todo in raw_todos]

    def get_todo_items(
        self, project_ids: list[str] | None = None
    ) -> list[TodoItemView]:
        if project_ids is None:
            raw_todolists = self.get_raw_todo_lists()
            all_todo_items = self._process_todolists(raw_todolists)
        else:
            print("Fetching todo items for the following projects:")
            all_todo_items = []
            for project_id in project_ids:
                project = self.get_raw_project(project_id)
                if project:
                    print(f"  - Project ID: {project_id}, Name: {project.name}")
                    raw_todolists = self.get_raw_todolists_for_project(project)
                    project_todo_items = self._process_todolists(raw_todolists)
                    all_todo_items.extend(project_todo_items)
                    print(f"    Number of todo items: {len(project_todo_items)}")
                else:
                    print(f"  - Project ID: {project_id} (not found)")

        print(f"Total number of todo items found: {len(all_todo_items)}")
        return all_todo_items

    def _process_todolists(self, todolists: list[RawTodoList]) -> list[TodoItemView]:
        todo_items = []
        for todolist in todolists:
            todo_items.extend(self.get_todo_items_for_todo_list(todolist))
        return todo_items

    def get_todos_for_user(self, user_id: str) -> list[TodoItemView]:
        """
        Get all todos assigned to the specified user across projects listed in the config.
        """
        config = read_config()
        todos = []

        for project_id in config.project_ids:
            project = self.get_raw_project(project_id)
            if project:
                todolists = self.get_raw_todolists_for_project(project)
                for todolist in todolists:
                    todo_items = self.get_raw_todos_for_todolist(todolist)
                    for todo in todo_items:
                        if any(
                            assignee["id"] == int(user_id)
                            for assignee in todo.get("assignees", [])
                        ):
                            todo_item = TodoItemView.from_api_data(todo)
                            todos.append(todo_item)
            else:
                print(f"Warning: Project with ID {project_id} not found.")

        return todos
