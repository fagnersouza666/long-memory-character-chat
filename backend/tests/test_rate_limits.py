import pytest
from fastapi.testclient import TestClient

def test_create_rate_limit(test_client, create_test_admin):
    """Teste de criação de limite de taxa"""
    if not create_test_admin:
        pytest.fail("Falha ao criar usuário administrador de teste")
    
    headers = {"Authorization": f"Bearer {create_test_admin['token']}"}
    
    response = test_client.post(
        "/api/v1/rate-limits/",
        json={
            "feature": "document_upload",
            "limit": 10,
            "window_seconds": 3600
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["feature"] == "document_upload"
    assert data["limit"] == 10

def test_list_rate_limits(test_client, create_test_admin):
    """Teste de listagem de limites de taxa"""
    if not create_test_admin:
        pytest.fail("Falha ao criar usuário administrador de teste")
    
    headers = {"Authorization": f"Bearer {create_test_admin['token']}"}
    
    # Listar limites de taxa
    response = test_client.get("/api/v1/rate-limits/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_rate_limit_status(test_client, create_test_user):
    """Teste de obtenção do status dos limites de taxa"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Obter status dos limites de taxa
    response = test_client.get("/api/v1/rate-limits/status/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Deve haver pelo menos alguns limites de taxa
    assert len(data) > 0