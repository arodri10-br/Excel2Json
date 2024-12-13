from flask import Blueprint, request, jsonify
import mysql.connector
from database import connect_db

# Criando um Blueprint para a API
tpdados_bp = Blueprint('tpdados_api', __name__)

# Rota para buscar todos os dados (GET)
@tpdados_bp.route('/api/tipos_dados', methods=['GET'])
def get_tipos_dados():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT tpValidacao, dsValidacao, Vlmin, Vlmax, PermiteBranco, PermiteNegativo FROM tpdados")
    dados = cursor.fetchall()
    conn.close()
    return jsonify(dados)

# Rota para inserir um novo dado (POST)
@tpdados_bp.route('/api/tipos_dados', methods=['POST'])
def add_tipo_dado():
    novo_dado = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tpdados (tpValidacao, dsValidacao, Vlmin, Vlmax, PermiteBranco, PermiteNegativo)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (novo_dado['tpValidacao'], novo_dado['dsValidacao'], novo_dado['Vlmin'], novo_dado['Vlmax'], 
          novo_dado['PermiteBranco'], novo_dado['PermiteNegativo']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Tipo de dado inserido com sucesso!'})

# Rota para atualizar um dado existente (PUT)
@tpdados_bp.route('/api/tipos_dados/<tpValidacao>', methods=['PUT'])
def update_tipo_dado(tpValidacao):
    dados_atualizados = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tpdados
        SET dsValidacao = %s, Vlmin = %s, Vlmax = %s, PermiteBranco = %s, PermiteNegativo = %s
        WHERE tpValidacao = %s
    """, (dados_atualizados['dsValidacao'], dados_atualizados['Vlmin'], dados_atualizados['Vlmax'], 
          dados_atualizados['PermiteBranco'], dados_atualizados['PermiteNegativo'], tpValidacao))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Tipo de dado atualizado com sucesso!'})

# Rota para excluir um dado (DELETE)
@tpdados_bp.route('/api/tipos_dados/<tpValidacao>', methods=['DELETE'])
def delete_tipo_dado(tpValidacao):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tpdados WHERE tpValidacao = %s", (tpValidacao,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Tipo de dado excluído com sucesso!'})
