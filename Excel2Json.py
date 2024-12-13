from flask import Flask, request, jsonify
import pandas as pd
import os
import configparser
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import json
import requests
from flask import Blueprint

import cx_Oracle #pip install cx_Oracle
app = Flask(__name__)
cursor = None

Excel2Json_bp = Blueprint('Excel2Json', __name__)

# Lendo o arquivo .ini
config = configparser.ConfigParser()

# Verifica se o arquivo foi lido com sucesso
config_file_path = os.path.join(os.path.dirname(__file__), 'Excel2Json.ini')
if not config.read(config_file_path):
    raise FileNotFoundError("Arquivo de configuracao 'Excel2Json.ini' nao encontrado.")

dbtype = config['DATABASE']['dbtype']

# Conexao com o banco de dados
def create_connection():
    global dbtype
    global cursor
    connection = None
    try:
        # Obtendo as configuracoes do banco de dados do arquivo .ini
        host = config['DATABASE']['host']
        user = config['DATABASE']['user']
        password = config['DATABASE']['password']
        dbname = config['DATABASE']['dbname']
        port = config['DATABASE'].getint('port')
        # Estabelecendo a conexao com o banco de dados
        if dbtype == 'mysql':
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=dbname
            )
        elif dbtype == 'oracle':
            #dsn = cx_Oracle.makedsn(host, port, service_name=dbname)
            dsn=dbname # deve ter a entrada no tnsnames com o parametro que esta no arquivo .ini
            connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
        else:
            raise ValueError("Tipo de banco de dados nao suportado.")
        print("Conexao com o banco de dados realizada com sucesso.")
    except Error as e:
        print(f"Erro: '{e}'")
    return connection
#
# Gravar log de processamento e mensagem de erro
# Obrigatorio somente o nome do arquivo e a conexao
# Retorna o ID_LOG somente quando ele não recebe esse dado e ai ele inclui um registro de processamento
#
def GravaMensagem(connection, ID_LOG, ARQUIVO, DATA_INICIO, DATA_FIM, STATUS, MENSAGEM, IDUSER, detalhe):
    global dbtype
    global cursor

    query = ""
    result = ""
    if not ARQUIVO:
        raise ValueError("O campo ARQUIVO é obrigatório.")
    
    if not connection:
        raise ValueError("O campo connection é obrigatório.")

    if ID_LOG is None:
        # Inserir novo registro em LOG_PROCESSAMENTO
        if dbtype == 'mysql':
            query = f"INSERT INTO log_processamento (arquivo, data_inicio, status, mensagem) VALUES ('{ARQUIVO}', now(), 'P','Arquivo em Processamento.')"
        elif dbtype == 'oracle':
            query = f"INSERT INTO log_processamento (arquivo, data_inicio, status, mensagem) VALUES ('{ARQUIVO}', sysdate, 'P','Arquivo em Processamento.')"
        #print(f"Query de inclusao : {query}")    
        cursor.execute(query)
        result = cursor.lastrowid
    else:
        # Atualizar registro existente em LOG_PROCESSAMENTO
        query = "UPDATE log_processamento SET"
        if STATUS == 'E' or STATUS == 'S':
            if dbtype == 'mysql':
                query = f"{query} STATUS = '{STATUS}', DATA_FIM = now(),"
            elif dbtype == 'oracle':
                query = f"{query} STATUS = '{STATUS}', DATA_FIM = sysdate,"
        if MENSAGEM is not None:
            query = f"{query} MENSAGEM = '{MENSAGEM},'"

        # retirar a virgula ao final da query.
        query = query.rstrip(',')

        if dbtype == 'mysql':
            query = f"{query} Where id_log = '{ID_LOG}'"
        elif dbtype == 'oracle':
            query = f"{query} Where rowid = '{ID_LOG}'"

        cursor.execute(query)
    
    if detalhe:
        # Buscar o campo de ID da tabela de cabeçalho de erro
        if dbtype == 'mysql':
            query = f"SELECT id_log FROM log_processamento Where id_log = '{ID_LOG}'"
        elif dbtype == 'oracle':
            query = f"SELECT id_log FROM log_processamento Where rowid = '{ID_LOG}'"
        cursor.execute(query)
        resultado = cursor.fetchone()
        pk_tabela = resultado if resultado else None

        # Inserir novo registro em LOG_ERROS
        if dbtype == 'mysql':
            query = f"INSERT INTO log_erros ( ID_LOG,MENSAGEM_ERRO,DATA_ERRO) values ({pk_tabela[0]}, '{detalhe.replace("'",'')}', now() )"
        elif dbtype == 'oracle':
            query = f"INSERT INTO log_erros ( ID_LOG,MENSAGEM_ERRO,DATA_ERRO) values ({pk_tabela[0]}, '{detalhe.replace("'",'')}', sysdate )"
        cursor.execute(query)
    
    # Confirmar as alterações
    connection.commit()
    return result

