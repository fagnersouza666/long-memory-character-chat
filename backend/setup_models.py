#!/usr/bin/env python3
"""
Script para configurar a tabela de modelos e inserir dados de exemplo.
Este script pode ser executado para criar a tabela Model e inserir os modelos padrão.
"""

import asyncio
import os
import sys
from prisma import Prisma

# Adicionar o diretório backend ao path para importar os módulos
sys.path.append(os.path.join(os.path.dirname(__file__)))

async def setup_models():
    """Configura a tabela de modelos e insere dados de exemplo"""
    db = Prisma()
    await db.connect()
    
    try:
        # Verificar se a tabela Model existe tentando buscar um registro
        try:
            model = await db.model.find_first()
            print("Tabela Model já existe no banco de dados.")
        except Exception as e:
            print(f"Erro ao acessar a tabela Model: {e}")
            print("Certifique-se de que a tabela Model foi criada no banco de dados.")
            return
        
        # Verificar se já existem modelos na tabela
        model_count = await db.model.count()
        if model_count > 0:
            print(f"Já existem {model_count} modelos na tabela. Nenhum modelo será inserido.")
            return
        
        # Inserir modelos de exemplo
        models_data = [
            {
                "name": "gpt-5-mini",
                "displayName": "GPT 5 mini",
                "prompt": "Você é um assistente prestativo. Responda de forma clara e concisa, mantendo a personalidade do personagem definido pelo usuário.",
                "isActive": True
            },
            {
                "name": "claude-3-haiku-20240307",
                "displayName": "Claude 3 Haiku",
                "prompt": "Você é um assistente analítico e preciso. Forneça respostas bem estruturadas e logicamente organizadas, mantendo a personalidade do personagem definido pelo usuário.",
                "isActive": True
            },
            {
                "name": "gemini-2.5-flash",
                "displayName": "Gemini 2.5 Flash",
                "prompt": "Você é um assistente criativo e envolvente. Use uma linguagem rica e imaginativa, mantendo a personalidade do personagem definido pelo usuário.",
                "isActive": True
            },
            {
                "name": "gpt-4o-mini",
                "displayName": "GPT 4o mini",
                "prompt": "Você é um assistente equilibrado, combinando criatividade e precisão. Responda de forma informativa e envolvente, mantendo a personalidade do personagem definido pelo usuário.",
                "isActive": True
            },
            {
                "name": "mistralai/Mistral-7B-Instruct-v0.3",
                "displayName": "Mistral 7B Instruct",
                "prompt": "Você é um assistente eficiente e direto. Forneça respostas concisas e úteis, mantendo a personalidade do personagem definido pelo usuário.",
                "isActive": True
            },
            {
                "name": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                "displayName": "Llama 3.3 70B",
                "prompt": "Você é um assistente abrangente e detalhista. Forneça respostas completas e bem fundamentadas, mantendo a personalidade do personagem definido pelo usuário.",
                "isActive": True
            }
        ]
        
        # Inserir os modelos
        for model_data in models_data:
            await db.model.create(data=model_data)
            print(f"Modelo '{model_data['displayName']}' inserido com sucesso.")
        
        print("Todos os modelos foram inseridos com sucesso!")
        
    except Exception as e:
        print(f"Erro ao configurar os modelos: {e}")
    finally:
        await db.disconnect()

if __name__ == "__main__":
    print("Configurando a tabela de modelos...")
    asyncio.run(setup_models())