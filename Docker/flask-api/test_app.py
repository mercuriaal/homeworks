import pytest

import app as tested_app


@pytest.fixture
def client():
    tested_app.app.config['TESTING'] = True
    app = tested_app.app.test_client()
    return app


def test_post(client):
    response = client.post('/')
    assert response.status_code == 404
