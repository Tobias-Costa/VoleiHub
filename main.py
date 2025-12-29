import os
from flask import Flask, request, redirect, url_for, render_template
from flask_migrate import Migrate
from datetime import datetime
from models import *

def format_cpf(cpf):
    """Formata um CPF (espera string de 11 dígitos)."""
    if cpf and len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def format_telefone(tel):
    """Formata um telefone (espera string de 10 ou 11 dígitos)."""
    if tel:
        if len(tel) == 11:
            return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
        elif len(tel) == 10:
            return f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
    return tel

def format_rg(rg):
    """Formata um RG (exemplo simples, pode variar por estado)."""
    if rg:
        # Exemplo de formatação simples (XXXXXXXXXX-X)
        if len(rg) >=10:
            return f"{rg[:10]}-{rg[10:]}"
    return rg

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
    # Coloque aqui querys gerais para otimizar o app reduzindo queries
    projetos_query = db.session.query(Projeto)
    equipes_query = db.session.query(Equipe)
    atletas_query = db.session.query(Atleta)
    cidades_query = db.session.query(Cidade)
    id_status_query = db.session.query(Status.id)

    # Painel dashboard
    total_projetos_ativos = projetos_query.filter_by(is_active=True).count()
    total_equipes_ativas = equipes_query.filter_by(is_active=True).count()
    total_atletas = atletas_query.count()

    # Status Atletas
    id_status_ativo = id_status_query.filter_by(nome_status="ativo").scalar()
    id_status_lesionado = id_status_query.filter_by(nome_status="lesionado").scalar()
    id_status_suspenso = id_status_query.filter_by(nome_status="suspenso").scalar()

    atletas_ativos = atletas_query.filter_by(status_id=id_status_ativo).count()
    atletas_lesionados = atletas_query.filter_by(status_id=id_status_lesionado).count()
    atletas_suspensos = atletas_query.filter_by(status_id=id_status_suspenso).count()

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

    ## Lógica para o funcionamento do filtro de projetos
    q = request.args.get("q", "").strip()
    status = request.args.get("status")
    cidade_id = request.args.get("cidade")

    ### Cria cópia de projetos_query
    filtro_query = projetos_query

    if q:
        filtro_query = filtro_query.filter(Projeto.nome_projeto.ilike(f"%{q}%"))

    if status == "ativo":
        filtro_query = filtro_query.filter(Projeto.is_active == True)
    elif status == "inativo":
        filtro_query = filtro_query.filter(Projeto.is_active == False)

    if cidade_id:
        filtro_query = filtro_query.filter(Projeto.cidade_id == cidade_id)

    lista_projetos = filtro_query.all()

    projetos = []
    for projeto in lista_projetos:
        projeto_cidade = cidades_query.filter_by(id=projeto.cidade_id).scalar().nome_cidade
        
        projeto_equipes = equipes_query.filter_by(projeto_id=projeto.id).count()

        projeto_atletas = atletas_query.join(Equipe, Equipe.id == Atleta.equipe_id).filter(Equipe.projeto_id == projeto.id).count()

        projetos.append({"id":projeto.id, "nome":projeto.nome_projeto, "cidade":projeto_cidade, "n_equipes":projeto_equipes, "n_atletas":projeto_atletas, "is_active":bool(projeto.is_active)})


    return render_template('dashboard.html', n_projetos_ativos=total_projetos_ativos, n_equipes_ativas=total_equipes_ativas, n_atletas=total_atletas, atletas_ativos=atletas_ativos, atletas_lesionados=atletas_lesionados, atletas_suspensos=atletas_suspensos, transferencias=transferencias, projetos=projetos, cidades=cidades_query.all())

@app.route('/criar/projeto/', methods=["GET","POST"])
def criar_projeto():
    return render_template('criar_projeto.html')

@app.route('/criar/equipe/', methods=["GET","POST"])
def criar_equipe():
    return render_template('criar_equipe.html')

@app.route('/criar/atleta/', methods=["GET","POST"])
def criar_atleta():
    return render_template('criar_atleta.html')

