from flask import Blueprint, request, jsonify
import mysql.connector
from database import connect_db

# Creating a Blueprint for the API
conexoes_bp = Blueprint('conexoes_api', __name__)

# Route to fetch all connections (GET)
@conexoes_bp.route('/api/conexoes', methods=['GET'])
def get_conexoes():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM api_conexao")
    conexoes = cursor.fetchall()
    conn.close()
    return jsonify(conexoes)

# Route to insert a new connection (POST)
@conexoes_bp.route('/api/conexoes', methods=['POST'])
def add_conexao():
    nova_conexao = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO api_conexao (nome, usuario, senha, tipo_autenticacao, url_base)
        VALUES (%s, %s, %s, %s, %s)
    """, (nova_conexao['nome'], nova_conexao['usuario'], nova_conexao['senha'],
          nova_conexao['tipo_autenticacao'], nova_conexao['url_base']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Conexão inserida com sucesso!'})

# Route to update an existing connection (PUT)
@conexoes_bp.route('/api/conexoes/<int:id>', methods=['PUT'])
def update_conexao(id):
    dados_atualizados = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE api_conexao
        SET nome = %s, usuario = %s, senha = %s, tipo_autenticacao = %s, url_base = %s
        WHERE id = %s
    """, (dados_atualizados['nome'], dados_atualizados['usuario'], dados_atualizados['senha'],
          dados_atualizados['tipo_autenticacao'], dados_atualizados['url_base'], id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Conexão atualizada com sucesso!'})

# Route to delete a connection (DELETE)
@conexoes_bp.route('/api/conexoes/<int:id>', methods=['DELETE'])
def delete_conexao(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM api_conexao WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Conexão excluída com sucesso!'})

# Route to fetch all endpoints for a specific connection (GET)
@conexoes_bp.route('/api/conexoes/<int:id>/endpoints', methods=['GET'])
def get_endpoints(id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM api_endpoints WHERE id_conexao = %s", (id,))
    endpoints = cursor.fetchall()
    conn.close()
    return jsonify(endpoints)

# Route to add a new endpoint (POST)
@conexoes_bp.route('/api/conexoes/<int:id>/endpoints', methods=['POST'])
def add_endpoint(id):
    novo_endpoint = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO api_endpoints (id_conexao, endpoint, metodo, descricao, swagger_url)
        VALUES (%s, %s, %s, %s, %s)
    """, (id, novo_endpoint['endpoint'], novo_endpoint['metodo'],
          novo_endpoint['descricao'], novo_endpoint['swagger_url']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Endpoint inserido com sucesso!'})

# Route to update an existing endpoint (PUT)
@conexoes_bp.route('/api/conexoes/<int:id_conexao>/endpoints/<int:id>', methods=['PUT'])
def update_endpoint(id_conexao, id):
    dados_atualizados = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE api_endpoints
        SET endpoint = %s, metodo = %s, descricao = %s, swagger_url = %s
        WHERE id = %s AND id_conexao = %s
    """, (dados_atualizados['endpoint'], dados_atualizados['metodo'],
          dados_atualizados['descricao'], dados_atualizados['swagger_url'], id, id_conexao))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Endpoint atualizado com sucesso!'})

# Route to delete an endpoint (DELETE)
@conexoes_bp.route('/api/conexoes/<int:id_conexao>/endpoints/<int:id>', methods=['DELETE'])
def delete_endpoint(id_conexao, id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM api_endpoints WHERE id = %s AND id_conexao = %s", (id, id_conexao))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Endpoint excluído com sucesso!'})
