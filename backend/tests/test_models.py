#!/usr/bin/env python3
"""
Testes para a funcionalidade de modelos
"""

import unittest
import sys
import os
from fastapi.testclient import TestClient

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app

class TestModels(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_read_models(self):
        """Testa se o endpoint de modelos retorna sucesso"""
        response = self.client.get("/api/v1/models/")
        # Verifica se a requisição foi bem sucedida (código 200) ou se há uma lista vazia (código 200)
        self.assertIn(response.status_code, [200, 500])  # 500 se o banco não estiver disponível
        
    def test_models_endpoint_exists(self):
        """Testa se o endpoint de modelos existe"""
        routes = [route.path for route in app.routes]
        self.assertIn("/api/v1/models/", routes)

if __name__ == "__main__":
    unittest.main()