@app.route('/view/projeto/')
def visualizar_projeto():
    projeto_id = request.args.get('projeto_id')

    # Querys principais para a rota
    projeto = db.session.query(Projeto).filter(Projeto.id == projeto_id).scalar()

    projeto_equipes = db.session.query(Equipe).filter_by(projeto_id=projeto.id)

    projeto_atletas = db.session.query(Atleta).join(Equipe, Equipe.id == Atleta.equipe_id).filter(Equipe.projeto_id == projeto.id)

    cidade = db.session.query(Cidade).filter(Cidade.id == projeto.cidade_id).scalar()

    usuarios_query = db.session.query(Usuario)
    modalidades_query = db.session.query(Modalidade)
    posicoes_query = db.session.query(Posicao)
    categorias_query = db.session.query(Categoria)
    niveis_query = db.session.query(Nivel)
    status_query = db.session.query(Status)

    responsavel = usuarios_query.filter(Usuario.id == projeto.responsavel_id).scalar()

    #Dicionário tabela equipes-projeto
    equipes = []
    for equipe in projeto_equipes:
        tecnico_equipe = usuarios_query.filter(Usuario.id == equipe.tecnico_id).scalar()
        total_atletas = projeto_atletas.filter(Atleta.equipe_id == equipe.id).count()

        equipes.append({"id":equipe.id, "nome_equipe":equipe.nome_equipe,"tecnico":tecnico_equipe.firstname_usuario, "is_active":bool(equipe.is_active),"total_atletas":total_atletas})

    #Dicionário tabela atletas-equipe
    atletas = []
    for atleta in projeto_atletas:
        equipe_atleta = projeto_equipes.filter(Equipe.id == atleta.equipe_id).scalar()

        modalidade_atleta = modalidades_query.filter(Modalidade.id==atleta.modalidade_id).scalar().nome_modalidade

        posicao_atleta = posicoes_query.filter(Posicao.id==atleta.posicao_id).scalar().nome_posicao

        categoria_atleta = categorias_query.filter(Categoria.id==atleta.categorias_id).scalar().nome_categoria

        nivel_atleta = niveis_query.filter(Nivel.id==atleta.nivel_id).scalar().nome_nivel

        status_atleta = status_query.filter(Status.id==atleta.status_id).scalar().nome_status

        atletas.append({"id":atleta.id, "nome_atleta":atleta.firstname_atleta, "equipe":equipe_atleta.nome_equipe, "modalidade":modalidade_atleta, "posicao":posicao_atleta, "categoria":categoria_atleta, "nivel":nivel_atleta, "status":status_atleta})

    return render_template('visualizar_projeto.html', projeto=projeto, cidade=cidade, responsavel=responsavel, data_criacao=datetime.strftime(projeto.created_at,"%d/%m/%Y"), n_equipes=projeto_equipes.count(), n_atletas=projeto_atletas.count(), equipes=equipes, atletas=atletas)

@app.route('/view/equipe/')
def visualizar_equipe():
    equipe_id = request.args.get('equipe_id')

    #Dados da equipe
    equipe = db.session.query(Equipe).filter(Equipe.id==equipe_id).scalar()
    projeto_equipe = db.session.query(Projeto).filter(Projeto.id==equipe.projeto_id).scalar()
    tecnico_equipe = db.session.query(Usuario).filter(Usuario.id==equipe.tecnico_id).scalar()
    tecnico_nome = f"{tecnico_equipe.firstname_usuario} {tecnico_equipe.lastname_usuario}"

    atletas_equipe = Atleta.query.filter(Atleta.equipe_id==equipe.id)

    modalidades_query = db.session.query(Modalidade)
    posicoes_query = db.session.query(Posicao)
    categorias_query = db.session.query(Categoria)
    niveis_query = db.session.query(Nivel)
    status_query = db.session.query(Status)

    dados_equipe = {"nome_equipe":equipe.nome_equipe.title(),"projeto":projeto_equipe.nome_projeto.title(),"tecnico":tecnico_nome.title(),"is_active":bool(equipe.is_active),"created_at":datetime.strftime(equipe.created_at,"%d/%m/%Y"),"total_atletas":atletas_equipe.count()}

    #Atletas da equipe
    #Dicionário tabela atletas-equipe
    atletas = []
    for atleta in atletas_equipe:

        modalidade_atleta = modalidades_query.filter(Modalidade.id==atleta.modalidade_id).scalar().nome_modalidade

        posicao_atleta = posicoes_query.filter(Posicao.id==atleta.posicao_id).scalar().nome_posicao

        categoria_atleta = categorias_query.filter(Categoria.id==atleta.categorias_id).scalar().nome_categoria

        nivel_atleta = niveis_query.filter(Nivel.id==atleta.nivel_id).scalar().nome_nivel

        status_atleta = status_query.filter(Status.id==atleta.status_id).scalar().nome_status

        atletas.append({"id":atleta.id, "nome_atleta":atleta.firstname_atleta.title(), "equipe":equipe.nome_equipe.title(), "modalidade":modalidade_atleta.title(), "posicao":posicao_atleta.title(), "categoria":categoria_atleta.title(), "nivel":nivel_atleta.title(), "status":status_atleta.title()})
    

    return render_template("visualizar_equipe.html", equipe=dados_equipe, atletas=atletas)

