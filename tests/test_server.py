import pytest
from unittest.mock import patch

from server import app

@pytest.fixture
def client():
    app.config.update({'TESTING': True})
    yield app.test_client()

@pytest.fixture
def clubs():
    clubs = [{'name': 'club', 'email': 'club@test.com', 'points': '10'}]
    with patch('server.clubs', clubs) as mock:
        yield mock

class TestShowSummary:
    route = '/showSummary'

    def test_found_email_can_login(self, client, clubs):
        response = client.post(self.route, data={'email': clubs[0]['email']})
        assert response.status_code == 200
        assert b"Summary" in response.data
    
    def test_not_found_email_cannot_login(self, client, clubs):
        response = client.post(self.route, data={'email': 'toto@blabla.com'}, follow_redirects=True)
        assert response.status_code == 200
        assert b"Sorry, that email wasn't found." in response.data

@patch('server.competitions', [{'name': 'COMP', 'numberOfPlaces': '15'}])
class TestPurchasePlaces:
    route = '/purchasePlaces'

    def test_can_purchase_club_points_amount(self, client, clubs):
        response = client.post(self.route, data={'competition': 'COMP', 'club': clubs[0]['name'], 'places': '10'})
        assert response.status_code == 200
        assert b"Great-booking complete!" in response.data
        assert clubs[0]['points'] == 0
    
    def test_cannot_purchase_more_than_club_points(self, client, clubs):
        response = client.post(self.route, data={'competition': 'COMP', 'club': clubs[0]['name'], 'places': '11'}, follow_redirects=True)
        assert response.status_code == 200
        assert b"You cannot redeem more points than you have." in response.data
        assert int(clubs[0]['points']) == 10
