import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.domains.user.models import User
from app.domains.user.dependencies import get_current_user


class TestDistanceRoutes:
    """Test distance calculation API endpoints"""

    @pytest.fixture
    def mock_authenticated_user(self):
        """Create a mock authenticated user"""
        return User(
            id=1,
            email="user@example.com",
            name="Test User",
            is_active=True,
            is_admin=False
        )

    @pytest.fixture(autouse=True)
    async def setup_and_teardown(self):
        """Clean up dependency overrides after each test"""
        yield
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_calculate_distance_success(self, mock_authenticated_user):
        """Test successful distance calculation with authenticated user"""

        # Override authentication dependency
        def override_get_current_user():
            return mock_authenticated_user

        app.dependency_overrides[get_current_user] = override_get_current_user

        # Test data
        request_data = {
            "point_a": {"x": 0.0, "lon": 0.0},
            "point_b": {"x": 3.0, "lon": 4.0}
        }
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/distance", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify distance calculation: sqrt((3-0)^2 + (4-0)^2) = sqrt(9+16) = 5.0
        assert data["distance"] == 5.0

    @pytest.mark.asyncio
    async def test_calculate_distance_same_points(self, mock_authenticated_user):
        """Test distance calculation with same points (should be 0)"""

        def override_get_current_user():
            return mock_authenticated_user

        app.dependency_overrides[get_current_user] = override_get_current_user

        # Same points
        request_data = {
            "point_a": {"x": 10.5, "lon": 20.3},
            "point_b": {"x": 10.5, "lon": 20.3}
        }

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
            "point_a": {"x": 0.0, "lon": 0.0},
            "point_b": {"x": 3.0, "lon": 4.0}
        }
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/distance", json=request_data)

        assert response.status_code == 401
        assert "Authentication not implemented yet" in response.json()["detail"]
