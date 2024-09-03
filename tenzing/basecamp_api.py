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
        raw_projects = self.get_raw_projects()
        all_todolists = []
        for project in raw_projects:
            project_todolists = self.get_todolists_for_project(project)
            all_todolists.extend(project_todolists)
        return all_todolists

    def get_todo_items_for_todo_list(self, todolist: RawTodoList) -> list[TodoItemView]:
        raw_todos = self.get_raw_todos_for_todolist(todolist)
        return [TodoItemView.from_api_data(todo) for todo in raw_todos]
