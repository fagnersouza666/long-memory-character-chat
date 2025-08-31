import streamlit as st
from rag_components.rag_agent import RAGAgent
from rag_components.evaluation_manager import EmployeeEvaluation
from rag_components.utils import save_uploaded_file, generate_metadata
from rag_components.auth import AuthManager, User
import os
import pandas as pd


# Page configuration
st.set_page_config(
    page_title="Sistema RAG Empresarial",
    page_icon="🏢",
    layout="wide"
)

# Custom CSS for better UI
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "auth_manager" not in st.session_state:
    st.session_state.auth_manager = AuthManager()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "rag_agent" not in st.session_state:
    st.session_state.rag_agent = RAGAgent()

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# Authentication check
if not st.session_state.authenticated:
    st.title("🏢 Sistema RAG Empresarial - Login")
    
    tab1, tab2 = st.tabs(["Login", "Registro"])
    
    with tab1:
        st.header("Login")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            authenticated, user = st.session_state.auth_manager.authenticate_user(username, password)
            if authenticated:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
    
    with tab2:
        st.header("Registro")
        new_username = st.text_input("Novo Usuário")
        email = st.text_input("Email")
        new_password = st.text_input("Nova Senha", type="password")
        department = st.selectbox("Departamento", ["RH", "Financeiro", "TI", "Marketing", "Operações", "Diretoria"])
        
        if st.button("Registrar"):
            success, message = st.session_state.auth_manager.register_user(
                new_username, email, "employee", department, new_password
            )
            if success:
                st.success(message)
            else:
                st.error(message)
    
    st.stop()

# Title
st.title("🏢 Sistema RAG Empresarial")
st.markdown(f"""
Bem-vindo, **{st.session_state.user.username}** ({st.session_state.user.role})
Este sistema permite gerenciar documentos empresariais e avaliações de funcionários 
com capacidades de busca semântica usando Retrieval-Augmented Generation (RAG).
""")

# Sidebar
with st.sidebar:
    st.header(f"Usuário: {st.session_state.user.username}")
    st.write(f"Departamento: {st.session_state.user.department}")
    st.write(f"Função: {st.session_state.user.role}")
    
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()
    
    st.header("Configurações")
    
    # Model selection
    model_options = {
        "GPT-3.5 Turbo": "gpt-3.5-turbo",
        "GPT-4o Mini": "gpt-4o-mini",
        "Gemini Pro": "gemini-pro",
        "Claude Haiku": "claude-3-haiku-20240307"
    }
    
    selected_model = st.selectbox(
        "Modelo de Linguagem",
        options=list(model_options.keys()),
        index=0
    )
    
    model_name = model_options[selected_model]
    
    if st.button("Atualizar Modelo"):
        st.session_state.rag_agent.set_model(model_name)
        st.success(f"Modelo atualizado para {selected_model}")
    
    # Statistics
    st.subheader("Estatísticas")
    if st.session_state.rag_agent.vector_store:
        doc_count = st.session_state.rag_agent.vector_store.index.ntotal
        st.metric("Documentos Indexados", doc_count)
    else:
        st.metric("Documentos Indexados", 0)
    
    st.metric("Custo Total", f"${st.session_state.rag_agent.total_cost:.5f}")

# Tabs
# Show different tabs based on user role
if st.session_state.user.role == "admin":
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Upload de Documentos", 
        "📄 Gerenciar Documentos", 
        "📊 Avaliações de Funcionários", 
        "🔍 Busca Semântica"
    ])
elif st.session_state.user.role == "manager":
    tab1, tab2, tab3 = st.tabs([
        "📤 Upload de Documentos", 
        "📄 Gerenciar Documentos", 
        "🔍 Busca Semântica"
    ])
else:  # employee
    tab1, tab2 = st.tabs([
        "📤 Upload de Documentos", 
        "🔍 Busca Semântica"
    ])

