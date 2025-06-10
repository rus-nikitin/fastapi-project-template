import pytest
from contextlib import contextmanager
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.core.dependencies import JwtClient, get_jwt_client


@contextmanager
def mock_authentication(mock_jwt_client):
    """Context manager for temporary authentication override"""
    def override_get_jwt_client():
        return mock_jwt_client

    app.dependency_overrides[get_jwt_client] = override_get_jwt_client
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_jwt_client, None)


class TestDistanceRoutes:
    """Test distance calculation API endpoints"""

    @pytest.fixture
    def mock_jwt_client(self):
        """Create a mock authenticated user"""
        return JwtClient(
            sub="test-client",
            roles=["base"],
            exp=9999999999
        )

    @pytest.mark.asyncio
    async def test_calculate_distance_success(self, mock_jwt_client):
        """Test successful distance calculation with authenticated user"""
        # primitive Pythagorean triples (3, 4, 5)
        request_data = {
            "point_a": {"x": 0.0, "y": 0.0},
            "point_b": {"x": 3.0, "y": 4.0}
        }

        with mock_authentication(mock_jwt_client):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post("/api/distance", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify distance calculation: sqrt((3-0)^2 + (4-0)^2) = sqrt(9+16) = 5.0
        assert data["distance"] == 5.0

    @pytest.mark.asyncio
    async def test_calculate_distance_same_points(self, mock_jwt_client):
        """Test distance calculation with same points (should be 0)"""

        # Same points
        request_data = {
            "point_a": {"x": 10.5, "y": 20.3},
            "point_b": {"x": 10.5, "y": 20.3}
        }

        with mock_authentication(mock_jwt_client):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post("/api/distance", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["distance"] == 0.0

    @pytest.mark.asyncio
    async def test_calculate_distance_unauthenticated_fails(self):
        """Test that unauthenticated requests fail"""
        # Don't override authentication - should fail
        request_data = {
            "point_a": {"x": 0.0, "y": 0.0},
            "point_b": {"x": 3.0, "y": 4.0}
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/distance", json=request_data)

        assert response.status_code == 401
