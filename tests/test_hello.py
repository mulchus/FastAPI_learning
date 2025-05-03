import pytest


def test_hello_world(pytest_client):
    response = pytest_client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


@pytest.mark.parametrize(
    "name, response_status, message",
    [
        ("Vasya", 200, {"message": "Hello, Vasya"}),
        ("Vasya-2", 400, {"detail": "Name must be in regex ^[a-zA-Zа-яА-Я]{2,30}$"}),
        ("V", 400, {"detail": "Name must be in regex ^[a-zA-Zа-яА-Я]{2,30}$"}),
        ("V"*31, 400, {"detail": "Name must be in regex ^[a-zA-Zа-яА-Я]{2,30}$"}),
    ],
)
def test_hello_name(pytest_client, name, response_status, message):
    response = pytest_client.get(f"/hello/{name}")
    assert response.status_code == response_status
    assert response.json() == message
