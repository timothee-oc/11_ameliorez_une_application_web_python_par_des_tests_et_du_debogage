import pytest
from server import app
from unittest.mock import patch

@pytest.fixture
def clubs():
    clubs = [{"name": "CLUB1", "points": 15}]
    with patch('server.clubs', clubs) as mock:
        yield mock 

@pytest.fixture
def competitions():
    competitions = [{"name": "COMP1", "numberOfPlaces": 20}]
    with patch('server.competitions', competitions) as mock:
        yield mock

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_purchase_enough_points(client, clubs, competitions):
    response = client.post(
        "/purchasePlaces", 
        data={
            "competition": "COMP1",
            "club": "CLUB1",
            "places": "10"
        }
    )
    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data
    assert clubs[0]["points"] == 5


def test_purchase_not_enough_points(client, clubs, competitions):
    response = client.post(
        "/purchasePlaces", 
        data={
            "competition": "COMP1",
            "club": "CLUB1",
            "places": "20"
        }
    )
    assert response.status_code == 200
    assert b"You cannot redeeem more points than available." in response.data
    assert clubs[0]["points"] == 15
