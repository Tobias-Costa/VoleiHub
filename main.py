import os
from flask import Flask, request, redirect, url_for, render_template
from models import db, Usuario


app = Flask(__name__)
# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voleihub.db'

# Inicializa o 'db' com o aplicativo 'app'
db.init_app(app)

# --- Rotas da Aplicação ---

@app.route('/')
def index():
    return "Olá mundo"


if __name__ == '__main__':
    # Cria o banco de dados e as tabelas, se ainda não existirem, dentro do contexto da aplicação
    with app.app_context():
        db.create_all()
    app.run(debug=True)
