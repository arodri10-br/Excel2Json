from flask import Blueprint, request, jsonify
import mysql.connector
from database import connect_db

# Criando um Blueprint para a API
xref_bp = Blueprint('xref_api', __name__)

# Rota para buscar todos os dados (GET)
@xref_bp.route('/api/xref_modelo', methods=['GET'])
def get_xref_modelo():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT cod_modelo, cod_tabela, vlr_origem, vlr_destino, param_adic FROM xref_modelo")
    dados = cursor.fetchall()
    conn.close()
    return jsonify(dados)

# Rota para inserir um novo dado (POST)
@xref_bp.route('/api/xref_modelo', methods=['POST'])
def add_xref():
    novo_dado = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO xref_modelo (cod_modelo, cod_tabela, vlr_origem, vlr_destino, param_adic)
        VALUES (%s, %s, %s, %s, %s)
    """, (novo_dado['cod_modelo'], novo_dado['cod_tabela'], novo_dado['vlr_origem'], 
          novo_dado['vlr_destino'], novo_dado['param_adic']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Registro de referência cruzada inserido com sucesso!'})

# Rota para atualizar um dado existente (PUT)
@xref_bp.route('/api/xref_modelo/<cod_modelo>', methods=['PUT'])
def update_xref(cod_modelo):
    dados_atualizados = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE xref_modelo
        SET cod_tabela = %s, vlr_origem = %s, vlr_destino = %s, param_adic = %s
        WHERE cod_modelo = %s
    """, (dados_atualizados['cod_tabela'], dados_atualizados['vlr_origem'], 
          dados_atualizados['vlr_destino'], dados_atualizados['param_adic'], cod_modelo))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Registro de referência cruzada atualizado com sucesso!'})

# Rota para excluir um dado (DELETE)
@xref_bp.route('/api/xref_modelo/<cod_modelo>', methods=['DELETE'])
def delete_xref(cod_modelo):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM xref_modelo WHERE cod_modelo = %s", (cod_modelo,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Registro de referência cruzada excluído com sucesso!'})
