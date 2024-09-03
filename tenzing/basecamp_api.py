from basecampy3 import Basecamp3
from basecampy3.endpoints.projects import Project as Basecampy3Project
from basecampy3.endpoints.todolists import TodoList as Basecampy3TodoList


from tenzing.models import (
    ProjectView,
    UserView,
    TodoListView,
    TodoItemView,
)


class BasecampAPI:
    def __init__(self) -> None:
        self.bc3 = Basecamp3.from_environment()

    def get_basecamp_projects(self) -> list[Basecampy3Project]:
        return list(self.bc3.projects.list())

    def get_basecamp_project(self, id: str) -> Basecampy3Project | None:
        return self.bc3.projects.get(id)

    def get_projects(self) -> list[ProjectView]:
        basecamp_projects = self.get_basecamp_projects()
        return [ProjectView.from_api_data(project) for project in basecamp_projects]

    def get_users(self) -> list[UserView]:
        basecamp_users = list(self.bc3.people.list())
        return [UserView.from_api_data(user) for user in basecamp_users]

    def get_basecamp_todolists_for_project(
        self, project: Basecampy3Project
    ) -> list[Basecampy3TodoList]:
        return list(self.bc3.todolists.list(project=project))

    def get_todolists_for_project(
        self, project: Basecampy3Project
    ) -> list[TodoListView]:
        basecamp_todolists = self.get_basecamp_todolists(project)
        return [TodoListView.from_api_data(todolist) for todolist in basecamp_todolists]

    def get_todolists(self) -> list[TodoListView]:
        basecamp_projects = self.get_basecamp_projects()
        all_todolists = []
        for project in basecamp_projects:
            project_todolists = self.get_todolists_for_project(project)
            all_todolists.extend(project_todolists)
        return all_todolists

    def get_basecamp_todos_for_todolist(
        self, todolist: Basecampy3TodoList
    ) -> list[dict]:
        return list(self.bc3.todos.list(todolist=todolist))

    def get_todo_items_for_todo_list(
        self, todolist: Basecampy3TodoList
    ) -> list[TodoItemView]:
        basecamp_todos = self.get_basecamp_todos_for_todolist(todolist)
        return [TodoItemView.from_api_data(todo) for todo in basecamp_todos]
