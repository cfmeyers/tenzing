from basecampy3 import Basecamp3
from basecampy3.endpoints.projects import Project as BasecampProject
from tenzing.models import (
    ProjectView,
    UserView,
)


class BasecampAPI:
    def __init__(self) -> None:
        self.bc3 = Basecamp3.from_environment()

    def get_projects(self) -> list[ProjectView]:
        basecamp_projects = list(self.bc3.projects.list())
        return [ProjectView.from_api_data(project) for project in basecamp_projects]

    def get_users(self) -> list[UserView]:
        basecamp_users = list(self.bc3.people.list())
        return [UserView.from_api_data(user) for user in basecamp_users]
