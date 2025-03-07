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

@pytest.fixture
def competitions():
    competitions = [{'name': 'comp', "date": "9999-12-31 23:59:59", "numberOfPlaces": "15"}]
    with patch('server.competitions', competitions) as mock:
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

class TestPurchasePlaces:
    route = '/purchasePlaces'

    def test_can_purchase_respect_all_criteria(self, client, clubs, competitions):
        club = clubs[0]
        competition = competitions[0]
        response = client.post(self.route, data={'competition': competition['name'], 'club': club['name'], 'places': '10'})
        assert response.status_code == 200
        assert b"Great-booking complete!" in response.data
        assert club['points'] == 0
        assert competition['numberOfPlaces'] == 5
    
    def test_cannot_purchase_more_than_club_points(self, client, clubs, competitions):
        club = clubs[0]
        competition = competitions[0]
        response = client.post(self.route, data={'competition': competition['name'], 'club': club['name'], 'places': '11'}, follow_redirects=True)
        assert response.status_code == 200
        assert b"You cannot redeem more points than you have." in response.data
        assert int(club['points']) == 10
        assert int(competition['numberOfPlaces']) == 15
    
    def test_cannot_purchase_more_than_12_points(self, client, clubs, competitions):
        club = clubs[0]
        competition = competitions[0]
        response = client.post(self.route, data={'competition': competition['name'], 'club': club['name'], 'places': '13'}, follow_redirects=True)
        assert response.status_code == 200
        assert b"You cannot redeem more than 12 points." in response.data
        assert int(club['points']) == 10
        assert int(competition['numberOfPlaces']) == 15
    
    def test_cannot_purchase_on_a_past_competition(self, client, clubs, competitions):
        club = clubs[0]
        competition = competitions[0]
        competition["date"] = "1111-11-11 11:11:11"
        response = client.post(self.route, data={'competition': competition['name'], 'club': club['name'], 'places': '10'})
        assert response.status_code == 200
        assert b"You cannot book on a past competition." in response.data
        assert int(club['points']) == 10
        assert int(competition['numberOfPlaces']) == 15
    
    def test_cannot_purchase_more_places_than_left_in_competition(self, client, clubs, competitions):
        club = clubs[0]
        competition = competitions[0]
        competition["numberOfPlaces"] = "5"
        response = client.post(self.route, data={'competition': competition['name'], 'club': club['name'], 'places': '10'}, follow_redirects=True)
        assert response.status_code == 200
        assert b"You cannot book more places than left in competition." in response.data
        assert int(club['points']) == 10
        assert int(competition['numberOfPlaces']) == 5

class TestBook:
    def test_cannot_access_book_page_for_unknown_club(self, client, clubs, competitions):
        response = client.get(f'/book/{competitions[0]['name']}/TOTO', follow_redirects=True)
        assert response.status_code == 200
        assert b"Your club TOTO does not exist. Please log in." in response.data

    def test_cannot_access_book_page_for_unknown_competition(self, client, clubs, competitions):
        response = client.get(f'/book/TOTO/{clubs[0]['name']}')
        assert response.status_code == 200
        assert b"The competition TOTO does not exist." in response.data

    def test_cannot_access_book_page_for_past_competition(self, client, clubs, competitions):
        competition = competitions[0]
        competition["date"] = "1111-11-11 11:11:11"
        response = client.get(f'/book/{competition['name']}/{clubs[0]['name']}')
        assert response.status_code == 200
        assert b"You cannot book on a past competition." in response.data

class TestPointsBoard:
    def test_points_board(self, client, clubs, competitions):
        response = client.get('/points_board')
        assert response.status_code == 200
