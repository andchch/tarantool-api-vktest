import pytest
from fastapi.testclient import TestClient
from main import app
from auth import create_access_token
from datetime import timedelta

client = TestClient(app)

# Тестовые данные
test_user = {
    "username": "admin",
    "password": "presale"
}


def test_login_success():
    # Тест на успешную авторизацию
    username = test_user['username']
    password = test_user['password']

    response = client.post(f"/api/login?username={username}&password={password}")
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_failure():
    # Тест на неудачную авторизацию (неверный пароль)
    wrong_username = 'vova'
    wrong_password = 'qwerty'

    response = client.post(f"/api/login?username={wrong_username}&password={wrong_password}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}


@pytest.fixture(scope="module")
def access_token():
    # Создаем JWT токен для тестирования защищенных эндпоинтов
    return create_access_token({"sub": "admin"}, expires_delta=timedelta(minutes=30))


def test_write_values_success(access_token):
    # Тест на успешную запись данных
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "1": "test1",
        "2": "test2"
    }
    response = client.post("/api/write?space=data", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}


def test_write_values_partial_success(access_token):
    # Тест на частичный успех (некоторые ключи уже существуют)
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {  # Ключ 1 уже существует
        "data": {
            "1": "value1",
            "3": "value3"
        }
    }
    response = client.post("/api/write?space=data", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "status": "partial success",
        "info": "key(s) already exists",
        "duplicated keys": {"1": "Key already exists"},
        "success": {"3": "successfully written"}
    }


def test_write_values_schema_error(access_token):
    # Тест на ошибку неверное пространство
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "data": {
            "1": "value1"
        }
    }
    response = client.post("/api/write?space=nodata", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "There is no space with name nodata"}


def test_read_values_success(access_token):
    # Тест на успешное чтение данных
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "keys": [1, 3],
    }
    response = client.post("/api/read?space=data", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "data": {"1": "value1", "3": "value3"}
    }


def test_read_values_partial_success(access_token):
    # Тест на частичный успех при чтении данных (некоторые ключи отсутствуют)
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "keys": [1, 2, 4],  # Ключ 4 отсутствует
    }
    response = client.post("/api/read?space=data", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "status": "partial success",
        "info": "missing keys are in request",
        "missing keys": {"4": "No such key in database"},
        "data": {"1": "value1", "2": "value2"}
    }


def test_read_values_schema_error(access_token):
    # Тест на неверное пространство
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "keys": [1],
    }
    response = client.post("/api/read?space=nodata", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "There is no space with name nodata"}
