import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_register_user():
    """Teste de registro de usuário"""
    # Gerar um nome de usuário e email únicos para cada teste
    unique_id = str(uuid.uuid4())[:8]
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "testpassword",
            "role": "employee",
            "department": "IT"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_user():
    """Teste de login de usuário"""
    # Gerar um nome de usuário e email únicos para cada teste
    unique_id = str(uuid.uuid4())[:8]
    
    # Primeiro registrar um usuário
    client.post(
        "/api/v1/auth/register",
        json={
            "username": f"testuser2_{unique_id}",
            "email": f"test2_{unique_id}@example.com",
            "password": "testpassword",
            "role": "employee",
            "department": "IT"
        }
    )
    
    # Depois fazer login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": f"testuser2_{unique_id}",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_invalid_login():
    """Teste de login inválido"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistentuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401