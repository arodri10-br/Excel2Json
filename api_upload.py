from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from database import connect_db
import configparser

# Carregar configurações do arquivo ini
config = configparser.ConfigParser()
config.read('Excel2Json.ini')
UPLOAD_FOLDER = config.get('PATHS', 'input_folder')  # Lê o diretório de upload do arquivo ini
ALLOWED_EXTENSIONS = {'txt', 'csv', 'json', 'xlsx'}  # Extensões permitidas

# Função para verificar se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Criando um Blueprint para a API
upload_bp = Blueprint('upload_api', __name__)

# Rota para upload de arquivos
@upload_bp.route('/api/upload', methods=['POST'])
def upload_file():
    # Verifica se a requisição contém o arquivo
    if 'arquivo' not in request.files:
        return jsonify({'message': 'Nenhum arquivo foi enviado!'}), 400
    
    file = request.files['arquivo']

    # Se o usuário não selecionar um arquivo, o navegador pode enviar um campo vazio sem nome
    if file.filename == '':
        return jsonify({'message': 'Nenhum arquivo selecionado!'}), 400

    # Verifica se o arquivo é permitido
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Verifica se a pasta de upload existe, se não, cria
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        file.save(os.path.join(UPLOAD_FOLDER, filename))  # Salva o arquivo na pasta de upload
        return jsonify({'message': 'Arquivo enviado com sucesso!'}), 200
    else:
        return jsonify({'message': 'Tipo de arquivo não permitido!'}), 400
