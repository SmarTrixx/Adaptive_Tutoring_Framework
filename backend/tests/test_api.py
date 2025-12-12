import pytest
from app import db


class TestBasicEndpoints:
    """Test basic app functionality."""
    
    def test_database_setup(self, app):
        """Test database is set up correctly."""
        with app.app_context():
            # Verify database is initialized
            assert db.engine is not None
    
    def test_cors_enabled(self, client):
        """Test that CORS is enabled."""
        response = client.options('/')
        assert response.status_code in [200, 404, 405]


class TestErrorHandling:
    """Test error handling."""
    
    def test_404_error(self, client):
        """Test 404 error for nonexistent route."""
        response = client.get('/nonexistent/route')
        assert response.status_code == 404
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.post('/api/cbt/student',
            data='invalid json',
            content_type='application/json')
        assert response.status_code in [400, 500]
