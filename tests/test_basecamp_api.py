import pytest
from unittest.mock import Mock, patch
from tenzing.basecamp_api import BasecampAPI
from basecampy3.endpoints.projects import Project

class TestBasecampAPI:
    def test_init_creates_basecamp3_instance(self):
        with patch('tenzing.basecamp_api.Basecamp3') as mock_basecamp3:
            BasecampAPI()
            mock_basecamp3.from_environment.assert_called_once()

    def test_list_projects_returns_list_of_projects(self):
        # Arrange
        mock_project1 = Mock(spec=Project)
        mock_project2 = Mock(spec=Project)
        mock_bc3 = Mock()
        mock_bc3.projects.list.return_value = [mock_project1, mock_project2]

        with patch('tenzing.basecamp_api.Basecamp3.from_environment', return_value=mock_bc3):
            api = BasecampAPI()

        # Act
        actual = api.list_projects()

        # Assert
        expected = [mock_project1, mock_project2]
        assert expected == actual

    def test_list_projects_returns_empty_list_when_no_projects(self):
        # Arrange
        mock_bc3 = Mock()
        mock_bc3.projects.list.return_value = []

        with patch('tenzing.basecamp_api.Basecamp3.from_environment', return_value=mock_bc3):
            api = BasecampAPI()

        # Act
        actual = api.list_projects()

        # Assert
        expected = []
        assert expected == actual
