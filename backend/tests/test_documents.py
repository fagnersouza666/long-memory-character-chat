import pytest
from fastapi.testclient import TestClient
import io

def test_upload_document(test_client, create_test_user):
    """Teste de upload de documento"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Criar um arquivo de teste
    test_file = io.BytesIO("Conteúdo de teste para o documento".encode("utf-8"))
    test_file.name = "test_document.txt"
    
    response = test_client.post(
        "/api/v1/documents/",
        files={"file": (test_file.name, test_file, "text/plain")},
        data={"title": "Test Document"},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Document"
    assert data["fileType"] == "text/plain"

def test_list_documents(test_client, create_test_user):
    """Teste de listagem de documentos"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Upload de um documento de teste
    test_file = io.BytesIO("Conteúdo de teste para o documento".encode("utf-8"))
    test_file.name = "test_document.txt"
    
    test_client.post(
        "/api/v1/documents/",
        files={"file": (test_file.name, test_file, "text/plain")},
        data={"title": "Test Document"},
        headers=headers
    )
    
    # Listar documentos
    response = test_client.get("/api/v1/documents/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_document(test_client, create_test_user):
    """Teste de obtenção de documento específico"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Upload de um documento de teste
    test_file = io.BytesIO("Conteúdo de teste para o documento".encode("utf-8"))
    test_file.name = "test_document.txt"
    
    upload_response = test_client.post(
        "/api/v1/documents/",
        files={"file": (test_file.name, test_file, "text/plain")},
        data={"title": "Test Document"},
        headers=headers
    )
    
    assert upload_response.status_code == 200
    document_id = upload_response.json()["id"]
    
    # Obter documento
    response = test_client.get(f"/api/v1/documents/{document_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == document_id
    assert data["title"] == "Test Document"

def test_update_document(test_client, create_test_user):
    """Teste de atualização de documento"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Upload de um documento de teste
    test_file = io.BytesIO("Conteúdo de teste para o documento".encode("utf-8"))
    test_file.name = "test_document.txt"
    
    upload_response = test_client.post(
        "/api/v1/documents/",
        files={"file": (test_file.name, test_file, "text/plain")},
        data={"title": "Test Document"},
        headers=headers
    )
    
    assert upload_response.status_code == 200
    document_id = upload_response.json()["id"]
    
    # Atualizar documento
    response = test_client.put(
        f"/api/v1/documents/{document_id}",
        json={"title": "Updated Test Document"},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Test Document"

def test_delete_document(test_client, create_test_user):
    """Teste de exclusão de documento"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Upload de um documento de teste
    test_file = io.BytesIO("Conteúdo de teste para o documento".encode("utf-8"))
    test_file.name = "test_document.txt"
    
    upload_response = test_client.post(
        "/api/v1/documents/",
        files={"file": (test_file.name, test_file, "text/plain")},
        data={"title": "Test Document"},
        headers=headers
    )
    
    assert upload_response.status_code == 200
    document_id = upload_response.json()["id"]
    
    # Excluir documento
    response = test_client.delete(f"/api/v1/documents/{document_id}", headers=headers)
    
    assert response.status_code == 200
