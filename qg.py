import mysql.connector
import configparser
from werkzeug.security import generate_password_hash

def connect_db():
    config = configparser.ConfigParser()
    config.read('excel2json.ini')  # Lê o arquivo de configuração
    
    db_config = {
        'host': config['DATABASE']['host'],
        'user': config['DATABASE']['user'],
        'password': config['DATABASE']['password'],
        'database': config['DATABASE']['dbname']
    }
    
    return mysql.connector.connect(**db_config)

def cadastrar_usuario(nome, email, senha):
    hashed_password = generate_password_hash(senha)  # Gera o hash da senha
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sys_users (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, hashed_password))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Usuário {nome} cadastrado com sucesso!")

# Cadastrando o usuário
cadastrar_usuario('arodri10', 'algr@uol.com.br', 'carol01')
