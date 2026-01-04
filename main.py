from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, DateField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from flask import Flask, request, redirect, url_for, render_template, flash
from sqlalchemy import or_
from flask_migrate import Migrate
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

def hash(txt):
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

@lm.user_loader
def user_loader(id):
    usuario = Usuario.query.get_or_404(id)
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
            password = hash(form.password.data),
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
        user = db.session.query(Usuario).filter_by(email=email, password=hash(password)).first()
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

        transferencias.append({"id":transferencia.id, "proj_origem":proj_origem.title(), "eq_origem":eq_origem.title(), "proj_destino":proj_destino.title(), "eq_destino":eq_destino.title(), "nome_atleta":atleta.title(), "responsavel":responsavel.title()})

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

        projetos.append({"id":projeto.id, "nome":projeto.nome_projeto.title(), "cidade":projeto_cidade.title(), "n_equipes":projeto_equipes, "n_atletas":projeto_atletas, "is_active":bool(projeto.is_active)})

    cidades = [{"id":c.id, "nome_cidade":c.nome_cidade.title()} for c in cidades_query.all()]

    return render_template('dashboard.html', n_projetos_ativos=total_projetos_ativos, n_equipes_ativas=total_equipes_ativas, n_atletas=total_atletas, atletas_ativos=atletas_ativos, atletas_lesionados=atletas_lesionados, atletas_suspensos=atletas_suspensos, transferencias=transferencias, projetos=projetos, cidades=cidades)

