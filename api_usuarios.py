from flask import Blueprint, request, jsonify
import mysql.connector
from database import connect_db
from werkzeug.security import generate_password_hash

# Criando um Blueprint para a API
usuarios_bp = Blueprint('usuarios_api', __name__)

def verificar_login(email, senha):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM sys_users WHERE email = %s"
    cursor.execute(query, (email,))
    usuario = cursor.fetchone()

    if usuario and usuario['senha'] == senha:  
        return usuario
    return None

# Rota para buscar todos os usuários (GET)
@usuarios_bp.route('/api/sys_users', methods=['GET'])
def get_users():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT nome, email, senha, telefone, status, perfil FROM sys_users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

# Rota para inserir um novo usuário (POST)
@usuarios_bp.route('/api/sys_users', methods=['POST'])
def add_user():
    novo_usuario = request.json
    hashed_password = generate_password_hash(novo_usuario['senha'])  # Gera o hash da senha
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sys_users (nome, email, senha, telefone, status, perfil)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (novo_usuario['nome'], novo_usuario['email'], hashed_password, novo_usuario['telefone'],
          novo_usuario['status'], novo_usuario['perfil']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Usuário inserido com sucesso!'})

# Rota para atualizar um usuário existente (PUT)
@usuarios_bp.route('/api/sys_users/<email>', methods=['PUT'])
def update_user(email):
    dados_atualizados = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sys_users
        SET nome = %s, senha = %s, telefone = %s, status = %s, perfil = %s
        WHERE email = %s
    """, (dados_atualizados['nome'], dados_atualizados['senha'], dados_atualizados['telefone'],
          dados_atualizados['status'], dados_atualizados['perfil'], email))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Usuário atualizado com sucesso!'})

# Rota para excluir um usuário (DELETE)
@usuarios_bp.route('/api/sys_users/<email>', methods=['DELETE'])
def delete_user(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sys_users WHERE email = %s", (email,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Usuário excluído com sucesso!'})