def grava_controle_chamada(connection, id_endpoint, dados_chamada, status_chamada, mensagem_erro=None, codigo_erro=None, tentativas=0, reprocessar=False):
    global dbtype
    global cursor

    insert_query = """
    INSERT INTO api_chamada_controle (id_endpoint, dados_chamada, status_chamada, mensagem_erro, codigo_erro, tentativas, reprocessar, data_sucesso)
    VALUES (:1, :2, :3, :4, :5, :6, :7, :8)
    """
    data_sucesso = datetime.now() if status_chamada == 'SUCESSO' else None
    cursor.execute(insert_query, (id_endpoint, json.dumps(dados_chamada), status_chamada, mensagem_erro, codigo_erro, tentativas, reprocessar, data_sucesso))
    connection.commit()

    #print(f" grava_controle_chamada => id_endpoint : {id_endpoint}, dados_chamada : {dados_chamada} status_chamada, : {status_chamada} mensagem_erro : {mensagem_erro}, codigo_erro, : {codigo_erro} tentativas : {tentativas}, reprocessar : {tentativas}")

    
#
# Funcoes de apoio para fazer a macro substituição indicada na tabela dmodelo
#
########################################################################################
# Função simples de substr, sempre considerando a varialvel que esta em processamento
# Sempre cadastrar o uso do campo pela variavel "valor", exemplo : substr(valor,7,14)
########################################################################################
#
def substr(string, start, length):
    return string[start-1:start-1+length]

#
########################################################################################
# Função de busca da referencia cruzada do atributo, eventualmente ele pode possuir
# parametros adicionais que devem ser agregados na lista, sendo assim essa função 
# devolve um dicionario com valor convertido, os parametros adicionais e uma mensagem
# com a informação "OK" e quando diferente disso, sera a mensagem de erro 
########################################################################################
#
def xRefModelo(cod_modelo, cod_tabela, chave ):
    global cursor
    retorno = {}
    query = f"Select VLR_DESTINO, PARAM_ADIC From XREF_MODELO Where COD_MODELO = '{cod_modelo}' And COD_TABELA = '{cod_tabela}' And VLR_ORIGEM = '{chave}'"
    cursor.execute(query)
    resultado = cursor.fetchone()
    if resultado:
        #print(f"Resultado ==================> {resultado}")
        retorno['status'] = 'OK'
        retorno['mensagem'] = 'Operação realizada com sucesso'
        retorno['valor'], retorno['parametros'] = resultado
        #print(f"Retorno ==================> {retorno}")
    else:
        retorno['status'] = 'Erro'
        retorno['mensagem'] = f"Referencia Modelo : {cod_modelo}, Tabela : {cod_tabela} e Chave : {chave} Não encontrada!"
        retorno['valor'] = None
        retorno['parametros'] = None
    #print(f"Retorno da função xRef : {retorno}")    
    return retorno
#

