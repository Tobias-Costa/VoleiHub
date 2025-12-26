from datetime import datetime
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 1. Defina a convenção de nomes
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# 2. Passe a convenção para o MetaData
metadata = MetaData(naming_convention=convention)

# 3. Inicialize o DB com esse metadata
db = SQLAlchemy(metadata=metadata)

class Usuario(db.Model):
    __tablename__ = 'usuarios' 

    id = db.Column(db.Integer, primary_key=True)
    # profile_picture_url = Column(String(255), nullable=True) 
    firstname_usuario = db.Column(db.String(80), nullable=False)
    lastname_usuario = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    telefone1 = db.Column(db.String(20), nullable=False)
    telefone2 = db.Column(db.String(20), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_coord = db.Column(db.Boolean, default=False, nullable=False)
    is_tecnico = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now) 
    last_edited = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now) 
    
    def __repr__(self):
        return f'<Usuario {self.nome_usuario} ({self.email})>'

class Estado(db.Model):
    __tablename__ = 'estados' 

    id = db.Column(db.Integer, primary_key=True)
    nome_estado = db.Column(db.String(40), unique=True, nullable=False)
    abreviacao = db.Column(db.String(10), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Estado {self.nome_estado}>'
    
class Cidade(db.Model):
    __tablename__ = 'cidades' 

    id = db.Column(db.Integer, primary_key=True)
    nome_cidade = db.Column(db.String(40), unique=True, nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estados.id'), nullable=False)
    
    def __repr__(self):
        return f'<Cidade {self.nome_cidade}>'
    
class Projeto(db.Model):
    __tablename__ = 'projetos' 

    id = db.Column(db.Integer, primary_key=True)
    nome_projeto = db.Column(db.String(80), unique=True, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    cidade_id = db.Column(db.Integer, db.ForeignKey('cidades.id'), nullable=False)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now) 
    last_edited = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now) 
     
    def __repr__(self):
        return f'<Projeto {self.nome_projeto} (Is_active:{self.is_active})>'
    
class Equipe(db.Model):
    __tablename__ = 'equipes' 

    id = db.Column(db.Integer, primary_key=True)
    nome_equipe = db.Column(db.String(80), unique=True, nullable=False)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projetos.id'), nullable=False)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now) 
    last_edited = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now) 
     
    def __repr__(self):
        return f'<Equipe {self.nome_equipe} (ProjetoID:{self.projeto_id} - Is_active:{self.is_active})>'

class Modalidade(db.Model):
    __tablename__ = 'modalidades' 

    id = db.Column(db.Integer, primary_key=True)
    nome_modalidade = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'<Modalidade {self.nome_modalidade}>'
    
class Posicao(db.Model):
    __tablename__ = 'posicoes' 

    id = db.Column(db.Integer, primary_key=True)
    nome_posicao = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'<Posicao {self.nome_posicao}>'
    
class Categoria(db.Model):
    __tablename__ = 'categorias' 

    id = db.Column(db.Integer, primary_key=True)
    nome_categoria = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'<Categoria {self.nome_categoria}>'
    
class Nivel(db.Model):
    __tablename__ = 'niveis' 

    id = db.Column(db.Integer, primary_key=True)
    nome_nivel = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'<Nivel {self.nome_nivel}>'
    
class Status(db.Model):
    __tablename__ = 'status' 

    id = db.Column(db.Integer, primary_key=True)
    nome_status = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'<Nivel {self.nome_status}>'

class Sexo(db.Model):
    __tablename__ = 'sexos' 

    id = db.Column(db.Integer, primary_key=True)
    sexo = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        return f'<Sexo {self.sexo} ID:{self.id}>'

class Atleta(db.Model):
    __tablename__ = 'atletas' 

    id = db.Column(db.Integer, primary_key=True)
    # profile_picture_url = Column(String(255), nullable=True) 
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipes.id'), nullable=False)
    firstname_atleta = db.Column(db.String(80), nullable=False)
    lastname_atleta = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rg = db.Column(db.String(20), unique=True, nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    data_nascimento =  db.Column(db.Date, nullable=False)
    telefone1 = db.Column(db.String(20), nullable=False)
    telefone2 = db.Column(db.String(20), nullable=True)
    sexo_id = db.Column(db.Integer, db.ForeignKey('sexos.id'), nullable=False)
    modalidade_id = db.Column(db.Integer, db.ForeignKey('modalidades.id'), nullable=False)
    posicao_id = db.Column(db.Integer, db.ForeignKey('posicoes.id'), nullable=False)
    categorias_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    nivel_id = db.Column(db.Integer, db.ForeignKey('niveis.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now) 
    last_edited = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now) 
     
    def __repr__(self):
        return f'<Atleta {self.nome_atleta} (EquipeID:{self.equipe_id} - StatusID:{self.status_id})>'
    
class AtletaEndereco(db.Model):
    __tablename__ = 'enderecos'

    id = db.Column(db.Integer, primary_key=True)
    atleta_id = db.Column(db.Integer, db.ForeignKey('atletas.id'), nullable=False)
    logradouro = db.Column(db.String(255), nullable=False)
    numero = db.Column(db.String(20), nullable=False) # Armazenar como string para incluir 's/n', 'apto 101'
    complemento = db.Column(db.String(100), nullable=True)
    bairro = db.Column(db.String(100), nullable=False)
    cidade_id = db.Column(db.Integer, db.ForeignKey('cidades.id'), nullable=False)
    cep = db.Column(db.String(8), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now) 
    last_edited = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now) 

    def __repr__(self):
        return f'<AtletaEndereco {self.logradouro} (AtletaID:{self.atleta_id})>'

class Transferencia(db.Model):
    __tablename__ = 'transferencias'

    id = db.Column(db.Integer, primary_key=True)
    atleta_id = db.Column(db.Integer, db.ForeignKey('atletas.id'), nullable=False)
    projeto_origem_id = db.Column(db.Integer, db.ForeignKey('projetos.id'), nullable=False)
    equipe_origem_id = db.Column(db.Integer, db.ForeignKey('equipes.id'), nullable=False)
    projeto_destino_id = db.Column(db.Integer, db.ForeignKey('projetos.id'), nullable=False)
    equipe_destino_id = db.Column(db.Integer, db.ForeignKey('equipes.id'), nullable=False)
    motivo = db.Column(db.String(255), nullable=True)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now) 

    def __repr__(self):
        return f'<Transferencia {self.projeto_origem_id}/{self.equipe_origem_id} -> {self.projeto_destino_id}/{self.equipe_destino_id} (AtletaID:{self.atleta_id})>'

class AtletaHistorico(db.Model):
    __tablename__ = 'historicos'

    id = db.Column(db.Integer, primary_key=True)
    atleta_id = db.Column(db.Integer, db.ForeignKey('atletas.id'), nullable=False)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projetos.id'), nullable=False)
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipes.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    motivo = db.Column(db.String(255), nullable=True)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now) 
    
    def __repr__(self):
        return f'<AtletaHistorico Status:{self.status_id}  (AtletaID:{self.atleta_id})>'