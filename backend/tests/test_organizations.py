import pytest
from fastapi.testclient import TestClient

def test_create_organization(test_client, create_test_admin):
    """Teste de criação de organização"""
    if not create_test_admin:
        pytest.fail("Falha ao criar usuário administrador de teste")
    
    headers = {"Authorization": f"Bearer {create_test_admin['token']}"}
    
    response = test_client.post(
        "/api/v1/organizations/",
        json={"name": "Test Organization"},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Organization"

def test_create_organization_non_admin(test_client, create_test_user):
    """Teste de tentativa de criação de organização por não administrador"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    response = test_client.post(
        "/api/v1/organizations/",
        json={"name": "Test Organization"},
        headers=headers
    )
    
    assert response.status_code == 403

def test_list_organizations(test_client, create_test_admin):
    """Teste de listagem de organizações"""
    if not create_test_admin:
        pytest.fail("Falha ao criar usuário administrador de teste")
    
    headers = {"Authorization": f"Bearer {create_test_admin['token']}"}
    
    # Criar uma organização primeiro
    test_client.post(
        "/api/v1/organizations/",
        json={"name": "Test Organization"},
        headers=headers
    )
    
    # Listar organizações
    response = test_client.get("/api/v1/organizations/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_organization(test_client, create_test_admin):
    """Teste de obtenção de organização específica"""
    if not create_test_admin:
        pytest.fail("Falha ao criar usuário administrador de teste")
    
    headers = {"Authorization": f"Bearer {create_test_admin['token']}"}
    
    # Criar uma organização
    create_response = test_client.post(
        "/api/v1/organizations/",
        json={"name": "Test Organization"},
        headers=headers
    )
    
    assert create_response.status_code == 200
    org_id = create_response.json()["id"]
    
    # Obter a organização
    response = test_client.get(f"/api/v1/organizations/{org_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == org_id
    assert data["name"] == "Test Organization"