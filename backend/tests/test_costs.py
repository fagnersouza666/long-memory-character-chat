import pytest
from fastapi.testclient import TestClient

def test_record_usage(test_client, create_test_admin, create_test_user):
    """Teste de registro de uso"""
    if not create_test_admin or not create_test_user:
        pytest.fail("Falha ao criar usuários de teste")
    
    headers = {"Authorization": f"Bearer {create_test_admin['token']}"}
    
    # Registrar uso
    response = test_client.post(
        "/api/v1/costs/usage/",
        json={
            "userId": 2,  # ID do usuário de teste
            "feature": "document_processing",
            "tokens_used": 1000,
            "cost": 0.005
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["userId"] == 2
    assert data["feature"] == "document_processing"
    assert data["cost"] == 0.005

def test_get_cost_dashboard(test_client, create_test_user):
    """Teste de obtenção do dashboard de custos"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Obter dashboard de custos
    response = test_client.get("/api/v1/costs/dashboard/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "total_cost" in data
    assert "daily_cost" in data
    assert "weekly_cost" in data
    assert "monthly_cost" in data

def test_get_cost_history(test_client, create_test_user):
    """Teste de obtenção do histórico de custos"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Obter histórico de custos
    response = test_client.get("/api/v1/costs/history/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "records" in data
    assert "total_records" in data
    assert "total_cost" in data