import pytest
from unittest.mock import Mock, patch, MagicMock
from tenzing.basecamp_api import BasecampAPI
from tenzing.models import ProjectView
from datetime import datetime, timezone


class TestBasecampAPI:
    def test_init_creates_basecamp3_instance(self):
        with patch("tenzing.basecamp_api.Basecamp3") as mock_basecamp3:
            BasecampAPI()
            mock_basecamp3.from_environment.assert_called_once()

    def test_list_projects_returns_list_of_project_views(self):
        # Arrange
        expected = [
            ProjectView(
                id=1,
                created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
                status="active",
                name="Project 1",
                description="Description 1",
                purpose="purpose 1",
                clients_enabled=True,
                timesheet_enabled=False,
                bookmark_url="http://example.com/1",
                url="http://example.com/1",
                app_url="http://example.com/app/1",
                dock=[],
                bookmarked=False,
            ),
            ProjectView(
                id=2,
                created_at=datetime(2024, 2, 1, tzinfo=timezone.utc),
                updated_at=datetime(2024, 2, 2, tzinfo=timezone.utc),
                status="active",
                name="Project 2",
                description="Description 2",
                purpose="purpose 2",
                clients_enabled=False,
                timesheet_enabled=True,
                bookmark_url="http://example.com/2",
                url="http://example.com/2",
                app_url="http://example.com/app/2",
                dock=[],
                bookmarked=True,
            ),
        ]

        mock_bc3 = Mock()
        mock_bc3.projects.list.return_value = [
            MagicMock(_values=project.model_dump()) for project in expected
        ]

        with patch(
            "tenzing.basecamp_api.Basecamp3.from_environment", return_value=mock_bc3
        ):
            api = BasecampAPI()

        # Act
        actual = api.list_projects()

        # Assert
        assert expected == actual

    def test_list_projects_returns_empty_list_when_no_projects(self):
        # Arrange
        mock_bc3 = Mock()
        mock_bc3.projects.list.return_value = []

        with patch(
            "tenzing.basecamp_api.Basecamp3.from_environment", return_value=mock_bc3
        ):
            api = BasecampAPI()

        # Act
        actual = api.list_projects()

        # Assert
        assert actual == []
