import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

@pytest.fixture
def test_client():
    """Fixture para o cliente de teste"""
    return TestClient(app)

@pytest.fixture
def unique_id():
    """Fixture para gerar um ID único para testes"""
    return str(uuid.uuid4())[:8]

@pytest.fixture
def create_test_user(test_client, unique_id):
    """Fixture para criar um usuário de teste"""
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    password = "testpassword"
    
    # Registrar usuário
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "role": "employee",
            "department": "IT"
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {
            "username": username,
            "email": email,
            "password": password,
            "token": token
        }
    else:
        return None

@pytest.fixture
def create_test_admin(test_client, unique_id):
    """Fixture para criar um administrador de teste"""
    username = f"testadmin_{unique_id}"
    email = f"testadmin_{unique_id}@example.com"
    password = "testpassword"
    
    # Registrar administrador
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "role": "admin",
            "department": "IT"
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {
            "username": username,
            "email": email,
            "password": password,
            "token": token
        }
    else:
        return None