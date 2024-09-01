from basecampy3 import Basecamp3
from basecampy3.endpoints.projects import Project

class BasecampAPI:
    def __init__(self) -> None:
        self.bc3 = Basecamp3.from_environment()

    def list_projects(self) -> list[Project]:
        return list(self.bc3.projects.list())