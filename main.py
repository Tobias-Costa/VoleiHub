from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, DateField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from flask import Flask, request, redirect, url_for, render_template, flash, abort
from sqlalchemy import or_
from flask_migrate import Migrate
from admin import init_admin 
from datetime import datetime
from models import *
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import re
import hashlib

def somente_digitos(valor):
    """Remove tudo que não for número."""
    return re.sub(r"\D", "", valor) if valor else valor

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

def format_cep(cep):
    """Formata um CEP aceitando entrada com ou sem hífen."""

    if len(cep) == 8:
        return f"{cep[:5]}-{cep[5:]}"
    
    return cep

def hash_password(txt):
    hash_obj = hashlib.sha256(txt.encode('utf-8'))
    return hash_obj.hexdigest()

# Carrega as variáveis do arquivo .env para o sistema
load_dotenv()

app = Flask(__name__)
lm = LoginManager(app)
lm.login_view = 'login'
lm.login_message = None
# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "chave-padrao-de-desenvolvimento")
# Inicializa o 'db' e as migrações com o aplicativo 'app'
db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True)
init_admin(app) 

def create_initial_admin():
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        return
    
    # Se já existe algum usuário, não cria outro
    if Usuario.query.first():
        return

    admin = Usuario(
        firstname_usuario="ADMIN",
        lastname_usuario="USER",
        email=admin_email,
        password=hash_password(admin_password),
        telefone1="00000000000",
        telefone2=None,
        is_admin=True,
        is_coord=False,
        is_tecnico=False,
        created_at=datetime.now(),
        last_edited=datetime.now()
    )

    db.session.add(admin)
    db.session.commit()

@lm.user_loader
def user_loader(id):
    usuario = db.session.query(Usuario).filter_by(id=int(id)).first()
    return usuario

# --- Classes de formulários ---
class UsuarioRegisterForm(FlaskForm):
    firstname_usuario = StringField(
        'Nome',
        validators=[
            DataRequired(message="O nome é obrigatório."), 
            Length(min=2, max=80, message="O nome deve ter entre 2 e 80 caracteres.")
        ]
    )

    lastname_usuario = StringField(
        'Sobrenome',
        validators=[
            DataRequired(message="O sobrenome é obrigatório."), 
            Length(min=2, max=80, message="O sobrenome deve ter entre 2 e 80 caracteres.")
        ]
    )

    email = StringField(
        'E-mail',
        validators=[
            DataRequired(message="O e-mail é obrigatório."), 
            Email(message="Insira um endereço de e-mail válido."), 
            Length(max=120)
        ]
    )

    password = PasswordField(
        'Senha',
        validators=[
            DataRequired(message="A senha é obrigatória."), 
            Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")
        ]
    )

    confirm_password = PasswordField(
        'Confirmar Senha',
        validators=[
            DataRequired(message="A confirmação de senha é obrigatória."),
            EqualTo('password', message='As senhas devem ser iguais.')
        ]
    )

    telefone1 = StringField(
        'Telefone principal',
        validators=[
            DataRequired(message="O telefone principal é obrigatório."), 
            Length(max=20, message="O telefone não pode exceder 20 caracteres.")
        ]
    )

    telefone2 = StringField(
        'Telefone secundário',
        validators=[
            Optional(), 
            Length(max=20, message="O telefone secundário não pode exceder 20 caracteres.")
        ]
    )

    submit = SubmitField('Cadastrar')

class LoginForm(FlaskForm):
    email = StringField(
        'E-mail',
        validators=[
            DataRequired(message="O campo e-mail é obrigatório."),
            Email(message="Insira um e-mail válido.")
        ]
    )

    password = PasswordField(
        'Senha',
        validators=[
            DataRequired(message="A senha é obrigatória.")
        ]
    )

    submit = SubmitField('Entrar')

class ProjetoForm(FlaskForm):
    nome_projeto = StringField(
        'Nome do Projeto',
        validators=[
            DataRequired(message="O nome do projeto é obrigatório."),
            Length(min=5, max=80)
        ]
    )
    descricao = TextAreaField(
        'Descrição',
        validators=[Length(max=500)]
    )
    is_active = BooleanField(
        'Projeto ativo',
        default=True
    )
    cidade_id = SelectField(
        'Cidade',
        coerce=int,
        validators=[DataRequired(message="Selecione uma cidade.")]
    )
    responsavel_id = SelectField(
        'Responsável',
        coerce=int,
        validators=[DataRequired(message="Selecione um responsável para coordenar o projeto.")]
    )

class EquipeForm(FlaskForm):
    nome_equipe = StringField(
        "Nome da Equipe",
        validators=[DataRequired(message="O nome da equipe é obrigatório."), Length(min=3, max=80)]
    )

    projeto_id = SelectField(
        "Projeto",
        coerce=int,
        validators=[DataRequired(message="Selecione um projeto.")]
    )

    tecnico_id = SelectField(
        "Técnico Responsável",
        coerce=int,
        validators=[DataRequired(message="Selecione um técnico para a equipe")]
    )

    is_active = BooleanField("Equipe ativa", default=True)

class AtletaForm(FlaskForm):
    firstname_atleta = StringField(
        "Nome",
        validators=[DataRequired(message="O nome é obrigatório.")]
    )
    lastname_atleta = StringField(
        "Sobrenome",
        validators=[DataRequired(message="O sobrenome é obrigatório.")]
    )

    equipe_id = SelectField("Equipe", coerce=int, validators=[DataRequired(message="Selecione uma equipe.")])

    email = StringField(
        "Email",
        validators=[DataRequired(message="O e-mail é obrigatório."), Email(message="Email inválido.")]
    )

    data_nascimento = DateField(
        "Data de Nascimento",
        format="%Y-%m-%d",
        validators=[DataRequired(message="A data de nascimento é obrigatória.")]
    )

    telefone1 = StringField("Telefone 1", validators=[DataRequired(message="O telefone principal é obrigatório.")])
    telefone2 = StringField("Telefone 2")

    rg = StringField("RG", validators=[DataRequired(message="O RG é obrigatório."), Length(min=7, max=20, message="O RG deve ter entre 7 e 20 caracteres.")])
    cpf = StringField("CPF", validators=[DataRequired(message="O CPF é obrigatório."), Length(min=11, max=11, message="O CPF deve ter 11 dígitos.")])

    registro_cuca = StringField("Registro CUCA", validators=[
        Optional(),
        Length(min=2, max=40, message="O registro CUCA deve ter entre 2 e 40 caracteres.")
    ])

    registro_cbv = StringField("Registro CBV", validators=[
        Optional(),
        Length(min=2, max=40, message="O registro CBV deve ter entre 2 e 40 caracteres.")
    ])

    sexo_id = SelectField("Sexo", coerce=int, validators=[DataRequired(message="Selecione o sexo.")])
    modalidade_id = SelectField("Modalidade", coerce=int, validators=[DataRequired(message="Selecione a modalidade.")])
    posicao_id = SelectField("Posição", coerce=int, validators=[DataRequired(message="Selecione a posição.")])
    categoria_id = SelectField("Categoria", coerce=int, validators=[DataRequired(message="Selecione a categoria.")])
    nivel_id = SelectField("Nível", coerce=int, validators=[DataRequired(message="Selecione o nível.")])
    status_id = SelectField("Status", coerce=int, validators=[DataRequired(message="Selecione o status.")])

