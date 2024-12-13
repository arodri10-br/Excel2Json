from flask import Blueprint, request, jsonify
import mysql.connector
from database import connect_db
from datetime import datetime

# Criando um Blueprint para a API
erros_bp = Blueprint('erros_api', __name__)

# Rota para buscar dados da tabela log_processamento com filtro de data (GET)
@erros_bp.route('/api/log_processamento', methods=['GET'])
def get_log_processamento():
    filtro_dia = request.args.get('filtro') == 'dia'
    filtro_mes = request.args.get('filtro') == 'mes'
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM log_processamento"
    params = []
    
    # Adiciona filtro de data, se especificado
    if filtro_dia:
        query += " WHERE DATE(data_inicio) = %s"
        params.append( datetime.strptime(request.args['valorInicio'], "%Y-%m-%d" ) )
    elif filtro_mes:
        query += " WHERE data_inicio >= %s And DATE(data_inicio) <= %s"
        params.append( datetime.strptime(request.args['valorInicio'], "%Y-%m-%d" ) )
        params.append( datetime.strptime(request.args['valorFim'], "%Y-%m-%d" ) )
    
    query += " ORDER BY data_inicio DESC"
    cursor.execute(query, params)
    dados = cursor.fetchall()
    conn.close()
    return jsonify(dados)

# Rota para buscar erros da tabela log_erros com base no id_log (GET)
@erros_bp.route('/api/log_erros/<int:id_log>', methods=['GET'])
def get_log_erros(id_log):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_erro, mensagem_erro, data_erro FROM log_erros WHERE id_log = %s", (id_log,))
    dados = cursor.fetchall()
    conn.close()
    return jsonify(dados)

# Rota para inserir novo registro de log_processamento (POST)
@erros_bp.route('/api/log_processamento', methods=['POST'])
def add_log_processamento():
    novo_log = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO log_processamento (arquivo, data_inicio, data_fim, status, mensagem, iduser)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (novo_log['arquivo'], novo_log['data_inicio'], novo_log['data_fim'], 
          novo_log['status'], novo_log['mensagem'], novo_log['iduser']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Registro de log de processamento inserido com sucesso!'})

# Rota para inserir novo erro na tabela log_erros (POST)
@erros_bp.route('/api/log_erros', methods=['POST'])
def add_log_erro():
    novo_erro = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO log_erros (id_log, mensagem_erro, data_erro)
        VALUES (%s, %s, %s)
    """, (novo_erro['id_log'], novo_erro['mensagem_erro'], novo_erro['data_erro']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Registro de erro inserido com sucesso!'})

# Rota para atualizar um log de processamento existente (PUT)
@erros_bp.route('/api/log_processamento/<int:id_log>', methods=['PUT'])
def update_log_processamento(id_log):
    dados_atualizados = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE log_processamento
        SET arquivo = %s, data_fim = %s, status = %s, mensagem = %s, iduser = %s
        WHERE id_log = %s
    """, (dados_atualizados['arquivo'], dados_atualizados['data_fim'], dados_atualizados['status'],
          dados_atualizados['mensagem'], dados_atualizados['iduser'], id_log))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Registro de log de processamento atualizado com sucesso!'})

# Rota para excluir um log de processamento (DELETE)
@erros_bp.route('/api/log_processamento/<int:id_log>', methods=['DELETE'])
def delete_log_processamento(id_log):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_processamento WHERE id_log = %s", (id_log,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Registro de log de processamento excluído com sucesso!'})
