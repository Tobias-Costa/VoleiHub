import os
from flask import Flask, request, redirect, url_for, render_template
from flask_migrate import Migrate
from models import *


app = Flask(__name__)
# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voleihub.db'
# Inicializa o 'db' e as migrações com o aplicativo 'app'
db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True) 

# --- Rotas da Aplicação ---

@app.route('/')
def index():
    return redirect(url_for("home"))

@app.route('/home')
def home():

    total_projetos_ativos = db.session.query(Projeto).filter_by(is_active=True).count()
    total_equipes_ativas = db.session.query(Equipe).filter_by(is_active=True).count()
    total_atletas = db.session.query(Atleta).count()

    # Status Atletas
    id_status_ativo = db.session.query(Status.id).filter_by(nome_status="ativo").scalar()
    id_status_lesionado = db.session.query(Status.id).filter_by(nome_status="lesionado").scalar()
    id_status_suspenso = db.session.query(Status.id).filter_by(nome_status="suspenso").scalar()

    atletas_ativos = db.session.query(Atleta).filter_by(status_id=id_status_ativo).count()
    atletas_lesionados = db.session.query(Atleta).filter_by(status_id=id_status_lesionado).count()
    atletas_suspensos = db.session.query(Atleta).filter_by(status_id=id_status_suspenso).count()

    # Atividades recentes(transferências)
    transferencias = []
    for transferencia in db.session.query(Transferencia).order_by(Transferencia.id.desc()).limit(5).all():

        proj_origem = db.session.query(Projeto.nome_projeto).filter_by(id=transferencia.projeto_origem_id).scalar()

        eq_origem = db.session.query(Equipe.nome_equipe).filter_by(id=transferencia.equipe_origem_id).scalar()

        proj_destino = db.session.query(Projeto.nome_projeto).filter_by(id=transferencia.projeto_destino_id).scalar()

        eq_destino = db.session.query(Equipe.nome_equipe).filter_by(id=transferencia.equipe_destino_id).scalar()

        atleta = db.session.query(Atleta.firstname_atleta).filter_by(id=transferencia.atleta_id).scalar()

        responsavel = db.session.query(Usuario.firstname_usuario).filter_by(id=transferencia.responsavel_id).scalar()

        transferencias.append({"id":transferencia.id, "proj_origem":proj_origem, "eq_origem":eq_origem, "proj_destino":proj_destino, "eq_destino":eq_destino, "nome_atleta":atleta, "responsavel":responsavel})

    # Tabela projetos
    lista_projetos = db.session.query(Projeto).all()
    projetos = []
    for projeto in lista_projetos:
        projeto_cidade = db.session.query(Cidade.nome_cidade).filter_by(id=projeto.cidade_id).scalar()

        projeto_equipes = db.session.query(Equipe).filter_by(projeto_id=projeto.id).count()

        projeto_atletas = db.session.query(Atleta).join(Equipe, Equipe.id == Atleta.equipe_id).filter(Equipe.projeto_id == projeto.id).count()

        projetos.append({"id":projeto.id, "nome":projeto.nome_projeto, "cidade":projeto_cidade, "n_equipes":projeto_equipes, "n_atletas":projeto_atletas, "is_active":bool(projeto.is_active)})
        

    return render_template('dashboard.html', n_projetos_ativos=total_projetos_ativos, n_equipes_ativas=total_equipes_ativas, n_atletas=total_atletas, atletas_ativos=atletas_ativos, atletas_lesionados=atletas_lesionados, atletas_suspensos=atletas_suspensos, transferencias=transferencias, projetos=projetos )

@app.route('/criar/projeto', methods=["GET","POST"])
def criar_projeto():
    return render_template('criar_projeto.html')

@app.route('/criar/equipe', methods=["GET","POST"])
def criar_equipe():
    return render_template('criar_equipe.html')

@app.route('/criar/atleta', methods=["GET","POST"])
def criar_atleta():
    return render_template('criar_atleta.html')


if __name__ == '__main__':
    # Cria o banco de dados e as tabelas, se ainda não existirem, dentro do contexto da aplicação
    with app.app_context():
        db.create_all()
    app.run(debug=True)
