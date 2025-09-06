import pytest
from fastapi.testclient import TestClient

def test_create_evaluation(test_client, create_test_admin, create_test_user):
    """Teste de criação de avaliação"""
    if not create_test_admin or not create_test_user:
        pytest.fail("Falha ao criar usuários de teste")
    
    headers = {"Authorization": f"Bearer {create_test_admin['token']}"}
    
    # Criar uma avaliação
    response = test_client.post(
        "/api/v1/evaluations/",
        json={
            "employeeId": 2,  # ID do usuário de teste
            "period": "Q3 2025",
            "content": "Excelente desempenho neste trimestre",
            "score": 9.5
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["employeeId"] == 2
    assert data["period"] == "Q3 2025"
    assert data["score"] == 9.5

def test_create_evaluation_non_manager(test_client, create_test_user):
    """Teste de tentativa de criação de avaliação por não gerente"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Tentar criar uma avaliação
    response = test_client.post(
        "/api/v1/evaluations/",
        json={
            "employeeId": 1,
            "period": "Q3 2025",
            "content": "Avaliação de teste",
            "score": 8.0
        },
        headers=headers
    )
    
    assert response.status_code == 403

def test_list_evaluations(test_client, create_test_admin):
    """Teste de listagem de avaliações"""
    if not create_test_admin:
        pytest.fail("Falha ao criar usuário administrador de teste")
    
    headers = {"Authorization": f"Bearer {create_test_admin['token']}"}
    
    # Listar avaliações
    response = test_client.get("/api/v1/evaluations/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_evaluation(test_client, create_test_admin):
    """Teste de obtenção de avaliação específica"""
    if not create_test_admin:
        pytest.fail("Falha ao criar usuário administrador de teste")
    
    headers = {"Authorization": f"Bearer {create_test_admin['token']}"}
    
    # Criar uma avaliação
    create_response = test_client.post(
        "/api/v1/evaluations/",
        json={
            "employeeId": 2,
            "period": "Q3 2025",
            "content": "Excelente desempenho neste trimestre",
            "score": 9.5
        },
        headers=headers
    )
    
    assert create_response.status_code == 200
    evaluation_id = create_response.json()["id"]
    
    # Obter a avaliação
    response = test_client.get(f"/api/v1/evaluations/{evaluation_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == evaluation_id
    assert data["period"] == "Q3 2025"