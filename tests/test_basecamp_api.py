import pytest
from unittest.mock import Mock, patch, MagicMock
from tenzing.basecamp_api import BasecampAPI
from tenzing.models import ProjectView, UserView, TodoListView
from datetime import datetime, timezone


class TestBasecampAPI:
    def test_init_creates_basecamp3_instance(self):
        with patch("tenzing.basecamp_api.Basecamp3") as mock_basecamp3:
            BasecampAPI()
            mock_basecamp3.from_environment.assert_called_once()

    def test_get_projects_returns_list_of_project_views(self):
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
        actual = api.get_projects()

        # Assert
        assert expected == actual

    def test_get_users_returns_list_of_user_views(self):
        # Arrange
        expected = [
            UserView(
                id=1,
                created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
                name="John Doe",
                email_address="john@example.com",
                admin=True,
                company={
                    "id": 101,
                    "name": "Example Corp",
                },
            ),
            UserView(
                id=2,
                created_at=datetime(2024, 2, 1, tzinfo=timezone.utc),
                updated_at=datetime(2024, 2, 2, tzinfo=timezone.utc),
                name="Jane Smith",
                email_address="jane@example.com",
                admin=False,
                company=None,
            ),
        ]

        mock_bc3 = Mock()
        mock_bc3.people.list.return_value = [
            MagicMock(_values=user.model_dump()) for user in expected
        ]

        with patch(
            "tenzing.basecamp_api.Basecamp3.from_environment", return_value=mock_bc3
        ):
            api = BasecampAPI()

        # Act
        actual = api.get_users()

        # Assert
        assert expected == actual

    def test_get_todolists_for_project(self):
        # Arrange
        project = ProjectView(
            id=1,
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
            status="active",
            name="Test Project",
            description="Test Description",
            purpose="Test Purpose",
            clients_enabled=True,
            timesheet_enabled=False,
            bookmark_url="http://example.com/1",
            url="http://example.com/1",
            app_url="http://example.com/app/1",
            dock=[],
            bookmarked=False,
        )

        expected_todolists = [
            TodoListView(
                id=101,
                created_at=datetime(2024, 1, 3, tzinfo=timezone.utc),
                updated_at=datetime(2024, 1, 4, tzinfo=timezone.utc),
                status="active",
                visible_to_clients=True,
                title="Todo List 1",
                inherits_status=True,
                type="TodoList",
                url="http://example.com/todolist/101",
                app_url="http://example.com/app/todolist/101",
                bookmark_url="http://example.com/bookmark/101",
                subscription_url="http://example.com/subscribe/101",
                comments_count=5,
                comments_url="http://example.com/comments/101",
                position=1,
                parent={},
                bucket={"id": 1, "name": "Test Project"},
                creator={"id": 1, "name": "John Doe"},
                description="Todo List 1 Description",
                completed=False,
                completed_ratio="0/5",
                name="Todo List 1",
                todos_url="http://example.com/todos/101",
                groups_url="http://example.com/groups/101",
                app_todos_url="http://example.com/app/todos/101",
            ),
            TodoListView(
                id=102,
                created_at=datetime(2024, 1, 5, tzinfo=timezone.utc),
                updated_at=datetime(2024, 1, 6, tzinfo=timezone.utc),
                status="active",
                visible_to_clients=False,
                title="Todo List 2",
                inherits_status=True,
                type="TodoList",
                url="http://example.com/todolist/102",
                app_url="http://example.com/app/todolist/102",
                bookmark_url="http://example.com/bookmark/102",
                subscription_url="http://example.com/subscribe/102",
                comments_count=3,
                comments_url="http://example.com/comments/102",
                position=2,
                parent={},
                bucket={"id": 1, "name": "Test Project"},
                creator={"id": 2, "name": "Jane Smith"},
                description="Todo List 2 Description",
                completed=True,
                completed_ratio="3/3",
                name="Todo List 2",
                todos_url="http://example.com/todos/102",
                groups_url="http://example.com/groups/102",
                app_todos_url="http://example.com/app/todos/102",
            ),
        ]

        mock_bc3 = Mock()
        mock_bc3.todolists.list.return_value = [
            MagicMock(_values=todolist.model_dump()) for todolist in expected_todolists
        ]

        with patch(
            "tenzing.basecamp_api.Basecamp3.from_environment", return_value=mock_bc3
        ):
            api = BasecampAPI()

        # Act
        actual = api.get_todolists_for_project(project)

        # Assert
        assert expected_todolists == actual
        mock_bc3.todolists.list.assert_called_once_with(project=project)