# Tab 1: Document Upload
with tab1:
    st.header("Upload de Documentos")
    
    # Only admins and managers can upload documents
    if st.session_state.user.role in ["admin", "manager"]:
        # Document type selection
        doc_type = st.selectbox(
            "Tipo de Documento",
            ["Documento Empresarial", "Política", "Relatório", "Manual", "Outro"]
        )
        
        # Department selection
        department = st.selectbox(
            "Departamento",
            ["RH", "Financeiro", "TI", "Marketing", "Operações", "Diretoria", "Outro"]
        )
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Escolha os arquivos para upload",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.subheader("Arquivos Selecionados")
            for uploaded_file in uploaded_files:
                st.write(f"📄 {uploaded_file.name} ({uploaded_file.type})")
            
            # Process files
            if st.button("Processar Documentos"):
                with st.spinner("Processando documentos..."):
                    try:
                        for uploaded_file in uploaded_files:
                            # Save file temporarily
                            file_path = save_uploaded_file(uploaded_file, "docs/company")
                            
                            # Generate metadata
                            metadata = generate_metadata(file_path, {
                                "type": doc_type,
                                "department": department,
                                "uploaded_by": st.session_state.user.username
                            })
                            
                            # Add document to RAG system
                            st.session_state.rag_agent.add_document(file_path, metadata)
                            
                            # Add to session state
                            st.session_state.uploaded_files.append({
                                "name": uploaded_file.name,
                                "path": file_path,
                                "type": doc_type,
                                "department": department
                            })
                        
                        st.success(f"{len(uploaded_files)} documentos processados com sucesso!")
                        
                    except Exception as e:
                        st.error(f"Erro ao processar documentos: {str(e)}")
    else:
        st.info("Apenas administradores e gerentes podem fazer upload de documentos.")

# Tab 2: Document Management
with tab2:
    st.header("Gerenciar Documentos")
    
    # Only admins and managers can manage documents
    if st.session_state.user.role in ["admin", "manager"]:
        if st.session_state.rag_agent.vector_store:
            # Show document statistics
            st.subheader("Estatísticas de Documentos")
            doc_count = st.session_state.rag_agent.vector_store.index.ntotal
            st.write(f"Total de documentos indexados: {doc_count}")
            
            # Show recent uploads
            if st.session_state.uploaded_files:
                st.subheader("Uploads Recentes")
                df = pd.DataFrame(st.session_state.uploaded_files)
                st.dataframe(df)
            else:
                st.info("Nenhum documento foi carregado ainda.")
        else:
            st.info("Nenhum documento foi indexado ainda. Faça upload de documentos na aba 'Upload de Documentos'.")
    else:
        st.info("Apenas administradores e gerentes podem gerenciar documentos.")

# Tab 3: Employee Evaluations
with tab3:
    st.header("Avaliações de Funcionários")
    
    # Only admins and managers can add evaluations
    if st.session_state.user.role in ["admin", "manager"]:
        with st.form("employee_evaluation_form"):
            st.subheader("Adicionar Nova Avaliação")
            
            col1, col2 = st.columns(2)
            
            with col1:
                employee_id = st.text_input("ID do Funcionário")
                evaluator = st.text_input("Avaliador", value=st.session_state.user.username)
                score = st.slider("Nota", 0.0, 10.0, 5.0, 0.5)
            
            with col2:
                period = st.text_input("Período (ex: Q1 2024)")
                department = st.selectbox(
                    "Departamento",
                    ["RH", "Financeiro", "TI", "Marketing", "Operações", "Diretoria", "Outro"]
                )
            
            content = st.text_area("Conteúdo da Avaliação", height=200)
            
            submitted = st.form_submit_button("Adicionar Avaliação")
            
            if submitted:
                if employee_id and evaluator and content:
                    try:
                        # Create evaluation
                        evaluation = EmployeeEvaluation(
                            employee_id=employee_id,
                            evaluator=evaluator,
                            period=period,
                            content=content,
                            score=score,
                            metadata={"department": department}
                        )
                        
                        # Add to RAG system
                        st.session_state.rag_agent.add_evaluation(evaluation)
                        
                        st.success("Avaliação adicionada com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao adicionar avaliação: {str(e)}")
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
        
        # Display existing evaluations
        st.subheader("Avaliações Existentes")
        st.info("As avaliações são adicionadas ao sistema de busca semântica e podem ser consultadas na aba 'Busca Semântica'.")
    else:
        st.info("Apenas administradores e gerentes podem adicionar avaliações de funcionários.")