class EnderecoAtletaForm(FlaskForm):
    logradouro = StringField(
        "Logradouro",
        validators=[DataRequired(message="O logradouro é obrigatório.")]
    )

    numero = StringField(
        "Número",
        validators=[DataRequired(message="O número é obrigatório.")]
    )

    complemento = StringField("Complemento")

    bairro = StringField(
        "Bairro",
        validators=[DataRequired(message="O bairro é obrigatório.")]
    )

    cidade_id = SelectField(
        "Cidade",
        coerce=int,
        validators=[DataRequired(message="Selecione uma cidade.")]
    )

    cep = StringField(
        "CEP",
        validators=[DataRequired(message="O CEP é obrigatório.")]
    )

# --- Rotas da Aplicação ---
@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/cadastro', methods=["GET","POST"])
def cadastro_usuario():
    form = UsuarioRegisterForm()

    if form.validate_on_submit():
        
        try:

            novo_usuario = Usuario(
            firstname_usuario = form.firstname_usuario.data.upper(),
            lastname_usuario = form.lastname_usuario.data.upper(),
            email = form.email.data,
            password = hash_password(form.password.data),
            telefone1 = somente_digitos(form.telefone1.data),
            telefone2 = somente_digitos(form.telefone2.data),
            )
        
            db.session.add(novo_usuario)
            db.session.commit()
            login_user(novo_usuario)
            return redirect(url_for('home'))
        except Exception:
            db.session.rollback()
            flash("Erro ao cadastrar usuário.", "danger")

    return render_template("cadastro_usuario.html", form=form)

