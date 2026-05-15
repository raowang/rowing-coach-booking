"""Test members API endpoints."""
import sys
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, "/mnt/d/GitHub/ai/agent/reserve-app/rowing-coach-booking/backend")


class TestMembersAPI:
    @pytest.fixture
    def mock_directus(self, mock_directus_client: MagicMock):
        return mock_directus_client

    @pytest.fixture
    def client(self, mock_directus: MagicMock):
        with patch("app.core.directus.get_directus_client", return_value=mock_directus):
            with patch("app.api.v1.members.get_directus_client", return_value=mock_directus):
                from fastapi import FastAPI
                from app.api.v1.members import router
                app = FastAPI()
                app.include_router(router)
                with TestClient(app) as c:
                    yield c

    def test_create_member_success(
        self,
        client: TestClient,
        mock_directus: MagicMock,
        sample_member_data: dict[str, Any],
    ):
        mock_directus.create_item = AsyncMock(
            return_value={"data": sample_member_data}
        )
        response = client.post("/", json={
            "openid": "test_openid",
            "name": "Test Member",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Member"

    def test_get_member_found(
        self,
        client: TestClient,
        mock_directus: MagicMock,
        sample_member_data: dict[str, Any],
    ):
        mock_directus.get_item = AsyncMock(
            return_value={"data": sample_member_data}
        )
        response = client.get("/member-123")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "member-123"

    def test_get_member_not_found(
        self,
        client: TestClient,
        mock_directus: MagicMock,
    ):
        mock_directus.get_item = AsyncMock(return_value={"data": None})
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_list_members(
        self,
        client: TestClient,
        mock_directus: MagicMock,
        sample_member_data: dict[str, Any],
    ):
        mock_directus.query = AsyncMock(
            return_value={"data": [sample_member_data]}
        )
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "member-123"

    def test_list_members_with_skill_level_filter(
        self,
        client: TestClient,
        mock_directus: MagicMock,
        sample_member_data: dict[str, Any],
    ):
        mock_directus.query = AsyncMock(
            return_value={"data": [sample_member_data]}
        )
        response = client.get("/?skill_level=intermediate")
        assert response.status_code == 200
        mock_directus.query.assert_called()

    def test_update_member_success(
        self,
        client: TestClient,
        mock_directus: MagicMock,
        sample_member_data: dict[str, Any],
    ):
        updated_data = dict(sample_member_data)
        updated_data["name"] = "Updated Name"
        mock_directus.get_item = AsyncMock(return_value={"data": sample_member_data})
        mock_directus.update_item = AsyncMock(return_value={"data": updated_data})
        response = client.patch("/member-123", json={"name": "Updated Name"})
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_update_member_not_found(
        self,
        client: TestClient,
        mock_directus: MagicMock,
    ):
        mock_directus.get_item = AsyncMock(return_value={"data": None})
        response = client.patch("/nonexistent", json={"name": "New Name"})
        assert response.status_code == 404

    def test_update_member_no_fields(
        self,
        client: TestClient,
        mock_directus: MagicMock,
        sample_member_data: dict[str, Any],
    ):
        mock_directus.get_item = AsyncMock(return_value={"data": sample_member_data})
        response = client.patch("/member-123", json={})
        assert response.status_code == 400

    def test_delete_member_success(
        self,
        client: TestClient,
        mock_directus: MagicMock,
    ):
        mock_directus.delete_item = AsyncMock(return_value={"data": None})
        response = client.delete("/member-123")
        assert response.status_code == 200
        assert response.json()["message"] == "Member deleted successfully"