@app.route('/criar/projeto/', methods=["GET","POST"])
@login_required
def criar_projeto():
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
    form.responsavel_id.choices = [
        (usuario.id, f"{usuario.firstname_usuario.title()} {usuario.lastname_usuario.title()}")
        for usuario in db.session.query(Usuario).all()
    ]

    # Opção inicial
    form.cidade_id.choices.insert(0, (0, "Selecione uma cidade"))
    form.responsavel_id.choices.insert(0, (0, "Selecione um responsável"))

    if form.validate_on_submit():
        try:
            novo_projeto = Projeto(
                nome_projeto=form.nome_projeto.data.upper(),
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
    projeto_id = request.args.get("projeto_id")
    projeto = Projeto.query.get_or_404(projeto_id)
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
    form.responsavel_id.choices = [
        (usuario.id, f"{usuario.firstname_usuario.title()} {usuario.lastname_usuario.title()}")
        for usuario in db.session.query(Usuario).all()
    ]

    # Opção inicial
    form.cidade_id.choices.insert(0, (0, "Selecione uma cidade"))
    form.responsavel_id.choices.insert(0, (0, "Selecione um responsável"))

    if form.validate_on_submit():
        try:
            projeto.nome_projeto = form.nome_projeto.data.upper()
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
    form = EquipeForm()

    # Popula projetos
    form.projeto_id.choices = [
        (p.id, p.nome_projeto)
        for p in db.session.query(Projeto).filter(Projeto.is_active == True).all()
    ]

    # Popula técnicos
    form.tecnico_id.choices = [
        (u.id, f"{u.firstname_usuario} {u.lastname_usuario}")
        for u in db.session.query(Usuario).filter(or_(Usuario.is_admin==True, Usuario.is_coord==True, Usuario.is_tecnico==True)).all()
    ]

    form.projeto_id.choices.insert(0, (0, "Selecione uma cidade"))
    form.tecnico_id.choices.insert(0, (0, "Selecione um responsável"))

    if form.validate_on_submit():
        nova_equipe = Equipe(
            nome_equipe=form.nome_equipe.data.upper(),
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
    equipe_id = request.args.get('equipe_id')
    equipe = Equipe.query.get_or_404(equipe_id)
    form = EquipeForm(obj=equipe)

    # Popula projetos
    form.projeto_id.choices = [
        (p.id, p.nome_projeto)
        for p in db.session.query(Projeto).filter(Projeto.is_active == True).all()
    ]

    # Popula técnicos
    form.tecnico_id.choices = [
        (u.id, f"{u.firstname_usuario} {u.lastname_usuario}")
        for u in db.session.query(Usuario).filter(or_(Usuario.is_admin==True, Usuario.is_coord==True, Usuario.is_tecnico==True)).all()
    ]

    form.projeto_id.choices.insert(0, (0, "Selecione uma cidade"))
    form.tecnico_id.choices.insert(0, (0, "Selecione um responsável"))

    if form.validate_on_submit():
        try:
            equipe.nome_equipe = form.nome_equipe.data.upper()
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
    form = AtletaForm()

    # Popula selects (SEM relationships)
    # Retorna todas as equipes do projeto do responsável
    #Equipe - Projeto
    form.equipe_id.choices = [(e.id, e.nome_equipe.title()) for e in Equipe.query.all()]

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
            sexo_id=form.sexo_id.data,
            modalidade_id=form.modalidade_id.data,
            posicao_id=form.posicao_id.data,
            categoria_id=form.categoria_id.data,
            nivel_id=form.nivel_id.data,
            status_id=form.status_id.data,
        )

        try:
            db.session.add(novo_atleta)
            db.session.commit()
            flash("Atleta criado com sucesso!", "success")
            # try:
            #     equipe_atleta = db.session.query(Equipe).filter(Equipe.id==novo_atleta.equipe_id).scalar()
            #     projeto_atleta = db.session.query(Projeto).filter(Projeto.id==equipe_atleta.projeto_id).scalar()

            #     NovoStatus = AtletaHistorico(
            #         atleta_id=novo_atleta.id,
            #         projeto_id=projeto_atleta.id,
            #         equipe_atleta=equipe_atleta.id,
            #         status_id=novo_atleta.status_id,
            #         motivo="Adicionado à equipe",
            #         # responsavel_id=Usuário
            #     )
            #     db.session.add(novo_atleta)
            #     db.session.commit()
            #     flash("Atleta criado com sucesso!", "success")
            #     except Exception:
            #     db.session.rollback()
            #     flash("Erro ao cadastrar atleta.", "danger")
            # redireciona para criar endereço
            return redirect(url_for("criar_endereco_atleta", atleta_id=novo_atleta.id))
        except Exception:
            db.session.rollback()
            flash("Erro ao cadastrar atleta.", "danger")

    return render_template("criar_atleta.html", form=form)

@app.route('/editar/atleta/', methods=["GET","POST"])
@login_required
def editar_atleta():
    atleta_id = request.args.get("atleta_id")
    atleta = Atleta.query.get_or_404(atleta_id)
    form = AtletaForm(obj=atleta)

    # Popula selects 
    # Retorna todas as equipes do projeto do responsável
    form.equipe_id.choices = [(e.id, e.nome_equipe.title()) for e in Equipe.query.all()]

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
            atleta.firstname_atleta=form.firstname_atleta.data.upper()
            atleta.lastname_atleta=form.lastname_atleta.data.upper()
            atleta.equipe_id=form.equipe_id.data
            atleta.email=form.email.data.lower()
            atleta.data_nascimento=form.data_nascimento.data
            atleta.telefone1=form.telefone1.data
            atleta.telefone2=form.telefone2.data
            atleta.rg=form.rg.data
            atleta.cpf=form.cpf.data
            atleta.sexo_id=form.sexo_id.data
            atleta.modalidade_id=form.modalidade_id.data
            atleta.posicao_id=form.posicao_id.data
            atleta.categoria_id=form.categoria_id.data
            atleta.nivel_id=form.nivel_id.data
            atleta.status_id=form.status_id.data
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
    atleta_id = request.args.get("atleta_id")
    atleta = Atleta.query.get_or_404(atleta_id)
    form = EnderecoAtletaForm()

    # Popula cidades (SEM relationships)
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
                cep=form.cep.data
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
    atleta_id = request.args.get("atleta_id")
    atleta = Atleta.query.get_or_404(atleta_id)
    endereco_atleta = db.session.query(AtletaEndereco).filter(AtletaEndereco.atleta_id==atleta.id).scalar()
    form = EnderecoAtletaForm(obj=endereco_atleta)

    # Popula cidades (SEM relationships)
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
            endereco_atleta.cep = form.cep.data
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
    projeto_id = request.args.get('projeto_id')

    # Querys principais para a rota
    projeto = db.session.query(Projeto).filter(Projeto.id == projeto_id).scalar()
    dados_projeto = {"id":projeto.id, "nome_projeto":projeto.nome_projeto.title(), "descricao":projeto.descricao, "is_active":bool(projeto.is_active)}

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

        equipes.append({"id":equipe.id, "nome_equipe":equipe.nome_equipe.title(),"tecnico":tecnico_equipe.firstname_usuario.title(), "is_active":bool(equipe.is_active),"total_atletas":total_atletas})

    #Dicionário tabela atletas-equipe
    atletas = []
    for atleta in projeto_atletas:
        equipe_atleta = projeto_equipes.filter(Equipe.id == atleta.equipe_id).scalar()

        modalidade_atleta = modalidades_query.filter(Modalidade.id==atleta.modalidade_id).scalar().nome_modalidade

        posicao_atleta = posicoes_query.filter(Posicao.id==atleta.posicao_id).scalar().nome_posicao

        categoria_atleta = categorias_query.filter(Categoria.id==atleta.categoria_id).scalar().nome_categoria

        nivel_atleta = niveis_query.filter(Nivel.id==atleta.nivel_id).scalar().nome_nivel

        status_atleta = status_query.filter(Status.id==atleta.status_id).scalar().nome_status

        atletas.append({"id":atleta.id, "nome_atleta":atleta.firstname_atleta.title(), "equipe":equipe_atleta.nome_equipe.title(), "modalidade":modalidade_atleta.title(), "posicao":posicao_atleta.title(), "categoria":categoria_atleta.title(), "nivel":nivel_atleta.title(), "status":status_atleta.title()})

    return render_template('visualizar_projeto.html', projeto=dados_projeto, nome_cidade=cidade.nome_cidade.title(), nome_responsavel=nome_responsavel, data_criacao=datetime.strftime(projeto.created_at,"%d/%m/%Y"), n_equipes=projeto_equipes.count(), n_atletas=projeto_atletas.count(), equipes=equipes, atletas=atletas)

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

    dados_equipe = {"id":equipe.id, "nome_equipe":equipe.nome_equipe.title(), "projeto_id":projeto_equipe.id, "projeto":projeto_equipe.nome_projeto.title(),"tecnico":tecnico_nome.title(),"is_active":bool(equipe.is_active),"created_at":datetime.strftime(equipe.created_at,"%d/%m/%Y"),"total_atletas":atletas_equipe.count()}

    #Atletas da equipe
    #Dicionário tabela atletas-equipe
    atletas = []
    for atleta in atletas_equipe:

        modalidade_atleta = modalidades_query.filter(Modalidade.id==atleta.modalidade_id).scalar().nome_modalidade

        posicao_atleta = posicoes_query.filter(Posicao.id==atleta.posicao_id).scalar().nome_posicao

        categoria_atleta = categorias_query.filter(Categoria.id==atleta.categoria_id).scalar().nome_categoria

        nivel_atleta = niveis_query.filter(Nivel.id==atleta.nivel_id).scalar().nome_nivel

        status_atleta = status_query.filter(Status.id==atleta.status_id).scalar().nome_status

        atletas.append({"id":atleta.id, "nome_atleta":atleta.firstname_atleta.title(), "equipe":equipe.nome_equipe.title(), "modalidade":modalidade_atleta.title(), "posicao":posicao_atleta.title(), "categoria":categoria_atleta.title(), "nivel":nivel_atleta.title(), "status":status_atleta.title()})
    

    return render_template("visualizar_equipe.html", equipe=dados_equipe, atletas=atletas)

@app.route('/view/atleta/')
@login_required
def visualizar_atleta():
    atleta_id = request.args.get('atleta_id')

    status_query = db.session.query(Status)
    equipes_query = db.session.query(Equipe)
    projetos_query = db.session.query(Projeto)
    usuarios_query = db.session.query(Usuario)

    atleta = Atleta.query.get_or_404(atleta_id)

    equipe_atleta = equipes_query.filter(Equipe.id==atleta.equipe_id).scalar()

    projeto_atleta = projetos_query.filter(Projeto.id==equipe_atleta.projeto_id).scalar()

    status_atleta = status_query.filter(Status.id==atleta.status_id).scalar()

    historico_atleta = db.session.query(AtletaHistorico).filter(AtletaHistorico.atleta_id==atleta.id).all()

    modalidade_atleta = db.session.query(Modalidade.nome_modalidade).filter(Modalidade.id==atleta.modalidade_id).scalar()
    posicao_atleta = db.session.query(Posicao.nome_posicao).filter(Posicao.id==atleta.posicao_id).scalar()
    categoria_atleta = db.session.query(Categoria.nome_categoria).filter(Categoria.id==atleta.categoria_id).scalar()
    nivel_atleta = db.session.query(Nivel.nome_nivel).filter(Nivel.id==atleta.nivel_id).scalar()
    sexo_atleta = db.session.query(Sexo.sexo).filter(Sexo.id==atleta.sexo_id).scalar()

    nome_atleta = f"{atleta.firstname_atleta} {atleta.lastname_atleta}"

    #Após feita a função de login, organize a tabela a seguir usando update para que os dados sensíveis não vá para o console web
    dados_atleta = {"id":atleta.id, "nome_atleta":nome_atleta.title(), "equipe_id":equipe_atleta.id, "equipe":equipe_atleta.nome_equipe.title(), "projeto": projeto_atleta.nome_projeto.title(), "status":status_atleta.nome_status.title(), "modalidade":modalidade_atleta.title(), "posicao":posicao_atleta.title(), "categoria":categoria_atleta.title(), "nivel":nivel_atleta.title(), "sexo":sexo_atleta.title(), "email":atleta.email, "telefone1":format_telefone(atleta.telefone1), "telefone2":format_telefone(atleta.telefone2), "rg":format_rg(atleta.rg), "cpf":format_cpf(atleta.cpf), "data_nascimento":datetime.strftime(atleta.data_nascimento,"%d/%m/%Y")}

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

        dados_endereco = {"logradouro":endereco_atleta.logradouro.title(), "numero":endereco_atleta.numero, "complemento": endereco_atleta.complemento.title(), "bairro":endereco_atleta.bairro.title(), "cidade":cidade_atleta.nome_cidade.title(), "estado_abreviacao":estado_abr_atleta.upper(), "cep":format_cep(endereco_atleta.cep)}
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