@Excel2Json_bp.route('/api/Excel2Json', methods=['POST'])
def excel_to_json():
    global cursor
    global config_file_path

    start_time = datetime.now()
    CallAPI_url = ""
    CallAPI_Metodo = ""
    Call_APIId = ""

    arquivo = request.json.get('arquivo')
    cod_modelo = request.json.get('cod_modelo')

    connection = create_connection()

    # Registrar inicio do processamento
    cursor = connection.cursor()
    #query = f"INSERT INTO log_processamento (arquivo, data_inicio, status) VALUES ('{arquivo}', sysdate, 'P')"
    #cursor.execute(query)
    #log_id = cursor.lastrowid
    #connection.commit()
    #log_id = GravaMensagem(connection, none, arquivo, DATA_INICIO, DATA_FIM, STATUS, MENSAGEM, IDUSER, detalhe)
    log_id = GravaMensagem(connection, None , arquivo, None, None, None, None, None, None)
    #print(f"Log ID Gerado pela mensagem : {log_id}")    
    # Verifica se o arquivo existe
    input_folder = config['PATHS']['input_folder']
    file_path = os.path.join(input_folder, arquivo)
    #print(file_path)
    if not os.path.isfile(file_path):
        #query = f"UPDATE log_processamento SET status = 'E', mensagem = 'Arquivo nao encontrado.' WHERE rowid = '{log_id}'"
        #cursor.execute(query)
        #connection.commit()
        msgerro = f"Arquivo : {file_path} Não Encontrado !"
        GravaMensagem(connection, log_id, arquivo, None, None, 'E', 'Arquivo não encontrado', 1, msgerro)
        return jsonify({'status': 'error', 'message': 'Arquivo nao encontrado.'}), 404

    # Ler o arquivo Excel
    df = pd.read_excel(file_path, sheet_name=None) # Le todas as planilhas

    # Obtendo as colunas validas do banco de dados
    query = f"SELECT T1.campoOrigem, T1.campoDestino, T1.tpValidacao, T1.PermiteBranco, T1.fnformato FROM dmodelo T1 WHERE T1.cod_modelo = '{cod_modelo}'"
    #print(query)
    cursor.execute(query)
    colunas_validas = cursor.fetchall()
    #print(colunas_validas)

    # Verificar se sera chamado o processo para envio dos dados por API
    query = f"SELECT concat(url_base, endpoint) AS url, metodo, a.id_endpoint FROM hmodelo a INNER JOIN api_endpoints b ON b.id = a.id_endpoint INNER JOIN api_conexao c ON c.id = b.id_conexao WHERE cod_modelo = '{cod_modelo}'"
    cursor.execute(query)
    result = cursor.fetchone()
    #print(f"Controle de API : {result} ")
    CallAPI_url, CallAPI_Metodo, Call_APIId = result
    #print(f"URL : {CallAPI_url} Metodo : {CallAPI_Metodo} Id : {Call_APIId} ")

    # Processa somente a primeira sheet em busca da linha de Cabecalho
    # O arquivo deve ser aberto considerando sempre a "primeira" linha como cabecao
    # Caso contrario, nao faz a conversao das colunas !
    resultados = {}
    for sheet_name, data in df.items():
        header_row = None
        for index, row in data.iterrows():
            for coluna in colunas_validas:
                if any(item in row.values for item in coluna if item is not None):
                    header_row = index
                    break

    if header_row is None:
        msgerro = f"Arquivo : {arquivo} Não Possue cabecalho !"
        GravaMensagem(connection, log_id, arquivo, None, None, 'E', 'Erro Formatacao do arquivo.', 1, msgerro)
        return jsonify({'status': 'error', 'message': msgerro}), 404

    # Ler a planilha, especificando que o cabeçalho está na linha 6 (index 5)
    df = pd.read_excel(file_path, header=header_row+1)  
    # Criar um dicionário para armazenar os dados simplificados
    dados_simplificados = []
    # Iterar sobre as linhas do DataFrame
    for _, row in df.iterrows():
        # Criar um dicionario para cada linha
        entrada = {}
        grava_linha = True
        for coluna_validada in colunas_validas:
            nome_padronizado = coluna_validada[1] 
            valor = row[coluna_validada[0]] if coluna_validada[0] in df.columns else None
            # Nao permitir a gravacao de dados quando o atributo esta marcado como Nao permite brancos e vem sem dados na planilha
            if (coluna_validada[3] == 'N' and ( pd.isna(valor)  or pd.isnull(valor)) ):
                grava_linha = False
            elif coluna_validada[4]:
                try:
                    msgEval = eval(coluna_validada[4])
                    #print(f"Resultado da formula {coluna_validada[4]}, tipo {type(msgEval)} Resultado => {msgEval}")
                    if isinstance(msgEval, dict):
                        try:
                            if msgEval['status'] == 'OK':
                                valor = msgEval['valor']
                                if msgEval['parametros']:
                                    var_add_dict = json.loads(f'{{{msgEval['parametros']}}}')
                                    entrada.update(var_add_dict)
                                    #print(f"var_add_dict ===== {var_add_dict}")
                            else:
                                valor = None
                        except Exception as strErro:
                            msgerro = f"Nao foi possivel gravar o registro : ({entrada}, devido a erro na referencia cruzada, {msgEval['mensagem']})"
                            grava_linha = False
                            GravaMensagem(connection, log_id, arquivo, None, None, 'E', 'Erro de conversao de cadastro.', 1, msgerro)
                    else:
                        valor = msgEval

                    #print("***************************************************************")
                    #print(f"Resultado da validação do campo {valor} para a Função {coluna_validada[4]} " )
                    #print(f"{type(msgEval)}")
                    #print("***************************************************************")
                except Exception as strErro:
                    msgerro = f"Nao foi possivel gravar o registro : ({entrada}, devido a erro de conversao do cadastro, err: {strErro})"
                    grava_linha = False
                    GravaMensagem(connection, log_id, arquivo, None, None, 'E', 'Erro de conversao de cadastro.', 1, msgerro)
            if grava_linha:
                entrada[nome_padronizado] = valor

            #print( f"valor : [{valor}] com o Tipo : [{type(valor)}]" )
            #print("***************************************************************")
            #print( f"coluna_validada 0 : {coluna_validada[0]}" ) # Coluna De
            #print( f"coluna_validada 1 : {coluna_validada[1]}" ) # Coluna Para
            #print( f"coluna_validada 2 : {coluna_validada[2]}" ) # Tipo do dado
            #print( f"coluna_validada 3 : {coluna_validada[3]}" ) # Permite Branco
            #print( f"coluna_validada 4 : {coluna_validada[4]}" ) # Funcao para Validacao
            #print("***************************************************************")
            #print( f"valor : {valor}" )
            #print("***************************************************************")
        if grava_linha:
            # se os dados aqui, estiverem Ok, proceder a gravacao no array
            dados_simplificados.append(entrada)

            # se devidamente configurado, fazer a chamada da API
            if CallAPI_url:
                try:
                    if CallAPI_Metodo.upper() == 'GET':
                        response = requests.get(CallAPI_url, params=entrada)
                    elif CallAPI_Metodo.upper() == 'POST':
                        response = requests.post(CallAPI_url, json=entrada)
                    else:
                        GravaMensagem(connection, log_id, arquivo, None, None, 'E', 'Erro no envio dos dados para API.', 1, f"Metodo {CallAPI_Metodo} nao suportado.")
                    # Verificar o resultado da chamada da API 
                    if response.status_code == 200:
                        print(f"Chamada da API {CallAPI_url} realizada com sucesso.")
                        grava_controle_chamada(connection,Call_APIId, entrada, 'SUCESSO')
                    else:
                        msgerro = f"Erro na chamada da API: {response.text}"
                        GravaMensagem(connection, log_id, arquivo, None, None, 'E', None, 1, "Erro na chamada da API, verifique tabela de log de envio.")
                        grava_controle_chamada(connection,Call_APIId, entrada, 'ERRO',msgerro)
                except Exception as strErro:
                    msgerro = f"Exception na chamada da API: {strErro}"
                    GravaMensagem(connection, log_id, arquivo, None, None, 'E', None, 1, msgerro)
                    grava_controle_chamada(connection,Call_APIId, entrada, 'ERRO',msgerro)
        else:
            msgerro = f"Nao foi possivel gravar o registro : ({entrada}, devido a inconsistencias de pelo menos uma coluna)"
            GravaMensagem(connection, log_id, arquivo, None, None, 'E', 'Arquivo possui registros invalidos.', 1, msgerro)
                

    # Salvar o dicionário como um arquivo JSON
    json_file_name = os.path.splitext(arquivo)[0] + '.json'
    json_file_path = os.path.join(config['PATHS']['backup_folder'], json_file_name)

    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(dados_simplificados, json_file, ensure_ascii=False, indent=4)

    # Atualizar log_processamento com sucesso
    end_time = datetime.now()
    query = f"UPDATE log_processamento SET data_fim = sysdate, status = 'S' WHERE rowid = '{log_id}'"
    #print(query)
    cursor.execute(query) 
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({'status': 'success', 'message': 'Processamento concluido com sucesso.'}), 200

if __name__ == '__main__':
    app.run(debug=True)