@app.route('/view/atleta/')
def visualizar_atleta():
    atleta_id = request.args.get('atleta_id')

    status_query = db.session.query(Status)
    equipes_query = db.session.query(Equipe)
    projetos_query = db.session.query(Projeto)
    usuarios_query = db.session.query(Usuario)

    atleta = db.session.query(Atleta).filter(Atleta.id==atleta_id).scalar()

    equipe_atleta = equipes_query.filter(Equipe.id==atleta.equipe_id).scalar()

    projeto_atleta = projetos_query.filter(Projeto.id==equipe_atleta.projeto_id).scalar()

    status_atleta = status_query.filter(Status.id==atleta.status_id).scalar()

    historico_atleta = db.session.query(AtletaHistorico).filter(AtletaHistorico.atleta_id==atleta.id).all()

    modalidade_atleta = db.session.query(Modalidade.nome_modalidade).filter(Modalidade.id==atleta.modalidade_id).scalar()
    posicao_atleta = db.session.query(Posicao.nome_posicao).filter(Posicao.id==atleta.posicao_id).scalar()
    categoria_atleta = db.session.query(Categoria.nome_categoria).filter(Categoria.id==atleta.categorias_id).scalar()
    nivel_atleta = db.session.query(Nivel.nome_nivel).filter(Nivel.id==atleta.nivel_id).scalar()
    sexo_atleta = db.session.query(Sexo.sexo).filter(Sexo.id==atleta.sexo_id).scalar()

    nome_atleta = f"{atleta.firstname_atleta} {atleta.lastname_atleta}"

    #Após feita a função de login, organize a tabela a seguir usando update para que os dados sensíveis não vá para o console web
    dados_atleta = {"nome_atleta":nome_atleta.title(), "equipe":equipe_atleta.nome_equipe.title(), "projeto": projeto_atleta.nome_projeto.title(), "status":status_atleta.nome_status.title(), "modalidade":modalidade_atleta.title(), "posicao":posicao_atleta.title(), "categoria":categoria_atleta.title(), "nivel":nivel_atleta.title(), "sexo":sexo_atleta.title(), "email":atleta.email, "telefone1":format_telefone(atleta.telefone1), "telefone2":format_telefone(atleta.telefone2), "rg":format_rg(atleta.rg), "cpf":format_cpf(atleta.cpf), "data_nascimento":datetime.strftime(atleta.data_nascimento,"%d/%m/%Y")}

    # if pode_ver_dados_pessoais(usuario_logado):
    # dados_atleta.update({
    #     "email": atleta.email,
    #     "telefone1": atleta.telefone1,
    #     "telefone2": atleta.telefone2,
    #     "rg": atleta.rg,
    #     "cpf": atleta.cpf,
    #     "data_nascimento": atleta.data_nascimento.strftime("%d/%m/%Y")
    # })

    endereco_atleta = db.session.query(AtletaEndereco).filter(AtletaEndereco.atleta_id==atleta.id).scalar()

    if endereco_atleta:

        cidade_atleta = db.session.query(Cidade).filter(Cidade.id == endereco_atleta.cidade_id).scalar()

        estado_abr_atleta = db.session.query(Estado.abreviacao).filter(Estado.id == cidade_atleta.estado_id).scalar()

        dados_endereco = {"logradouro":endereco_atleta.logradouro, "numero":endereco_atleta.numero, "complemento": endereco_atleta.complemento, "bairro":endereco_atleta.bairro, "cidade":cidade_atleta.nome_cidade.title(), "estado_abreviacao":estado_abr_atleta, "cep":endereco_atleta.cep}
    else:
        dados_endereco=None

    historico = []
    for h in historico_atleta:

        h_status = status_query.filter(Status.id == h.status_id).scalar().nome_status

        h_projeto = projetos_query.filter(Projeto.id==h.projeto_id).scalar().nome_projeto

        h_equipe = equipes_query.filter(Equipe.id==h.equipe_id).scalar().nome_equipe

        h_responsavel = usuarios_query.filter(Usuario.id==h.responsavel_id).scalar()

        historico.append({"status":h_status.title(), "motivo":h.motivo, "projeto":h_projeto.title(), "equipe":h_equipe.title(), "responsavel":h_responsavel.firstname_usuario.title(), "created_at":h.created_at.strftime('%d/%m/%Y %H:%M')})

    return render_template("visualizar_atleta.html", atleta=dados_atleta, endereco=dados_endereco, historico=historico)

if __name__ == '__main__':
    # Cria o banco de dados e as tabelas, se ainda não existirem, dentro do contexto da aplicação
    with app.app_context():
        db.create_all()
    app.run(debug=True)
