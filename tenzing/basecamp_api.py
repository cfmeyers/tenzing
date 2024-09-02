from basecampy3 import Basecamp3
from basecampy3.endpoints.projects import Project as Basecampy3Project
from tenzing.models import (
    ProjectView,
    UserView,
    TodoListView,
)


class BasecampAPI:
    def __init__(self) -> None:
        self.bc3 = Basecamp3.from_environment()

    def get_basecamp_projects(self) -> list[Basecampy3Project]:
        return list(self.bc3.projects.list())

    def get_projects(self) -> list[ProjectView]:
        basecamp_projects = self.get_basecamp_projects()
        return [ProjectView.from_api_data(project) for project in basecamp_projects]

    def get_users(self) -> list[UserView]:
        basecamp_users = list(self.bc3.people.list())
        return [UserView.from_api_data(user) for user in basecamp_users]

    def get_todolists_for_project(
        self, project: Basecampy3Project
    ) -> list[TodoListView]:
        basecamp_todolists = list(self.bc3.todolists.list(project=project))
        return [TodoListView.from_api_data(todolist) for todolist in basecamp_todolists]

    def get_todolists(self) -> list[TodoListView]:
        basecamp_projects = self.get_basecamp_projects()
        all_todolists = []
        for project in basecamp_projects:
            project_todolists = self.get_todolists_for_project(project)
            all_todolists.extend(project_todolists)
        return all_todolists
