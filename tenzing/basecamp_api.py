from basecampy3 import Basecamp3
from basecampy3.endpoints.projects import Project as BasecampProject
from tenzing.models import ProjectView


class BasecampAPI:
    def __init__(self) -> None:
        self.bc3 = Basecamp3.from_environment()

    def list_projects(self) -> list[ProjectView]:
        basecamp_projects = list(self.bc3.projects.list())
        return [ProjectView.from_api_data(project) for project in basecamp_projects]
