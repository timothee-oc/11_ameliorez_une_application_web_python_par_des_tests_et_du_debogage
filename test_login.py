import pytest
from server import clubs, app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_login_valid_email(client):
    valid_email = clubs[0]["email"]
    response = client.post("/showSummary", data={"email": valid_email})

    assert response.status_code == 200
    assert b"Summary" in response.data

def test_login_invalid_email(client):
    invalid_email = "invalid_email"
    response = client.post("/showSummary", data={"email": invalid_email}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Sorry, that email wasn't found." in response.data