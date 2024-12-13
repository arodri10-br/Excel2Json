from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import hashlib
import configparser
from database import connect_db  # Importa a função connect_db
from werkzeug.security import check_password_hash  # Importa check_password_hash
from api_tpdados import tpdados_bp
from api_usuarios import usuarios_bp
from api_modelos import modelos_bp
from api_conexoes import conexoes_bp
from api_xref import xref_bp
from api_upload import upload_bp
from api_upload import upload_bp
from Excel2Json import Excel2Json_bp
from api_consulta_erros import erros_bp

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Mantenha essa chave em segredo

# Array contendo as informações da sidebar
sidebar_items = [
    {'name': 'Upload de Arquivos', 'url': '/upload'},
    {'name': 'Consulta de Erros', 'url': '/consulta_erros'},
    {'name': 'Dashboard de Erros', 'url': '/dashboard_erros'},
    {'name': 'Consulta Controle API', 'url': '/consulta_api_log'},
    {'name': 'Conexões API', 'url': '/conexoes'},
    {'name': 'Modelos', 'url': '/modelos'},
    {'name': 'Referencia Cruzada', 'url': '/xref'},
    {'name': 'Tipos de Dados', 'url': '/tipos_dados'},
    {'name': 'Man. Usuários', 'url': '/usuarios'},
    {'name': 'Logout', 'url': '/logout'}
]

# Registrando o blueprint da API de tpdados
app.register_blueprint(tpdados_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(modelos_bp)
app.register_blueprint(conexoes_bp)
app.register_blueprint(xref_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(Excel2Json_bp)
app.register_blueprint(erros_bp)

from flask import session
import mysql.connector

def verificar_login(email, senha):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, email, status, perfil, senha FROM sys_users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    if user and check_password_hash(user['senha'], senha):  # Verifique a senha criptografada
        return user
    return False


@app.route('/')
def index():
    return redirect('/login')  # Redireciona para a página de login

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        usuario = verificar_login(email, senha)
        if usuario:
            if usuario['status'] != "A":
                error = 'Usuário inativo ou bloqueado.'
            else:
                # Armazena os dados do usuario na sessão
                session['usuario_email']  = email  
                session['usuario_nome']   = usuario['nome']  
                session['usuario_perfil'] = usuario['perfil']
                session['sidebar_items'] = sidebar_items
                return redirect('/home')  # Redireciona após login bem-sucedido
        else:
            error = 'Usuário ou senha inválidos.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', sidebar_items=sidebar_items,
                       usuario_nome=session.get('usuario_nome'), 
                       usuario_email=session.get('usuario_email'), 
                       usuario_perfil=session.get('usuario_perfil'))

@app.route('/usuarios')
def usuarios():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    return render_template('usuarios.html', sidebar_items=sidebar_items,
                       usuario_nome=session.get('usuario_nome'), 
                       usuario_email=session.get('usuario_email'), 
                       usuario_perfil=session.get('usuario_perfil'))

@app.route('/tipos_dados')
def tipos_dados():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    return render_template('tipos_dados.html', sidebar_items=sidebar_items,
                       usuario_nome=session.get('usuario_nome'), 
                       usuario_email=session.get('usuario_email'), 
                       usuario_perfil=session.get('usuario_perfil'))

@app.route('/modelos')
def modelos():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    return render_template('modelos.html', sidebar_items=sidebar_items,
                       usuario_nome=session.get('usuario_nome'), 
                       usuario_email=session.get('usuario_email'), 
                       usuario_perfil=session.get('usuario_perfil'))

@app.route('/conexoes')
def conexoes():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    return render_template('conexoes.html', sidebar_items=sidebar_items,
                       usuario_nome=session.get('usuario_nome'), 
                       usuario_email=session.get('usuario_email'), 
                       usuario_perfil=session.get('usuario_perfil'))

@app.route('/xref')
def xref():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    return render_template('xref.html', sidebar_items=sidebar_items,
                       usuario_nome=session.get('usuario_nome'), 
                       usuario_email=session.get('usuario_email'), 
                       usuario_perfil=session.get('usuario_perfil'))

@app.route('/upload')
def upload():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    return render_template('upload.html', sidebar_items=sidebar_items,
                       usuario_nome=session.get('usuario_nome'), 
                       usuario_email=session.get('usuario_email'), 
                       usuario_perfil=session.get('usuario_perfil'))

@app.route('/consulta_erros')
def consulta_erros():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    return render_template('consulta_erros.html', sidebar_items=sidebar_items,
                       usuario_nome=session.get('usuario_nome'), 
                       usuario_email=session.get('usuario_email'), 
                       usuario_perfil=session.get('usuario_perfil'))

@app.errorhandler(404)
def page_not_found(e):
    return "Página não encontrada", 404

if __name__ == '__main__':
    app.run(debug=True)
