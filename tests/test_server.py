import pytest
from unittest.mock import patch

from server import app

@pytest.fixture
def client():
    app.config.update({'TESTING': True})
    yield app.test_client()

@patch('server.clubs', [{'email': 'test@test.com'}])
class TestShowSummary:
    route = '/showSummary'

    def test_found_email_can_login(self, client):
        response = client.post(self.route, data={'email': 'test@test.com'})
        assert response.status_code == 200
        assert b"Summary" in response.data
    
    def test_not_found_email_cannot_login(self, client):
        response = client.post(self.route, data={'email': 'toto@blabla.com'}, follow_redirects=True)
        assert response.status_code == 200
        assert b"Sorry, that email wasn't found." in response.data