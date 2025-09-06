import pytest
from fastapi.testclient import TestClient

def test_create_workspace(test_client, create_test_admin):
    """Teste de criação de workspace"""
    if not create_test_admin:
        pytest.fail("Falha ao criar usuário administrador de teste")
    
    headers = {"Authorization": f"Bearer {create_test_admin['token']}"}
    
    # Primeiro criar uma organização
    org_response = test_client.post(
        "/api/v1/organizations/",
        json={"name": "Test Organization"},
        headers=headers
    )
    
    assert org_response.status_code == 200
    org_id = org_response.json()["id"]
    
    # Criar workspace
    response = test_client.post(
        "/api/v1/workspaces/",
        json={
            "name": "Test Workspace",
            "organizationId": org_id
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Workspace"
    assert data["organizationId"] == org_id

def test_list_workspaces(test_client, create_test_admin):
    """Teste de listagem de workspaces"""
    if not create_test_admin:
        pytest.fail("Falha ao criar usuário administrador de teste")
    
    headers = {"Authorization": f"Bearer {create_test_admin['token']}"}
    
    # Criar organização e workspace
    org_response = test_client.post(
        "/api/v1/organizations/",
        json={"name": "Test Organization"},
        headers=headers
    )
    
    assert org_response.status_code == 200
    org_id = org_response.json()["id"]
    
    test_client.post(
        "/api/v1/workspaces/",
        json={
            "name": "Test Workspace",
            "organizationId": org_id
        },
        headers=headers
    )
    
    # Listar workspaces
    response = test_client.get(
        f"/api/v1/workspaces/?organization_id={org_id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_workspace(test_client, create_test_admin):
    """Teste de obtenção de workspace específico"""
    if not create_test_admin:
        pytest.fail("Falha ao criar usuário administrador de teste")
    
    headers = {"Authorization": f"Bearer {create_test_admin['token']}"}
    
    # Criar organização e workspace
    org_response = test_client.post(
        "/api/v1/organizations/",
        json={"name": "Test Organization"},
        headers=headers
    )
    
    assert org_response.status_code == 200
    org_id = org_response.json()["id"]
    
    workspace_response = test_client.post(
        "/api/v1/workspaces/",
        json={
            "name": "Test Workspace",
            "organizationId": org_id
        },
        headers=headers
    )
    
    assert workspace_response.status_code == 200
    workspace_id = workspace_response.json()["id"]
    
    # Obter workspace
    response = test_client.get(f"/api/v1/workspaces/{workspace_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workspace_id
    assert data["name"] == "Test Workspace"