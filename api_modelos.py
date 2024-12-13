from flask import Blueprint, request, jsonify
import mysql.connector
from database import connect_db

# Criando um Blueprint para a API
modelos_bp = Blueprint('modelos_api', __name__)

# Rota para buscar todos os modelos (GET)
@modelos_bp.route('/api/hmodelos', methods=['GET'])
def get_hmodelos():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT cod_modelo, desc_modelo, id_endpoint, tipo_saida, pasta_saida, tipo_arquivo FROM hmodelo")
    hmodelos = cursor.fetchall()
    conn.close()
    return jsonify(hmodelos)

# Rota para buscar detalhes de um modelo específico (GET)
@modelos_bp.route('/api/dmodelos/<cod_modelo>', methods=['GET'])
def get_dmodelos(cod_modelo):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, cod_modelo, seq, campoOrigem, campoDestino, PermiteBranco, tpValidacao, fnformato FROM dmodelo WHERE cod_modelo = %s", (cod_modelo,))
    dmodelos = cursor.fetchall()
    conn.close()
    return jsonify(dmodelos)

# Rota para inserir um novo modelo (POST)
@modelos_bp.route('/api/hmodelos', methods=['POST'])
def add_hmodelo():
    novo_modelo = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO hmodelo (cod_modelo, desc_modelo, id_endpoint, tipo_saida, pasta_saida, tipo_arquivo)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (novo_modelo['cod_modelo'], novo_modelo['desc_modelo'], novo_modelo['id_endpoint'],
          novo_modelo['tipo_saida'], novo_modelo['pasta_saida'], novo_modelo['tipo_arquivo']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Modelo inserido com sucesso!'})

# Rota para atualizar um modelo existente (PUT)
@modelos_bp.route('/api/hmodelos/<cod_modelo>', methods=['PUT'])
def update_hmodelo(cod_modelo):
    modelo_atualizado = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE hmodelo
        SET desc_modelo = %s, id_endpoint = %s, tipo_saida = %s, pasta_saida = %s, tipo_arquivo = %s
        WHERE cod_modelo = %s
    """, (modelo_atualizado['desc_modelo'], modelo_atualizado['id_endpoint'],
          modelo_atualizado['tipo_saida'], modelo_atualizado['pasta_saida'], modelo_atualizado['tipo_arquivo'], cod_modelo))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Modelo atualizado com sucesso!'})

# Rota para excluir um modelo (DELETE)
@modelos_bp.route('/api/hmodelos/<cod_modelo>', methods=['DELETE'])
def delete_hmodelo(cod_modelo):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM hmodelo WHERE cod_modelo = %s", (cod_modelo,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Modelo excluído com sucesso!'})

# Rota para inserir um novo detalhe (POST)
@modelos_bp.route('/api/dmodelos', methods=['POST'])
def add_dmodelo():
    novo_detalhe = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO dmodelo (cod_modelo, seq, campoOrigem, campoDestino, PermiteBranco, tpValidacao, fnformato)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (novo_detalhe['cod_modelo'], novo_detalhe['seq'], novo_detalhe['campoOrigem'],
          novo_detalhe['campoDestino'], novo_detalhe['PermiteBranco'], novo_detalhe['tpValidacao'],
          novo_detalhe['fnformato']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Detalhe inserido com sucesso!'})

# Rota para atualizar um detalhe existente (PUT)
@modelos_bp.route('/api/dmodelos/<id>', methods=['PUT'])
def update_dmodelo(id):
    detalhe_atualizado = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE dmodelo
        SET cod_modelo = %s, seq = %s, campoOrigem = %s, campoDestino = %s, PermiteBranco = %s, tpValidacao = %s, fnformato = %s
        WHERE id = %s
    """, (detalhe_atualizado['cod_modelo'], detalhe_atualizado['seq'], detalhe_atualizado['campoOrigem'],
          detalhe_atualizado['campoDestino'], detalhe_atualizado['PermiteBranco'], detalhe_atualizado['tpValidacao'],
          detalhe_atualizado['fnformato'], id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Detalhe atualizado com sucesso!'})

# Rota para excluir um detalhe (DELETE)
@modelos_bp.route('/api/dmodelos/<id>', methods=['DELETE'])
def delete_dmodelo(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dmodelo WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Detalhe excluído com sucesso!'})