# Tab 4: Semantic Search
with tab4:
    st.header("Busca Semântica")
    
    query = st.text_input("Digite sua pergunta sobre documentos ou avaliações:")
    
    if st.button("Buscar") and query:
        with st.spinner("Buscando respostas..."):
            try:
                # Query the RAG system
                result = st.session_state.rag_agent.query(query)
                
                # Display answer
                st.subheader("Resposta")
                st.write(result["answer"])
                
                # Display source documents
                if result["source_documents"]:
                    st.subheader("Documentos Fonte")
                    doc_count = 0
                    for i, doc in enumerate(result["source_documents"]):
                        # Check document access based on user role
                        doc_type = doc.metadata.get("type", "")
                        doc_department = doc.metadata.get("department", "")
                        
                        # Admins can see everything
                        can_access = st.session_state.user.role == "admin"
                        
                        # Users can access documents in their department
                        if not can_access and st.session_state.user.department == doc_department:
                            can_access = True
                        
                        # Everyone can access general documents
                        if not can_access and doc_department in ["all", ""]:
                            can_access = True
                        
                        # Special handling for employee evaluations
                        if not can_access and doc_type == "employee_evaluation":
                            # Managers can see evaluations in their department
                            if st.session_state.user.role == "manager" and st.session_state.user.department == doc_department:
                                can_access = True
                            
                            # Users can see their own evaluations
                            employee_id = doc.metadata.get("employee_id", "")
                            if employee_id == st.session_state.user.username:
                                can_access = True
                        
                        if can_access:
                            doc_count += 1
                            with st.expander(f"Documento {doc_count}: {doc.metadata.get('title', 'Sem título')}"):
                                st.write(f"**Tipo:** {doc.metadata.get('type', 'Não especificado')}")
                                st.write(f"**Departamento:** {doc.metadata.get('department', 'Não especificado')}")
                                st.write(f"**Data de Modificação:** {doc.metadata.get('modified_date', 'Não especificada')}")
                                st.write("**Conteúdo:**")
                                st.write(doc.page_content)
                    
                    if doc_count == 0:
                        st.info("Nenhum documento relevante encontrado para seu nível de acesso.")
                else:
                    st.info("Nenhum documento relevante encontrado.")
                    
            except Exception as e:
                st.error(f"Erro ao processar consulta: {str(e)}")
    
    # Example queries
    with st.expander("Exemplos de perguntas"):
        st.write("""
        Aqui estão alguns exemplos de perguntas que você pode fazer:
        - "Quais são as políticas de férias da empresa?"
        - "Como é o processo de onboarding de novos funcionários?"
        - "Quais foram as avaliações do funcionário 123 no último trimestre?"
        - "Quais são os principais objetivos do departamento de TI para este ano?"
        - "Como a empresa lida com feedbacks dos funcionários?"
        """)

# Footer
st.markdown("---")
st.markdown("Sistema RAG Empresarial - Transformando documentos em conhecimento acessível")

# Add a help section
with st.expander("ℹ️ Ajuda e Suporte"):
    st.markdown("""
    ### Como usar este sistema:
    
    1. **Upload de Documentos**: Apenas administradores e gerentes podem fazer upload de documentos.
    2. **Busca Semântica**: Todos os usuários podem fazer perguntas sobre documentos e avaliações.
    3. **Avaliações de Funcionários**: Apenas administradores e gerentes podem adicionar avaliações.
    
    ### Tipos de perguntas que você pode fazer:
    
    - "Quais são as políticas de férias da empresa?"
    - "Como é o processo de onboarding de novos funcionários?"
    - "Quais foram as avaliações do funcionário [ID] no último trimestre?"
    - "Quais são os principais objetivos do departamento de [NOME] para este ano?"
    
    ### Precisa de ajuda?
    
    Entre em contato com o administrador do sistema ou com o departamento de TI.
    """)