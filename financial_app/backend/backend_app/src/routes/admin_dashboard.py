from flask import Blueprint, render_template_string, jsonify, request
from flask_jwt_extended import create_access_token
import os

admin_dashboard_bp = Blueprint("admin_dashboard_bp", __name__)

# HTML Template para o Dashboard
ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Clean Database</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            width: 100%;
            padding: 40px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 30px;
        }
        
        button {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-login {
            background: #667eea;
            color: white;
        }
        
        .btn-login:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-login:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-clean {
            background: #ef4444;
            color: white;
        }
        
        .btn-clean:hover {
            background: #dc2626;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(239, 68, 68, 0.3);
        }
        
        .btn-clean:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-logout {
            background: #f3f4f6;
            color: #666;
        }
        
        .btn-logout:hover {
            background: #e5e7eb;
        }
        
        .alert {
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 14px;
            display: none;
        }
        
        .alert-success {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #6ee7b7;
            display: block;
        }
        
        .alert-error {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fca5a5;
            display: block;
        }
        
        .alert-warning {
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #fcd34d;
            display: block;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .spinner {
            border: 3px solid #f3f4f6;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .status {
            margin-top: 20px;
            padding: 15px;
            background: #f9fafb;
            border-radius: 6px;
            font-size: 12px;
            color: #666;
        }
        
        .hidden {
            display: none !important;
        }
        
        .form-hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Admin Dashboard</h1>
        <p class="subtitle">Gerenciador de Banco de Dados</p>
        
        <div id="alert" class="alert"></div>
        
        <div id="loadingSpinner" class="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px; color: #666;">Processando...</p>
        </div>
        
        <!-- Login Form -->
        <div id="loginForm">
            <div class="form-group">
                <label for="username">Usuário</label>
                <input type="text" id="username" placeholder="Digite seu usuário">
            </div>
            
            <div class="form-group">
                <label for="password">Senha</label>
                <input type="password" id="password" placeholder="Digite sua senha">
            </div>
            
            <button class="btn-login" onclick="handleLogin()">Fazer Login</button>
        </div>
        
        <!-- Clean Database Form -->
        <div id="cleanForm" class="form-hidden">
            <div class="form-group">
                <label for="apiKey">Chave de API (Secret Key)</label>
                <input type="password" id="apiKey" placeholder="Cole a chave de API aqui">
            </div>
            
            <div class="button-group">
                <button class="btn-clean" onclick="handleCleanDatabase()">🗑️ Limpar Banco</button>
                <button class="btn-logout" onclick="handleLogout()">Sair</button>
            </div>
        </div>
        
        <div id="status" class="status hidden">
            <strong>Status:</strong> <span id="statusText">-</span>
        </div>
    </div>
    
    <script>
        const API_URL = '/api';
        
        // Verifica se já há token no localStorage ao carregar
        document.addEventListener('DOMContentLoaded', function() {
            const token = localStorage.getItem('admin_token');
            if (token) {
                showCleanForm();
            } else {
                showLoginForm();
            }
        });
        
        function showAlert(message, type) {
            const alertEl = document.getElementById('alert');
            alertEl.textContent = message;
            alertEl.className = `alert alert-${type}`;
            
            // Auto-hide success messages after 5 seconds
            if (type === 'success') {
                setTimeout(() => {
                    alertEl.className = 'alert';
                }, 5000);
            }
        }
        
        function showLoading(show = true) {
            document.getElementById('loadingSpinner').style.display = show ? 'block' : 'none';
        }
        
        function showLoginForm() {
            document.getElementById('loginForm').classList.remove('form-hidden');
            document.getElementById('cleanForm').classList.add('form-hidden');
            document.getElementById('alert').className = 'alert';
        }
        
        function showCleanForm() {
            document.getElementById('loginForm').classList.add('form-hidden');
            document.getElementById('cleanForm').classList.remove('form-hidden');
            document.getElementById('alert').className = 'alert';
        }
        
        function handleLogin() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            if (!username || !password) {
                showAlert('⚠️ Por favor, preencha usuário e senha', 'warning');
                return;
            }
            
            showLoading(true);
            
            fetch(`${API_URL}/admin/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            })
            .then(response => response.json())
            .then(data => {
                showLoading(false);
                
                if (data.access_token) {
                    localStorage.setItem('admin_token', data.access_token);
                    showAlert('✅ Login realizado com sucesso!', 'success');
                    
                    // Clear form
                    document.getElementById('username').value = '';
                    document.getElementById('password').value = '';
                    
                    // Show clean form after 1 second
                    setTimeout(() => showCleanForm(), 1000);
                } else {
                    showAlert(`❌ Erro: ${data.message || 'Falha no login'}`, 'error');
                }
            })
            .catch(error => {
                showLoading(false);
                showAlert(`❌ Erro de conexão: ${error.message}`, 'error');
            });
        }
        
        function handleCleanDatabase() {
            const apiKey = document.getElementById('apiKey').value;
            const token = localStorage.getItem('admin_token');
            
            if (!apiKey) {
                showAlert('⚠️ Por favor, insira a chave de API', 'warning');
                return;
            }
            
            if (!token) {
                showAlert('❌ Sessão expirada. Por favor, faça login novamente', 'error');
                showLoginForm();
                return;
            }
            
            // Confirm action
            const confirmClean = confirm(
                '⚠️ ATENÇÃO!\\n\\nVocê está prestes a limpar TODO o banco de dados.\\n' +
                'Todas as tabelas serão recriadas e os dados serão perdidos.\\n\\n' +
                'Tem certeza que deseja continuar?'
            );
            
            if (!confirmClean) {
                return;
            }
            
            showLoading(true);
            updateStatus('Limpando banco de dados...');
            
            fetch(`${API_URL}/admin/clean-database`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'X-API-KEY': apiKey
                }
            })
            .then(response => response.json())
            .then(data => {
                showLoading(false);
                
                if (data.message) {
                    updateStatus(`Completado: ${data.message}`);
                    showAlert(`✅ ${data.message}`, 'success');
                } else {
                    updateStatus('Sucesso');
                    showAlert('✅ Banco de dados limpado com sucesso!', 'success');
                }
            })
            .catch(error => {
                showLoading(false);
                const errorMsg = error.message || 'Erro desconhecido';
                updateStatus(`Erro: ${errorMsg}`);
                showAlert(`❌ Erro: ${errorMsg}`, 'error');
            });
        }
        
        function handleLogout() {
            localStorage.removeItem('admin_token');
            document.getElementById('apiKey').value = '';
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
            document.getElementById('alert').className = 'alert';
            document.getElementById('status').classList.add('hidden');
            showLoginForm();
            showAlert('✅ Logout realizado com sucesso', 'success');
        }
        
        function updateStatus(message) {
            document.getElementById('status').classList.remove('hidden');
            document.getElementById('statusText').textContent = message;
        }
        
        // Allow Enter key for login
        document.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                if (!document.getElementById('loginForm').classList.contains('form-hidden')) {
                    handleLogin();
                }
            }
        });
    </script>
</body>
</html>
"""

@admin_dashboard_bp.route("/admin/dashboard", methods=["GET"])
def admin_dashboard():
    """Serve the admin dashboard page for clean database operations."""
    return render_template_string(ADMIN_DASHBOARD_HTML)
