import streamlit as st
import requests
import pandas as pd
import json
from typing import List, Optional
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="Second Brain System",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS para melhorar a UI
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e0e0e0;
    }
    .st-emotion-cache-16idsys p {
        font-size: 18px;
    }
    .reportview-container {
        background: linear-gradient(to right, #f5f7fa, #c3cfe2);
    }
    .css-1d391kg {
        background-color: #f5f7fa;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado da sessão
if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "user" not in st.session_state:
    st.session_state.user = None

if "current_organization" not in st.session_state:
    st.session_state.current_organization = None

if "current_workspace" not in st.session_state:
    st.session_state.current_workspace = None

# Configuração da API
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

def make_api_request(method: str, endpoint: str, data: dict = None, files: dict = None):
    """Fazer requisição à API com tratamento de autenticação"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    if st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, files=files, data=data)
            else:
                response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        response.raise_for_status()
        return response.json() if response.content else None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na requisição à API: {str(e)}")
        return None

def login(username: str, password: str):
    """Realizar login do usuário"""
    data = {
        "username": username,
        "password": password
    }
    
    response = make_api_request("POST", "/auth/login", data)
    if response:
        st.session_state.access_token = response["access_token"]
        # Obter informações do usuário
        user_info = make_api_request("GET", "/users/me")
        if user_info:
            st.session_state.user = user_info
        return True
    return False

def register(username: str, email: str, password: str):
    """Registrar novo usuário"""
    data = {
        "username": username,
        "email": email,
        "password": password,
        "role": "employee"
    }
    
    response = make_api_request("POST", "/auth/register", data)
    if response:
        st.session_state.access_token = response["access_token"]
        # Obter informações do usuário
        user_info = make_api_request("GET", "/users/me")
        if user_info:
            st.session_state.user = user_info
        return True
    return False

def logout():
    """Realizar logout do usuário"""
    st.session_state.access_token = None
    st.session_state.user = None
    st.session_state.current_organization = None
    st.session_state.current_workspace = None

def get_organizations():
    """Obter organizações do usuário"""
    return make_api_request("GET", "/organizations/")

def get_workspaces(organization_id: int):
    """Obter workspaces de uma organização"""
    return make_api_request("GET", f"/workspaces/?organization_id={organization_id}")

def upload_document(file, title: str, workspace_id: int = None, tags: str = None):
    """Fazer upload de documento"""
    files = {"file": file}
    data = {
        "title": title,
        "workspace_id": workspace_id,
        "tags": tags
    }
    
    return make_api_request("POST", "/documents/", data=data, files=files)

def search_content(query: str, search_type: str = "semantic", workspace_id: int = None):
    """Buscar conteúdo"""
    data = {
        "query": query,
        "search_type": search_type,
        "workspace_id": workspace_id
    }
    
    return make_api_request("POST", "/search/", data)

# Página de autenticação
if not st.session_state.access_token:
    st.title("🧠 Second Brain System")
    st.markdown("Seu segundo cérebro digital para gerenciamento de conhecimento")
    
    tab1, tab2 = st.tabs(["Login", "Registro"])
    
    with tab1:
        st.header("Login")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            if login(username, password):
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
    
    with tab2:
        st.header("Registro")
        new_username = st.text_input("Novo Usuário")
        email = st.text_input("Email")
        new_password = st.text_input("Nova Senha", type="password")
        
        if st.button("Registrar"):
            if register(new_username, email, new_password):
                st.success("Registro realizado com sucesso!")
                st.rerun()
            else:
                st.error("Erro no registro")
    
    st.stop()

# Barra lateral
with st.sidebar:
    st.header(f"Olá, {st.session_state.user['username']}!")
    
    # Informações do usuário
    st.subheader("Perfil")
    st.write(f"**Papel:** {st.session_state.user['role']}")
    if st.session_state.user.get('department'):
        st.write(f"**Departamento:** {st.session_state.user['department']}")
    
    # Seleção de organização/workspace
    organizations = get_organizations()
    if organizations:
        org_names = [org["name"] for org in organizations]
        selected_org = st.selectbox("Organização", org_names)
        
        # Encontrar ID da organização selecionada
        selected_org_id = None
        for org in organizations:
            if org["name"] == selected_org:
                selected_org_id = org["id"]
                break
        
        if selected_org_id:
            st.session_state.current_organization = selected_org_id
            
            # Seleção de workspace
            workspaces = get_workspaces(selected_org_id)
            if workspaces:
                workspace_names = [ws["name"] for ws in workspaces]
                workspace_names.insert(0, "Todos")  # Opção para todos os workspaces
                selected_workspace = st.selectbox("Workspace", workspace_names)
                
                # Encontrar ID do workspace selecionado
                selected_workspace_id = None
                if selected_workspace != "Todos":
                    for ws in workspaces:
                        if ws["name"] == selected_workspace:
                            selected_workspace_id = ws["id"]
                            break
                
                st.session_state.current_workspace = selected_workspace_id
    
    # Botão de logout
    if st.button("Logout"):
        logout()
        st.rerun()

# Conteúdo principal
st.title("🧠 Second Brain System")
st.markdown(f"Bem-vindo ao seu segundo cérebro digital, **{st.session_state.user['username']}**!")

# Tabs principais
tab_names = ["Dashboard", "Documentos", "Avaliações", "Busca", "Configurações"]
tabs = st.tabs(tab_names)

# Dashboard
with tabs[0]:
    st.header("Dashboard")
    st.markdown("Visão geral do seu conhecimento")
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documentos", "128", "12")
    
    with col2:
        st.metric("Avaliações", "24", "3")
    
    with col3:
        st.metric("Workspaces", "5", "1")
    
    # Atividade recente
    st.subheader("Atividade Recente")
    recent_activity = [
        {"ação": "Documento adicionado", "item": "Relatório Q2 2025", "tempo": "2 horas atrás"},
        {"ação": "Avaliação criada", "item": "Avaliação João Silva", "tempo": "1 dia atrás"},
        {"ação": "Documento atualizado", "item": "Política de Férias", "tempo": "3 dias atrás"}
    ]
    
    for activity in recent_activity:
        st.markdown(f"- **{activity['ação']}**: {activity['item']} ({activity['tempo']})")

# Documentos
with tabs[1]:
    st.header("Gerenciamento de Documentos")
    
    # Upload de documentos
    st.subheader("Upload de Documento")
    uploaded_file = st.file_uploader("Escolha um arquivo", type=["pdf", "docx", "txt"])
    
    if uploaded_file:
        title = st.text_input("Título do Documento", value=uploaded_file.name)
        tags = st.text_input("Tags (separadas por vírgula)")
        
        if st.button("Fazer Upload"):
            with st.spinner("Fazendo upload..."):
                result = upload_document(
                    uploaded_file, 
                    title, 
                    st.session_state.current_workspace, 
                    tags
                )
                if result:
                    st.success("Documento adicionado com sucesso!")
                else:
                    st.error("Erro ao fazer upload do documento")
    
    # Listagem de documentos
    st.subheader("Documentos Recentes")
    # Esta seria uma chamada real à API para obter documentos
    # documents = make_api_request("GET", "/documents/")
    # Para demonstração, criamos dados fictícios
    documents_data = [
        {"title": "Relatório Q2 2025", "type": "PDF", "date": "2025-08-15", "size": "2.4 MB"},
        {"title": "Política de Férias", "type": "DOCX", "date": "2025-08-10", "size": "1.1 MB"},
        {"title": "Plano Estratégico 2025", "type": "PDF", "date": "2025-07-22", "size": "5.2 MB"}
    ]
    
    df = pd.DataFrame(documents_data)
    st.dataframe(df, use_container_width=True)

# Avaliações
with tabs[2]:
    st.header("Avaliações de Equipe")
    
    # Criar nova avaliação
    st.subheader("Nova Avaliação")
    with st.form("new_evaluation"):
        employee_id = st.text_input("ID do Funcionário")
        period = st.text_input("Período", "Q3 2025")
        score = st.slider("Pontuação", 0.0, 10.0, 5.0, 0.5)
        content = st.text_area("Conteúdo da Avaliação", height=200)
        
        submitted = st.form_submit_button("Criar Avaliação")
        if submitted:
            st.success("Avaliação criada com sucesso!")
    
    # Listagem de avaliações
    st.subheader("Avaliações Recentes")
    # Esta seria uma chamada real à API para obter avaliações
    # evaluations = make_api_request("GET", "/evaluations/")
    # Para demonstração, criamos dados fictícios
    evaluations_data = [
        {"employee": "João Silva", "period": "Q2 2025", "score": 8.5, "date": "2025-08-20"},
        {"employee": "Maria Santos", "period": "Q2 2025", "score": 9.2, "date": "2025-08-18"},
        {"employee": "Pedro Costa", "period": "Q2 2025", "score": 7.8, "date": "2025-08-15"}
    ]
    
    df_eval = pd.DataFrame(evaluations_data)
    st.dataframe(df_eval, use_container_width=True)

# Busca
with tabs[3]:
    st.header("Busca Semântica")
    
    # Interface de busca
    query = st.text_input("O que você está procurando?")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        search_type = st.selectbox("Tipo de Busca", ["semantic", "keyword", "hybrid"])
    with col2:
        limit = st.number_input("Limite de Resultados", min_value=1, max_value=50, value=10)
    with col3:
        st.write("")  # Espaço vazio para alinhamento
    
    if st.button("Buscar") and query:
        with st.spinner("Buscando..."):
            results = search_content(
                query, 
                search_type, 
                st.session_state.current_workspace
            )
            
            if results and results.get("results"):
                st.subheader(f"Resultados da Busca ({len(results['results'])} encontrados)")
                
                for i, result in enumerate(results["results"]):
                    with st.expander(f"Resultado {i+1}: {result['metadata'].get('document_title', 'Sem título')}"):
                        st.markdown(f"**Tipo:** {result['source_type']}")
                        st.markdown(f"**Relevância:** {result['score']:.2f}")
                        st.markdown(f"**Conteúdo:** {result['content']}")
                        
                        # Mostrar metadados
                        st.markdown("**Metadados:**")
                        for key, value in result["metadata"].items():
                            st.markdown(f"- {key}: {value}")
            else:
                st.info("Nenhum resultado encontrado para sua busca.")

# Configurações
with tabs[4]:
    st.header("Configurações")
    
    # Perfil do usuário
    st.subheader("Perfil")
    with st.form("user_profile"):
        username = st.text_input("Nome de Usuário", value=st.session_state.user["username"])
        email = st.text_input("Email", value=st.session_state.user["email"])
        
        submitted = st.form_submit_button("Atualizar Perfil")
        if submitted:
            st.success("Perfil atualizado com sucesso!")
    
    # Preferências
    st.subheader("Preferências")
    st.selectbox("Idioma", ["Português", "English", "Español"])
    st.checkbox("Notificações por Email", value=True)
    st.checkbox("Modo Escuro", value=False)
    
    # Sobre
    st.subheader("Sobre")
    st.markdown("""
    **Second Brain System** v1.0
    
    Um sistema avançado de gerenciamento de conhecimento que utiliza 
    tecnologia de busca semântica para ajudá-lo a organizar e acessar 
    suas informações de forma inteligente.
    
    Desenvolvido com:
    - Python
    - FastAPI
    - Streamlit
    - PostgreSQL
    - FAISS
    """)

# Rodapé
st.markdown("---")
st.markdown("Second Brain System - Transformando informação em conhecimento")