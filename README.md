# Excel2Json

## Descrição do Projeto
O **Excel2Json** é uma aplicação desenvolvida para converter dados de planilhas Excel em formatos JSON, permitindo fácil integração com outros sistemas. Além disso, o projeto oferece uma interface web e APIs para gerenciar dados, realizar uploads e realizar operações diversas com os dados processados.

---

## Estrutura do Projeto

### Diretórios principais:

- `app/`: Contém o código-fonte principal da aplicação.
  - `api_*.py`: APIs para diferentes funcionalidades (conexões, modelos, usuários, etc.).
  - `templates/`: Arquivos HTML usados como base para a interface web.
  - `static/`: Arquivos estáticos como CSS e imagens.
  - `Excel2Json.py`: Arquivo principal para iniciar o servidor.

- `db/`: Scripts SQL e definições relacionadas ao banco de dados.
  - `DBInstall.sql`: Script para instalação do banco de dados.
  - `Atualizacoes_*.sql`: Scripts de atualização do banco de dados.

---

## Tecnologias Utilizadas

### Backend:
- Linguagem: Python
- Framework: Flask (provavelmente, dado o uso de APIs e templates HTML)

### Frontend:
- HTML + CSS (templates baseados em Jinja2)

### Banco de Dados:
- MySQL e Oracle (scripts para ambos os sistemas estão disponíveis).

---

## Configuração e Execução

### Pré-requisitos:
- **Python 3.10+**
- Gerenciador de pacotes `pip`
- Servidor de banco de dados MySQL ou Oracle

### Passos:

1. Clone este repositório:
```bash
git clone <URL_DO_REPOSITORIO>
cd Excel2Json
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo `Excel2Json.ini` para ajustar as configurações de banco de dados e outros parâmetros.

4. Execute a aplicação:
```bash
python app/Excel2Json.py
```

5. Acesse a aplicação em: `http://localhost:5000`

---

## Funcionalidades

### APIs:
- **Conexões**: Gerencia conexões de banco de dados.
- **Upload**: Permite o envio de arquivos Excel.
- **Modelos e Tipos de Dados**: Define e gerencia os modelos utilizados para conversão.
- **Usuários**: Gerencia autenticação e permissões de usuários.

### Interface Web:
- Upload de arquivos Excel
- Consulta de erros
- Gerenciamento de usuários e conexões

---

## Scripts de Banco de Dados
- **Instalação**: Use o arquivo `DBInstall.sql` para configurar o banco de dados inicialmente.
- **Atualizações**: Arquivos de atualização são incluídos na pasta `db/` com datas específicas.

---

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature/bugfix:
```bash
git checkout -b minha-feature
```
3. Commit suas alterações:
```bash
git commit -m "Descrição da alteração"
```
4. Envie suas alterações:
```bash
git push origin minha-feature
```
5. Abra um Pull Request

---

## Licença
Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
