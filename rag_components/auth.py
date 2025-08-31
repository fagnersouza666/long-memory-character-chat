import streamlit as st
import hashlib
import os
import json
from datetime import datetime, timedelta


class User:
    """User class for authentication"""
    
    def __init__(self, username, email, role, department, password_hash=None):
        self.username = username
        self.email = email
        self.role = role  # admin, manager, employee
        self.department = department
        self.password_hash = password_hash
        self.created_at = datetime.now().isoformat()
        self.last_login = None


class AuthManager:
    """Manage user authentication and access control"""
    
    def __init__(self, users_file="users.json"):
        self.users_file = users_file
        self.users = self.load_users()
        self.setup_admin_user()
    
    def load_users(self):
        """Load users from file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                    users = {}
                    for username, data in users_data.items():
                        user = User(
                            username=data['username'],
                            email=data['email'],
                            role=data['role'],
                            department=data['department'],
                            password_hash=data['password_hash']
                        )
                        user.created_at = data.get('created_at', datetime.now().isoformat())
                        user.last_login = data.get('last_login')
                        users[username] = user
                    return users
            except Exception as e:
                print(f"Error loading users: {e}")
                return {}
        return {}
    
    def save_users(self):
        """Save users to file"""
        users_data = {}
        for username, user in self.users.items():
            users_data[username] = {
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'department': user.department,
                'password_hash': user.password_hash,
                'created_at': user.created_at,
                'last_login': user.last_login
            }
        
        try:
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def hash_password(self, password):
        """Hash a password for storing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, password_hash):
        """Verify a password against its hash"""
        return self.hash_password(password) == password_hash
    
    def setup_admin_user(self):
        """Setup default admin user if none exists"""
        if not self.users:
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            admin_user = User(
                username="admin",
                email="admin@company.com",
                role="admin",
                department="IT",
                password_hash=self.hash_password(admin_password)
            )
            self.users["admin"] = admin_user
            self.save_users()
    
    def register_user(self, username, email, role, department, password):
        """Register a new user"""
        if username in self.users:
            return False, "Username already exists"
        
        user = User(
            username=username,
            email=email,
            role=role,
            department=department,
            password_hash=self.hash_password(password)
        )
        
        self.users[username] = user
        self.save_users()
        return True, "User registered successfully"
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        if username not in self.users:
            return False, None
        
        user = self.users[username]
        if self.verify_password(password, user.password_hash):
            user.last_login = datetime.now().isoformat()
            self.save_users()
            return True, user
        
        return False, None
    
    def get_user(self, username):
        """Get user by username"""
        return self.users.get(username)
    
    def update_user_role(self, username, new_role):
        """Update user role (admin only)"""
        if username in self.users:
            self.users[username].role = new_role
            self.save_users()
            return True
        return False
    
    def delete_user(self, username):
        """Delete a user (admin only)"""
        if username in self.users and username != "admin":
            del self.users[username]
            self.save_users()
            return True
        return False


def require_authentication():
    """Decorator to require authentication for functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if "authenticated" not in st.session_state or not st.session_state.authenticated:
                st.warning("Você precisa estar autenticado para acessar esta função.")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator


def check_document_access(user, document_metadata):
    """Check if user has access to a document"""
    # Admins can access everything
    if user.role == "admin":
        return True
    
    # Check department access
    doc_department = document_metadata.get("department")
    if doc_department and user.department != doc_department and doc_department != "all":
        return False
    
    # Check role-based access
    doc_role = document_metadata.get("access_role")
    if doc_role and doc_role != "all":
        role_hierarchy = ["employee", "manager", "admin"]
        user_role_index = role_hierarchy.index(user.role) if user.role in role_hierarchy else 0
        required_role_index = role_hierarchy.index(doc_role) if doc_role in role_hierarchy else 0
        
        if user_role_index < required_role_index:
            return False
    
    return True


def check_evaluation_access(user, evaluation):
    """Check if user has access to an evaluation"""
    # Admins can access everything
    if user.role == "admin":
        return True
    
    # Users can access their own evaluations
    if hasattr(evaluation, 'employee_id') and user.username == evaluation.employee_id:
        return True
    
    # Managers can access evaluations in their department
    if user.role == "manager" and hasattr(evaluation, 'metadata'):
        eval_department = evaluation.metadata.get("department")
        if eval_department and user.department == eval_department:
            return True
    
    return False