@app.route('/login', methods=["GET","POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.query(Usuario).filter_by(email=email, password=hash_password(password)).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
        elif not user:
            flash("Nome ou senha incorretos.", "danger")
        
    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/home')
@login_required
def home():
    # Coloque aqui querys gerais para otimizar o app reduzindo queries
    projetos_query = db.session.query(Projeto)
    equipes_query = db.session.query(Equipe)
    atletas_query = db.session.query(Atleta)
    usuarios_query = db.session.query(Usuario)
    cidades_query = db.session.query(Cidade)
    id_status_query = db.session.query(Status.id)

    # Painel dashboard
    total_projetos_ativos = projetos_query.filter_by(is_active=True).count()
    total_equipes_ativas = equipes_query.filter_by(is_active=True).count()
    total_atletas = atletas_query.count()

    # Status Atletas
    id_status_ativo = id_status_query.filter_by(nome_status="ATIVO").scalar()
    id_status_lesionado = id_status_query.filter_by(nome_status="LESIONADO").scalar()
    id_status_suspenso = id_status_query.filter_by(nome_status="SUSPENSO").scalar()

    atletas_ativos = atletas_query.filter_by(status_id=id_status_ativo).count()
    atletas_lesionados = atletas_query.filter_by(status_id=id_status_lesionado).count()
    atletas_suspensos = atletas_query.filter_by(status_id=id_status_suspenso).count()

    # Atividades recentes(transferências)
    # Queries base (fora do loop)
    transferencias_db = (
        db.session.query(Transferencia)
        .order_by(Transferencia.id.desc())
        .limit(5)
        .all()
    )

    # Montagem da lista
    transferencias = []

    for transferencia in transferencias_db:

        proj_origem = projetos_query.filter_by(
            id=transferencia.projeto_origem_id
        ).scalar()

        eq_origem = equipes_query.filter_by(
            id=transferencia.equipe_origem_id
        ).scalar()

        proj_destino = projetos_query.filter_by(
            id=transferencia.projeto_destino_id
        ).scalar()

        eq_destino = equipes_query.filter_by(
            id=transferencia.equipe_destino_id
        ).scalar()

        atleta = atletas_query.filter_by(
            id=transferencia.atleta_id
        ).scalar()

        responsavel = usuarios_query.filter_by(
            id=transferencia.responsavel_id
        ).scalar()

        transferencias.append({
            "id": transferencia.id,
            "proj_origem": proj_origem.nome_projeto,
            "eq_origem": eq_origem.nome_equipe,
            "proj_destino": proj_destino.nome_projeto,
            "eq_destino": eq_destino.nome_equipe,
            "nome_atleta": atleta.firstname_atleta.title(),
            "responsavel": responsavel.firstname_usuario.title(),
        })

    # Tabela projetos

    ## Lógica para o funcionamento do filtro de projetos
    q = request.args.get("q", "").strip()
    status = request.args.get("status")
    cidade_id = request.args.get("cidade", type=int)

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

        projetos.append({"id":projeto.id, "nome":projeto.nome_projeto, "cidade":projeto_cidade.title(), "n_equipes":projeto_equipes, "n_atletas":projeto_atletas, "is_active":bool(projeto.is_active)})

    cidades = [{"id":c.id, "nome_cidade":c.nome_cidade.title()} for c in cidades_query.all()]

    return render_template('dashboard.html', n_projetos_ativos=total_projetos_ativos, n_equipes_ativas=total_equipes_ativas, n_atletas=total_atletas, atletas_ativos=atletas_ativos, atletas_lesionados=atletas_lesionados, atletas_suspensos=atletas_suspensos, transferencias=transferencias, projetos=projetos, cidades=cidades)

@app.route('/coordenador/dashboard/')
@login_required
def coordenador_dashboard():
    #Verifica se tem acesso(admin ou coordenador)
    if not (current_user.is_admin or current_user.is_coord):
        abort(403)

    # Coloque aqui querys gerais para otimizar o app reduzindo queries
    # Projetos onde o usuário é coordenador
    projetos_query = db.session.query(Projeto).filter(
        Projeto.responsavel_id == current_user.id
    )

    # Equipes vinculadas aos projetos do coordenador
    equipes_query = db.session.query(Equipe).join(Projeto).filter(
        Projeto.responsavel_id == current_user.id
    )

    # Atletas vinculados às equipes dos projetos do coordenador
    atletas_query = db.session.query(Atleta) \
        .join(Equipe) \
        .join(Projeto) \
        .filter(Projeto.responsavel_id == current_user.id)

    cidades_query = db.session.query(Cidade)
    id_status_query = db.session.query(Status.id)

    # Painel dashboard
    total_equipes_ativas = equipes_query.filter(
        Equipe.is_active == True
    ).count()

    total_atletas = atletas_query.count()

    # Status dos atletas
    id_status_ativo = id_status_query.filter_by(nome_status="ATIVO").scalar()
    id_status_lesionado = id_status_query.filter_by(nome_status="LESIONADO").scalar()
    id_status_suspenso = id_status_query.filter_by(nome_status="SUSPENSO").scalar()

    atletas_ativos = atletas_query.filter(
        Atleta.status_id == id_status_ativo
    ).count()

    atletas_lesionados = atletas_query.filter(
        Atleta.status_id == id_status_lesionado
    ).count()

    atletas_suspensos = atletas_query.filter(
        Atleta.status_id == id_status_suspenso
    ).count()

    dashboard_dict = {"n_equipes_ativas":total_equipes_ativas, "n_atletas":total_atletas, "atletas_ativos":atletas_ativos, "atletas_lesionados":atletas_lesionados, "atletas_suspensos":atletas_suspensos}

    # Atividades recentes(transferências)
    transferencias_db = (
        db.session.query(Transferencia)
        .join(Projeto, or_(
            Projeto.id == Transferencia.projeto_origem_id,
            Projeto.id == Transferencia.projeto_destino_id
        ))
        .filter(Projeto.responsavel_id == current_user.id)
        .distinct()
        .order_by(Transferencia.id.desc())
        .limit(5)
        .all()
    )

    # Montagem da lista
    transferencias = []

    for transferencia in transferencias_db:

        proj_origem = db.session.query(Projeto).filter(Projeto.id == transferencia.projeto_origem_id).first()

        proj_destino = db.session.query(Projeto).filter(Projeto.id == transferencia.projeto_destino_id).first()

        eq_origem = db.session.query(Equipe).filter(Equipe.id == transferencia.equipe_origem_id).first()

        eq_destino = db.session.query(Equipe).filter(Equipe.id == transferencia.equipe_destino_id).first()

        atleta = db.session.query(Atleta).filter(Atleta.id == transferencia.atleta_id).first()

        responsavel = db.session.query(Usuario).filter(Usuario.id == transferencia.responsavel_id).first()

        transferencias.append({
            "id": transferencia.id,
            "proj_origem": proj_origem.nome_projeto,
            "eq_origem": eq_origem.nome_equipe,
            "proj_destino": proj_destino.nome_projeto,
            "eq_destino": eq_destino.nome_equipe,
            "nome_atleta": atleta.firstname_atleta.title(),
            "responsavel": responsavel.firstname_usuario.title(),
        })

    # Tabela Projetos
    ## Lógica para o funcionamento do filtro de projetos
    q = request.args.get("q", "").strip()
    status = request.args.get("status")
    cidade_id = request.args.get("cidade", type=int)

    ### Cria cópia de projetos_query com apenas os projetos do coordenador
    # filtro_query = projetos_query.filter(Projeto.responsavel_id==current_user.id)
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
        
        projeto_equipes = equipes_query.filter(Equipe.projeto_id==projeto.id).count()

        projeto_atletas = atletas_query.filter(Equipe.projeto_id == projeto.id).count()

        projetos.append({"id":projeto.id, "nome":projeto.nome_projeto, "cidade":projeto_cidade.title(), "n_equipes":projeto_equipes, "n_atletas":projeto_atletas, "is_active":bool(projeto.is_active)})

    cidades = [{"id":c.id, "nome_cidade":c.nome_cidade.title()} for c in cidades_query.all()]

    return render_template("painel_coordenador.html", dashboard=dashboard_dict, transferencias=transferencias, cidades=cidades, projetos=projetos)

@app.route('/tecnico/dashboard/')
@login_required
def tecnico_dashboard():
    #Verifica se tem acesso(admin, coordenador ou tecnico)
    if not(current_user.is_admin or current_user.is_tecnico):
        abort(403)

    # Coloque aqui querys gerais para otimizar o app reduzindo queries
    # Equipes do técnico logado
    # equipes_query = db.session.query(Equipe).filter(
    #     Equipe.tecnico_id == current_user.id
    # )

    # Atletas vinculados às equipes do técnico
    atletas_query = db.session.query(Atleta) \
        .join(Equipe) \
        .filter(Equipe.tecnico_id == current_user.id)

    # Total de atletas do técnico (somatório de todas as equipes)
    total_atletas = atletas_query.count()

    id_status_query = db.session.query(Status.id)

    # Status dos atletas
    id_status_ativo = id_status_query.filter_by(nome_status="ATIVO").scalar()
    id_status_lesionado = id_status_query.filter_by(nome_status="LESIONADO").scalar()
    id_status_suspenso = id_status_query.filter_by(nome_status="SUSPENSO").scalar()

    atletas_ativos = atletas_query.filter(
        Atleta.status_id == id_status_ativo
    ).count()

    atletas_lesionados = atletas_query.filter(
        Atleta.status_id == id_status_lesionado
    ).count()

    atletas_suspensos = atletas_query.filter(
        Atleta.status_id == id_status_suspenso
    ).count()

    dashboard_dict = {"n_atletas":total_atletas, "atletas_ativos":atletas_ativos, "atletas_lesionados":atletas_lesionados, "atletas_suspensos":atletas_suspensos}

    # Atividades recentes(transferências)
    # Transferências envolvendo equipes do técnico
    transferencias_db = (
        db.session.query(Transferencia)
        .join(
            Equipe,
            or_(
                Equipe.id == Transferencia.equipe_origem_id,
                Equipe.id == Transferencia.equipe_destino_id
            )
        )
        .filter(Equipe.tecnico_id == current_user.id)
        .distinct()
        .order_by(Transferencia.id.desc())
        .limit(5)
        .all()
    )

    # Montagem da lista
    transferencias = []

    for transferencia in transferencias_db:

        proj_origem = db.session.query(Projeto).filter(Projeto.id == transferencia.projeto_origem_id).first()

        proj_destino = db.session.query(Projeto).filter(Projeto.id == transferencia.projeto_destino_id).first()

        eq_origem = db.session.query(Equipe).filter(Equipe.id == transferencia.equipe_origem_id).first()

        eq_destino = db.session.query(Equipe).filter(Equipe.id == transferencia.equipe_destino_id).first()

        atleta = db.session.query(Atleta).filter(Atleta.id == transferencia.atleta_id).first()

        responsavel = db.session.query(Usuario).filter(Usuario.id == transferencia.responsavel_id).first()

        transferencias.append({
            "id": transferencia.id,
            "proj_origem": proj_origem.nome_projeto,
            "eq_origem": eq_origem.nome_equipe,
            "proj_destino": proj_destino.nome_projeto,
            "eq_destino": eq_destino.nome_equipe,
            "nome_atleta": atleta.firstname_atleta.title(),
            "responsavel": responsavel.firstname_usuario.title(),
        })

    # Tabela Equipe
    ## Lógica para o funcionamento do filtro de Equipes
    q = request.args.get("q", "").strip()
    status = request.args.get("status")

    ### Cria cópia de equipes_query com apenas as equipes do técnico
    filtro_query = (
        db.session.query(Equipe, Projeto)
        .join(Projeto, Projeto.id == Equipe.projeto_id)
        .filter(Equipe.tecnico_id == current_user.id)
    )

    if q:
        filtro_query = filtro_query.filter(or_(Equipe.nome_equipe.ilike(f"%{q}%"), Projeto.nome_projeto.ilike(f"%{q}%")))

    if status == "ativo":
        filtro_query = filtro_query.filter(Equipe.is_active == True)
    elif status == "inativo":
        filtro_query = filtro_query.filter(Equipe.is_active == False)

    lista_equipes = filtro_query.all()

    equipes = []
    for equipe, projeto in lista_equipes:
        total_atletas = atletas_query.filter(Atleta.equipe_id == equipe.id).count()

        equipes.append({"id":equipe.id, "nome_equipe":equipe.nome_equipe,"nome_projeto":projeto.nome_projeto, "is_active":bool(equipe.is_active),"total_atletas":total_atletas})

    return render_template("painel_tecnico.html", dashboard=dashboard_dict, transferencias=transferencias, equipes=equipes)

@app.route('/criar/projeto/', methods=["GET","POST"])
@login_required
def criar_projeto():

    #Verifica se tem acesso(admin ou coordenador)
    if not (current_user.is_admin or current_user.is_coord):
        abort(403)

    form = ProjetoForm()

    # Popula cidades
    form.cidade_id.choices = [
        (cidade_id, f"{nome_cidade.title()} - {abreviacao}")
        for cidade_id, nome_cidade, abreviacao in (
            db.session.query(
                Cidade.id,
                Cidade.nome_cidade,
                Estado.abreviacao
            )
            .join(Estado, Estado.id == Cidade.estado_id)
            .order_by(Cidade.nome_cidade)
            .all()
        )
    ]

    # Popula responsáveis
    if current_user.is_admin:
        responsaveis = Usuario.query.filter(or_(Usuario.is_admin == True, Usuario.is_coord == True)).all()
    else:
        responsaveis = [current_user]

    form.responsavel_id.choices = [(u.id, f"{u.firstname_usuario.title()} {u.lastname_usuario.title()}") for u in responsaveis]

    # Opção inicial
    form.cidade_id.choices.insert(0, (0, "Selecione uma cidade"))
    form.responsavel_id.choices.insert(0, (0, "Selecione um responsável"))

    if form.validate_on_submit():

        try:
            novo_projeto = Projeto(
                nome_projeto=form.nome_projeto.data,
                descricao=form.descricao.data,
                cidade_id=form.cidade_id.data,
                responsavel_id=form.responsavel_id.data
                )
            db.session.add(novo_projeto)
            db.session.commit()
            flash("Projeto salvo com sucesso!", "success")
            return redirect(url_for('criar_projeto'))
        except Exception:
            db.session.rollback()
            flash("Erro ao salvar no banco de dados.", "danger")

    return render_template('criar_projeto.html', form=form)

@app.route('/editar/projeto/', methods=["GET","POST"])
@login_required
def editar_projeto():
    projeto_id = request.args.get("projeto_id", type=int)

    #Verifica se tem acesso(admin ou coordenador do projeto)
    projeto_query = db.session.query(Projeto).filter(Projeto.id==projeto_id)

    if current_user.is_admin:
        pass
    elif current_user.is_coord:
        projeto_query = projeto_query.filter(Projeto.responsavel_id == current_user.id)
    else:
        abort(403)

    projeto = projeto_query.first_or_404()

    form = ProjetoForm(obj=projeto)

    form.cidade_id.choices = [
        (cidade_id, f"{nome_cidade.title()} - {abreviacao}")
        for cidade_id, nome_cidade, abreviacao in (
            db.session.query(
                Cidade.id,
                Cidade.nome_cidade,
                Estado.abreviacao
            )
            .join(Estado, Estado.id == Cidade.estado_id)
            .order_by(Cidade.nome_cidade)
            .all()
        )
    ]

    # Popula responsáveis
    if current_user.is_admin:
        responsaveis = Usuario.query.filter(or_(Usuario.is_admin == True, Usuario.is_coord == True)).all()
    else:
        responsaveis = [current_user]

    form.responsavel_id.choices = [(u.id, f"{u.firstname_usuario.title()} {u.lastname_usuario.title()}") for u in responsaveis]

    # Opção inicial
    form.cidade_id.choices.insert(0, (0, "Selecione uma cidade"))
    form.responsavel_id.choices.insert(0, (0, "Selecione um responsável"))

    if form.validate_on_submit():
        try:
            projeto.nome_projeto = form.nome_projeto.data
            projeto.descricao = form.descricao.data
            projeto.is_active = form.is_active.data
            projeto.cidade_id = form.cidade_id.data
            projeto.responsavel_id = form.responsavel_id.data
            db.session.commit()
            flash("Projeto atualizado com sucesso!", "success")
            return redirect(url_for('editar_projeto', projeto_id=projeto.id))
        except Exception:
            db.session.rollback()
            flash("Erro ao atualizar o projeto.", "danger")
    
    return render_template("editar_projeto.html", form=form, projeto=projeto)

@app.route('/criar/equipe/', methods=["GET","POST"])
@login_required
def criar_equipe():
    #Verifica se tem acesso(admin ou coordenador)
    if not (current_user.is_admin or current_user.is_coord):
        abort(403)

    form = EquipeForm()

    # Popula projetos
    projetos_query = Projeto.query.filter(Projeto.is_active == True)

    if current_user.is_admin:
        pass
    else:
        projetos_query = projetos_query.filter(Projeto.responsavel_id == current_user.id)

    projetos = projetos_query.all()

    form.projeto_id.choices = [(p.id, p.nome_projeto) for p in projetos]

    # Popula técnicos(Todos que são técnicos + usuário)
    tecnicos = Usuario.query.filter(Usuario.is_tecnico == True).all()
    usuarios_tecnicos = tecnicos.copy()

    if current_user.id not in [u.id for u in usuarios_tecnicos]:
        usuarios_tecnicos.insert(0, current_user)

    form.tecnico_id.choices = [
        (u.id, f"{u.firstname_usuario.title()} {u.lastname_usuario.title()}")
        for u in usuarios_tecnicos
    ]

    form.projeto_id.choices.insert(0, (0, "Selecione uma cidade"))
    form.tecnico_id.choices.insert(0, (0, "Selecione um responsável"))

    if form.validate_on_submit():
        nova_equipe = Equipe(
            nome_equipe=form.nome_equipe.data,
            projeto_id=form.projeto_id.data,
            tecnico_id=form.tecnico_id.data,
        )

        try:
            db.session.add(nova_equipe)
            db.session.commit()
            flash("Equipe criada com sucesso!", "success")
            return redirect(url_for("criar_equipe"))
        except Exception:
            db.session.rollback()
            flash("Erro ao salvar equipe.", "danger")

    return render_template('criar_equipe.html', form=form)

@app.route('/editar/equipe/', methods=["GET","POST"])
@login_required
def editar_equipe():
    equipe_id = request.args.get('equipe_id', type=int)

    #Verifica se tem acesso(admin ou coordenador do projeto)

    equipe_query = (
    db.session.query(Equipe)
    .join(Projeto, Projeto.id == Equipe.projeto_id)
    .filter(Equipe.id == equipe_id)
    )
        
    if current_user.is_admin:
        pass
    elif current_user.is_coord:
        equipe_query = equipe_query.filter(Projeto.responsavel_id == current_user.id)
    # elif current_user.is_tecnico:
    #     equipe_query = equipe_query.filter(Equipe.tecnico_id == current_user.id)
    else:
        abort(403)

    equipe = equipe_query.first_or_404()

    form = EquipeForm(obj=equipe)

    # Popula projetos
    projetos_query = Projeto.query.filter(Projeto.is_active == True)

    if current_user.is_admin:
        pass
    else:
        projetos_query = projetos_query.filter(Projeto.responsavel_id == current_user.id)

    projetos = projetos_query.all()

    form.projeto_id.choices = [(p.id, p.nome_projeto) for p in projetos]

    # Popula técnicos(Todos que são técnicos + usuário)
    tecnicos = Usuario.query.filter(Usuario.is_tecnico == True).all()
    usuarios_tecnicos = tecnicos.copy()

    if current_user.id not in [u.id for u in usuarios_tecnicos]:
        usuarios_tecnicos.insert(0, current_user)

    form.tecnico_id.choices = [
        (u.id, f"{u.firstname_usuario.title()} {u.lastname_usuario.title()}")
        for u in usuarios_tecnicos
    ]

    form.projeto_id.choices.insert(0, (0, "Selecione uma cidade"))
    form.tecnico_id.choices.insert(0, (0, "Selecione um responsável"))

    if form.validate_on_submit():
        try:
            equipe.nome_equipe = form.nome_equipe.data
            equipe.projeto_id = form.projeto_id.data
            equipe.tecnico_id = form.tecnico_id.data
            equipe.is_active = form.is_active.data
            db.session.commit()
            flash("Equipe atualizada com sucesso!", "success")
            return redirect(url_for("editar_equipe", equipe_id=equipe.id))
        except Exception:
            db.session.rollback()
            flash("Erro ao atualizar equipe.", "danger")

    return render_template('editar_equipe.html', form=form, equipe=equipe)

@app.route('/criar/atleta/', methods=["GET","POST"])
@login_required
def criar_atleta():
    #Verifica se tem acesso(admin, coordenador ou tecnico)
    if not( current_user.is_admin or current_user.is_coord or current_user.is_tecnico ):
        abort(403)

    form = AtletaForm()

    # Popula selects de Equipes
    equipe_query = (
        db.session.query(
            Equipe.id,
            Equipe.nome_equipe,
            Projeto.nome_projeto
            ).join(Projeto, Projeto.id == Equipe.projeto_id)
    )

    if current_user.is_admin:
        pass
    elif current_user.is_coord:
        equipe_query = equipe_query.filter(
            Projeto.responsavel_id == current_user.id
        )
    elif current_user.is_tecnico:
        equipe_query = equipe_query.filter(
            Equipe.tecnico_id == current_user.id
        )

    form.equipe_id.choices = [
        (equipe_id, f"{nome_equipe} - {nome_projeto}")
        for equipe_id, nome_equipe, nome_projeto in equipe_query.all()
    ]

    form.sexo_id.choices = [(s.id, s.sexo.title()) for s in Sexo.query.all()]
    form.modalidade_id.choices = [(m.id, m.nome_modalidade.title()) for m in Modalidade.query.all()]
    form.posicao_id.choices = [(p.id, p.nome_posicao.title()) for p in Posicao.query.all()]
    form.categoria_id.choices = [(c.id, c.nome_categoria.title()) for c in Categoria.query.all()]
    form.nivel_id.choices = [(n.id, n.nome_nivel.title()) for n in Nivel.query.all()]
    form.status_id.choices = [(st.id, st.nome_status.title()) for st in Status.query.all()]

    form.equipe_id.choices.insert(0, (0, "Selecione uma equipe."))
    form.sexo_id.choices.insert(0, (0, "Selecione."))
    form.modalidade_id.choices.insert(0, (0, "Selecione a modalidade."))
    form.posicao_id.choices.insert(0, (0, "Selecione a posição."))
    form.categoria_id.choices.insert(0, (0, "Selecione uma categoria."))
    form.nivel_id.choices.insert(0, (0, "Selecione o nível do atleta."))
    form.status_id.choices.insert(0, (0, "Selecione o status do atleta."))

    if form.validate_on_submit():
        novo_atleta = Atleta(
            firstname_atleta=form.firstname_atleta.data.upper(),
            lastname_atleta=form.lastname_atleta.data.upper(),
            equipe_id=form.equipe_id.data,
            email=form.email.data.lower(),
            data_nascimento=form.data_nascimento.data,
            telefone1=somente_digitos(form.telefone1.data),
            telefone2=somente_digitos(form.telefone2.data),
            rg=somente_digitos(form.rg.data),
            cpf=somente_digitos(form.cpf.data),
            registro_cuca=form.registro_cuca.data,
            registro_cbv=form.registro_cbv.data,
            sexo_id=form.sexo_id.data,
            modalidade_id=form.modalidade_id.data,
            posicao_id=form.posicao_id.data,
            categoria_id=form.categoria_id.data,
            nivel_id=form.nivel_id.data,
            status_id=form.status_id.data,
        )

        try:
            db.session.add(novo_atleta)
            db.session.flush()  # Gera o ID sem dar commit

            # Busca equipe e projeto
            equipe_atleta = db.session.query(Equipe).filter(Equipe.id == novo_atleta.equipe_id).first()
            projeto_atleta = db.session.query(Projeto).filter(Projeto.id == equipe_atleta.projeto_id).first()

            # Cria histórico
            novo_historico = AtletaHistorico(
                atleta_id=novo_atleta.id,
                projeto_id=projeto_atleta.id,
                equipe_id=equipe_atleta.id,
                status_id=novo_atleta.status_id,
                motivo="Adicionado à equipe",
                responsavel_id=current_user.id 
            )

            db.session.add(novo_historico)
            db.session.commit()
            flash("Atleta criado com sucesso!", "success")
            return redirect(url_for("criar_endereco_atleta", atleta_id=novo_atleta.id))
        except Exception:
            db.session.rollback()
            flash("Erro ao cadastrar atleta.", "danger")

    return render_template("criar_atleta.html", form=form)

@app.route('/editar/atleta/', methods=["GET","POST"])
@login_required
def editar_atleta():
    atleta_id = request.args.get("atleta_id", type=int)

    #Verifica se tem acesso(admin ou coordenador do projeto ou tecnico da equipe)
    
    atleta_query = (
    db.session.query(Atleta, Projeto)
    .join(Equipe, Equipe.id == Atleta.equipe_id)
    .join(Projeto, Projeto.id == Equipe.projeto_id)
    .filter(Atleta.id == atleta_id)
    )

    if current_user.is_admin:
        pass
    elif current_user.is_coord:
        atleta_query = atleta_query.filter(
            Projeto.responsavel_id == current_user.id
        )
    elif current_user.is_tecnico:
        atleta_query = atleta_query.filter(
            Equipe.tecnico_id == current_user.id
        )
    else:
        abort(403)

    result = atleta_query.first_or_404()
    atleta = result.Atleta
    projeto_atual = result.Projeto

    # 🔒 Salvando estado anterior
    status_anterior_id = atleta.status_id
    equipe_anterior_id = atleta.equipe_id
    projeto_anterior_id = projeto_atual.id

    form = AtletaForm(obj=atleta)

    # =========================
    # POPULA EQUIPES
    # =========================
    equipe_query = (
        db.session.query(
            Equipe.id,
            Equipe.nome_equipe,
            Projeto.nome_projeto
            ).join(Projeto, Projeto.id == Equipe.projeto_id)
    )

    if current_user.is_admin or current_user.is_coord:
        #Mostra todos os projetos em caso de desejo de transferência
        pass
    elif current_user.is_tecnico:
        # Aparece somente equipes do projeto do atleta e não mais equipes do técnico
        equipe_query = equipe_query.filter(
            Projeto.id == projeto_atual.id
        )

    form.equipe_id.choices = [
        (equipe_id, f"{nome_equipe} - {nome_projeto}")
        for equipe_id, nome_equipe, nome_projeto in equipe_query.all()
    ]

    # =========================
    # DEMAIS SELECTS
    # =========================
    form.sexo_id.choices = [(s.id, s.sexo.title()) for s in Sexo.query.all()]
    form.modalidade_id.choices = [(m.id, m.nome_modalidade.title()) for m in Modalidade.query.all()]
    form.posicao_id.choices = [(p.id, p.nome_posicao.title()) for p in Posicao.query.all()]
    form.categoria_id.choices = [(c.id, c.nome_categoria.title()) for c in Categoria.query.all()]
    form.nivel_id.choices = [(n.id, n.nome_nivel.title()) for n in Nivel.query.all()]
    form.status_id.choices = [(st.id, st.nome_status.title()) for st in Status.query.all()]

    form.equipe_id.choices.insert(0, (0, "Selecione uma equipe."))
    form.sexo_id.choices.insert(0, (0, "Selecione."))
    form.modalidade_id.choices.insert(0, (0, "Selecione a modalidade."))
    form.posicao_id.choices.insert(0, (0, "Selecione a posição."))
    form.categoria_id.choices.insert(0, (0, "Selecione uma categoria."))
    form.nivel_id.choices.insert(0, (0, "Selecione o nível do atleta."))
    form.status_id.choices.insert(0, (0, "Selecione o status do atleta."))

    if form.validate_on_submit():

        try:
            status_novo_id = form.status_id.data
            equipe_nova_id = form.equipe_id.data

            # Atualiza dados básicos
            atleta.firstname_atleta=form.firstname_atleta.data.upper()
            atleta.lastname_atleta=form.lastname_atleta.data.upper()
            atleta.email=form.email.data.lower()
            atleta.data_nascimento=form.data_nascimento.data
            atleta.telefone1=somente_digitos(form.telefone1.data)
            atleta.telefone2=somente_digitos(form.telefone2.data)
            atleta.rg=somente_digitos(form.rg.data)
            atleta.cpf=somente_digitos(form.cpf.data)
            atleta.registro_cuca=form.registro_cuca.data
            atleta.registro_cbv=form.registro_cbv.data
            atleta.sexo_id=form.sexo_id.data
            atleta.modalidade_id=form.modalidade_id.data
            atleta.posicao_id=form.posicao_id.data
            atleta.categoria_id=form.categoria_id.data
            atleta.nivel_id=form.nivel_id.data

            # =====================
            # 🔄 TRANSFERÊNCIA
            # =====================
            if equipe_nova_id != equipe_anterior_id:
                equipe_nova = db.session.query(Equipe).filter(Equipe.id == equipe_nova_id).first()

                transferencia = Transferencia(
                    atleta_id=atleta.id,
                    equipe_origem_id=equipe_anterior_id,
                    equipe_destino_id=equipe_nova_id,
                    projeto_origem_id=projeto_anterior_id,
                    projeto_destino_id=equipe_nova.projeto_id,
                    responsavel_id=current_user.id
                )
                db.session.add(transferencia)

                historico_transferencia = AtletaHistorico(
                    atleta_id=atleta.id,
                    projeto_id=equipe_nova.projeto_id,
                    equipe_id=equipe_nova_id,
                    status_id=status_novo_id,
                    motivo="Transferência de equipe",
                    responsavel_id=current_user.id
                )
                db.session.add(historico_transferencia)

                atleta.equipe_id = equipe_nova_id
                atleta.status_id = status_novo_id

            # =====================
            # 🔁 STATUS
            # =====================
            elif status_novo_id != status_anterior_id:
                historico_status = AtletaHistorico(
                    atleta_id=atleta.id,
                    projeto_id=projeto_anterior_id,
                    equipe_id=atleta.equipe_id,
                    status_id=status_novo_id,
                    motivo="Alteração de status",
                    responsavel_id=current_user.id
                )
                db.session.add(historico_status)

                atleta.status_id = status_novo_id

            db.session.commit()            
            flash("Atleta atualizado com sucesso!", "success")
            return redirect(url_for("editar_atleta", atleta_id=atleta.id))
        except Exception:
            db.session.rollback()
            flash("Erro ao atualizar atleta.", "danger")

    return render_template("editar_atleta.html", form=form, atleta=atleta)

@app.route("/criar/endereco/atleta/", methods=["GET", "POST"])
@login_required
def criar_endereco_atleta():
    atleta_id = request.args.get("atleta_id", type=int)

    atleta_endereco_query = (
        db.session.query(Atleta)
        .join(Equipe, Equipe.id == Atleta.equipe_id)
        .join(Projeto, Projeto.id == Equipe.projeto_id)
        .filter(Atleta.id == atleta_id)
    )

    #Verifica se tem acesso(admin, coordenador do projeto ou tecnico da equipe do atleta)
    if current_user.is_admin:
        pass
    elif current_user.is_coord:
        atleta_endereco_query = atleta_endereco_query.filter(
            Projeto.responsavel_id == current_user.id
        )
    elif current_user.is_tecnico:
        atleta_endereco_query = atleta_endereco_query.filter(
            Equipe.tecnico_id == current_user.id
        )
    else:
        abort(403)

    atleta = atleta_endereco_query.first_or_404()

    form = EnderecoAtletaForm()

    # Popula cidades
    form.cidade_id.choices = [
        (cidade_id, f"{nome_cidade.title()} - {abreviacao}")
        for cidade_id, nome_cidade, abreviacao in (
            db.session.query(
                Cidade.id,
                Cidade.nome_cidade,
                Estado.abreviacao
            )
            .join(Estado, Estado.id == Cidade.estado_id)
            .order_by(Cidade.nome_cidade)
            .all()
        )
    ]

    # Placeholder padrão
    form.cidade_id.choices.insert(0, (0, "Selecione a cidade"))

    if form.validate_on_submit():
        try:
            endereco = AtletaEndereco(
                atleta_id=atleta.id,
                logradouro=form.logradouro.data.upper(),
                numero=form.numero.data,
                complemento=form.complemento.data.upper(),
                bairro=form.bairro.data.upper(),
                cidade_id=form.cidade_id.data,
                cep=somente_digitos(form.cep.data)
            )

            db.session.add(endereco)
            db.session.commit()

            flash("Endereço cadastrado com sucesso!", "success")
            return redirect(url_for("home"))

        except Exception:
            db.session.rollback()
            flash("Erro ao salvar endereço.", "danger")

    return render_template(
        "criar_endereco_atleta.html",
        form=form,
        atleta=atleta
    )

@app.route("/editar/endereco/atleta/", methods=["GET", "POST"])
@login_required
def editar_endereco_atleta():
    atleta_id = request.args.get("atleta_id", type=int)
    atleta = Atleta.query.get_or_404(atleta_id)

    endereco_existe = (
        db.session.query(AtletaEndereco)
        .filter(AtletaEndereco.atleta_id == atleta.id)
        .first()
    )
    #Verifica se existe o endereço de fato no bd
    # Na rota de criar endereço há verificação de permissão
    if not endereco_existe:
        return redirect(
            url_for("criar_endereco_atleta", atleta_id=atleta.id)
        )
    
    #Verifica se tem acesso(admin ou coordenador do projeto ou tecnico da equipe)

    endereco_atleta_query = (
    db.session.query(AtletaEndereco)
    .join(Atleta, Atleta.id == AtletaEndereco.atleta_id)
    .join(Equipe, Equipe.id == Atleta.equipe_id)
    .join(Projeto, Projeto.id == Equipe.projeto_id)
    .filter(AtletaEndereco.atleta_id == atleta.id)
    )

    if current_user.is_admin:
        pass
    elif current_user.is_coord:
        endereco_atleta_query = endereco_atleta_query.filter(
            Projeto.responsavel_id == current_user.id
        )
    elif current_user.is_tecnico:
        endereco_atleta_query = endereco_atleta_query.filter(
            Equipe.tecnico_id == current_user.id
        )
    else:
        abort(403)

    endereco_atleta = endereco_atleta_query.first_or_404()

    form = EnderecoAtletaForm(obj=endereco_atleta)

    form.cidade_id.choices = [
        (cidade_id, f"{nome_cidade.title()} - {abreviacao}")
        for cidade_id, nome_cidade, abreviacao in (
            db.session.query(
                Cidade.id,
                Cidade.nome_cidade,
                Estado.abreviacao
            )
            .join(Estado, Estado.id == Cidade.estado_id)
            .order_by(Cidade.nome_cidade)
            .all()
        )
    ]

    # Placeholder padrão
    form.cidade_id.choices.insert(0, (0, "Selecione a cidade"))

    if form.validate_on_submit():
        try:
            endereco_atleta.logradouro = form.logradouro.data.upper()
            endereco_atleta.numero = form.numero.data
            endereco_atleta.complemento = form.complemento.data.upper()
            endereco_atleta.bairro = form.bairro.data.upper()
            endereco_atleta.cidade_id = form.cidade_id.data
            endereco_atleta.cep = somente_digitos(form.cep.data)
            db.session.commit()

            flash("Endereço atualizado com sucesso!", "success")
            return redirect(url_for("editar_endereco_atleta", atleta_id=atleta.id))

        except Exception:
            db.session.rollback()
            flash("Erro ao atualizar endereço.", "danger")

    return render_template(
        "editar_endereco_atleta.html",
        form=form,
        atleta=atleta
    )

@app.route('/view/projeto/')
@login_required
def visualizar_projeto():
    projeto_id = request.args.get('projeto_id', type=int)

    # Querys principais para a rota
    projeto = db.session.query(Projeto).filter(Projeto.id == projeto_id).scalar()
    dados_projeto = {"id":projeto.id, "nome_projeto":projeto.nome_projeto, "descricao":projeto.descricao, "is_active":bool(projeto.is_active)}

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
    nome_responsavel = f"{responsavel.firstname_usuario} {responsavel.lastname_usuario}".title()

    #Dicionário tabela equipes-projeto
    equipes = []
    for equipe in projeto_equipes:
        tecnico_equipe = usuarios_query.filter(Usuario.id == equipe.tecnico_id).scalar()
        total_atletas = projeto_atletas.filter(Atleta.equipe_id == equipe.id).count()

        equipes.append({"id":equipe.id, "nome_equipe":equipe.nome_equipe,"tecnico":tecnico_equipe.firstname_usuario.title(), "is_active":bool(equipe.is_active),"total_atletas":total_atletas})

    #Dicionário tabela atletas-equipe
    atletas = []
    for atleta in projeto_atletas:
        equipe_atleta = projeto_equipes.filter(Equipe.id == atleta.equipe_id).scalar()

        modalidade_atleta = modalidades_query.filter(Modalidade.id==atleta.modalidade_id).scalar().nome_modalidade

        posicao_atleta = posicoes_query.filter(Posicao.id==atleta.posicao_id).scalar().nome_posicao

        categoria_atleta = categorias_query.filter(Categoria.id==atleta.categoria_id).scalar().nome_categoria

        nivel_atleta = niveis_query.filter(Nivel.id==atleta.nivel_id).scalar().nome_nivel

        status_atleta = status_query.filter(Status.id==atleta.status_id).scalar().nome_status

        atletas.append({"id":atleta.id, "nome_atleta":atleta.firstname_atleta.title(), "equipe":equipe_atleta.nome_equipe, "modalidade":modalidade_atleta.title(), "posicao":posicao_atleta.title(), "categoria":categoria_atleta.title(), "nivel":nivel_atleta.title(), "status":status_atleta.title()})
    
    can_edit = ((current_user.is_admin) or (current_user.is_coord and current_user.id==projeto.responsavel_id))
        
    return render_template('visualizar_projeto.html', projeto=dados_projeto, nome_cidade=cidade.nome_cidade.title(), nome_responsavel=nome_responsavel, n_equipes=projeto_equipes.count(), n_atletas=projeto_atletas.count(), equipes=equipes, atletas=atletas, can_edit=can_edit)

@app.route('/view/equipe/')
@login_required
def visualizar_equipe():
    equipe_id = request.args.get('equipe_id', type=int)

    #Dados da equipe
    equipe = Equipe.query.get_or_404(equipe_id)
    projeto_equipe = db.session.query(Projeto).filter(Projeto.id==equipe.projeto_id).scalar()
    tecnico_equipe = db.session.query(Usuario).filter(Usuario.id==equipe.tecnico_id).scalar()
    tecnico_nome = f"{tecnico_equipe.firstname_usuario} {tecnico_equipe.lastname_usuario}"

    atletas_equipe = Atleta.query.filter(Atleta.equipe_id==equipe.id)

    modalidades_query = db.session.query(Modalidade)
    posicoes_query = db.session.query(Posicao)
    categorias_query = db.session.query(Categoria)
    niveis_query = db.session.query(Nivel)
    status_query = db.session.query(Status)

    dados_equipe = {"id":equipe.id, "nome_equipe":equipe.nome_equipe, "projeto_id":projeto_equipe.id, "projeto":projeto_equipe.nome_projeto,"tecnico":tecnico_nome.title(),"is_active":bool(equipe.is_active),"total_atletas":atletas_equipe.count()}

    #Atletas da equipe
    #Dicionário tabela atletas-equipe
    atletas = []
    for atleta in atletas_equipe:

        modalidade_atleta = modalidades_query.filter(Modalidade.id==atleta.modalidade_id).scalar().nome_modalidade

        posicao_atleta = posicoes_query.filter(Posicao.id==atleta.posicao_id).scalar().nome_posicao

        categoria_atleta = categorias_query.filter(Categoria.id==atleta.categoria_id).scalar().nome_categoria

        nivel_atleta = niveis_query.filter(Nivel.id==atleta.nivel_id).scalar().nome_nivel

        status_atleta = status_query.filter(Status.id==atleta.status_id).scalar().nome_status

        atletas.append({"id":atleta.id, "nome_atleta":atleta.firstname_atleta.title(), "equipe":equipe.nome_equipe, "modalidade":modalidade_atleta.title(), "posicao":posicao_atleta.title(), "categoria":categoria_atleta.title(), "nivel":nivel_atleta.title(), "status":status_atleta.title()})

        if (current_user.is_admin) or (current_user.is_coord and current_user.id==projeto_equipe.responsavel_id):
            can_edit = True
    
    can_edit = ((current_user.is_admin) or (current_user.is_coord and current_user.id==projeto_equipe.responsavel_id) or (current_user.is_tecnico and current_user.id==equipe.tecnico_id))

    return render_template("visualizar_equipe.html", equipe=dados_equipe, atletas=atletas, can_edit=can_edit)

@app.route('/view/atleta/')
@login_required
def visualizar_atleta():
    atleta_id = request.args.get('atleta_id', type=int)

    status_query = db.session.query(Status)
    equipes_query = db.session.query(Equipe)
    projetos_query = db.session.query(Projeto)

    atleta = Atleta.query.get_or_404(atleta_id)
    nome_atleta = f"{atleta.firstname_atleta} {atleta.lastname_atleta}"
    equipe_atleta = equipes_query.filter(Equipe.id==atleta.equipe_id).scalar()
    projeto_atleta = projetos_query.filter(Projeto.id==equipe_atleta.projeto_id).scalar()
    status_atleta = status_query.filter(Status.id==atleta.status_id).scalar()
    modalidade_atleta = db.session.query(Modalidade.nome_modalidade).filter(Modalidade.id==atleta.modalidade_id).scalar()
    posicao_atleta = db.session.query(Posicao.nome_posicao).filter(Posicao.id==atleta.posicao_id).scalar()
    categoria_atleta = db.session.query(Categoria.nome_categoria).filter(Categoria.id==atleta.categoria_id).scalar()
    nivel_atleta = db.session.query(Nivel.nome_nivel).filter(Nivel.id==atleta.nivel_id).scalar()
    sexo_atleta = db.session.query(Sexo.sexo).filter(Sexo.id==atleta.sexo_id).scalar()

    dados_atleta = {"id":atleta.id, "nome_atleta":nome_atleta.title(), "equipe_id":equipe_atleta.id, "equipe":equipe_atleta.nome_equipe, "projeto": projeto_atleta.nome_projeto, "status":status_atleta.nome_status.title(), "modalidade":modalidade_atleta.title(), "posicao":posicao_atleta.title(), "categoria":categoria_atleta.title(), "nivel":nivel_atleta.title(), "sexo":sexo_atleta.title()}

    dados_pessoais_atleta = None
    dados_endereco = None

    # DADOS PRIVADOS

    can_edit = ((current_user.is_admin) or (current_user.is_coord and current_user.id==projeto_atleta.responsavel_id) or (current_user.is_tecnico and current_user.id==equipe_atleta.tecnico_id))
        
    if can_edit:

        dados_pessoais_atleta = {
            "email":atleta.email,
            "telefone1":format_telefone(atleta.telefone1),
            "telefone2":format_telefone(atleta.telefone2),
            "rg":format_rg(atleta.rg),
            "cpf":format_cpf(atleta.cpf),
            "cuca":atleta.registro_cuca,
            "cbv":atleta.registro_cbv,
            "data_nascimento":datetime.strftime(atleta.data_nascimento,"%d/%m/%Y")
        }

        endereco_atleta = db.session.query(AtletaEndereco).filter(AtletaEndereco.atleta_id==atleta.id).scalar()

        if endereco_atleta:

            cidade_atleta = db.session.query(Cidade).filter(Cidade.id == endereco_atleta.cidade_id).scalar()
            estado_abr_atleta = db.session.query(Estado.abreviacao).filter(Estado.id == cidade_atleta.estado_id).scalar()

            dados_endereco = {"logradouro":endereco_atleta.logradouro.title(), "numero":endereco_atleta.numero, "complemento": endereco_atleta.complemento.title(), "bairro":endereco_atleta.bairro.title(), "cidade":cidade_atleta.nome_cidade.title(), "estado_abreviacao":estado_abr_atleta.upper(), "cep":format_cep(endereco_atleta.cep)}

    # HISTÓRICO (1 QUERY)
    
    historico_rows = (
        db.session.query(
            AtletaHistorico,
            Status.nome_status,
            Projeto.nome_projeto,
            Equipe.nome_equipe,
            Usuario.firstname_usuario
        )
        .join(Status, Status.id == AtletaHistorico.status_id)
        .join(Projeto, Projeto.id == AtletaHistorico.projeto_id)
        .join(Equipe, Equipe.id == AtletaHistorico.equipe_id)
        .join(Usuario, Usuario.id == AtletaHistorico.responsavel_id)
        .filter(AtletaHistorico.atleta_id == atleta.id)
        .order_by(AtletaHistorico.created_at.desc())
        .all()
    )

    historico = []
    for h, status_nome, projeto_nome, equipe_nome, responsavel_nome in historico_rows:
        historico.append({
            "status": status_nome.title(),
            "motivo": h.motivo,
            "projeto": projeto_nome,
            "equipe": equipe_nome,
            "responsavel": responsavel_nome.title(),
            "created_at": h.created_at.strftime("%d/%m/%Y %H:%M"),
        })

    return render_template("visualizar_atleta.html", atleta=dados_atleta, endereco=dados_endereco, historico=historico, dados_pessoais_atleta= dados_pessoais_atleta, can_edit=can_edit)

# Cria o banco de dados e as tabelas, se ainda não existirem, dentro do contexto da aplicação
# with app.app_context():
#     create_initial_admin()

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Excluir após sistema estável
        create_initial_admin()
    app.run(debug=True)
