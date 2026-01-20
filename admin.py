from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request, abort
from flask_admin.form import Select2Field
from flask_login import current_user
from models import *


#Configurando acessibilidade da página admin e models
class AdminIndex(AdminIndexView):

    def is_accessible(self):
        # NÃO logado → barra
        if not current_user.is_authenticated:
            return False

        # Logado mas NÃO admin → barra
        if not current_user.is_admin:
            abort(403)

        # Admin → entra
        return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login", next=request.url))

class AdminModelView(ModelView):

    column_display_pk = True

    def is_visible(self):
        return current_user.is_authenticated and current_user.is_admin

    def is_accessible(self):
        # Não logado → redireciona para login
        if not current_user.is_authenticated:
            return False

        # Logado mas não é admin → 403
        if not current_user.is_admin:
            abort(403)

        return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class ProjetoAdmin(AdminModelView):
    # Colunas que aparecem no formulário
    form_columns = [
        "nome_projeto",
        "descricao",
        "is_active",
        "cidade_id",
        "responsavel_id",
    ]

    # Campos do formulário com Select2Field
    form_extra_fields = {
        "cidade_id": Select2Field(
            "Cidade",
            coerce=int,
            choices=lambda: [(c.id, c.nome_cidade) for c in Cidade.query.order_by(Cidade.nome_cidade).all()]
        ),
        "responsavel_id": Select2Field(
            "Responsável",
            coerce=int,
            choices=lambda: [(u.id, f"{u.firstname_usuario} {u.lastname_usuario}") for u in Usuario.query.all()]
        ),
    }

    # Colunas que aparecem na lista
    column_list = [
        "id",
        "nome_projeto",
        "descricao",
        "is_active",
        "cidade_id",
        "responsavel_id",
        "created_at",
        "last_edited",
    ]

    # Formatadores para mostrar os nomes legíveis
    column_formatters = {
        "cidade_id": lambda v, c, m, p: Cidade.query.get(m.cidade_id).nome_cidade if m.cidade_id else "",
        "responsavel_id": lambda v, c, m, p: f"{Usuario.query.get(m.responsavel_id).firstname_usuario} {Usuario.query.get(m.responsavel_id).lastname_usuario}" if m.responsavel_id else "",
    }

class AtletaAdmin(AdminModelView):

    column_list = [
        "id",
        "firstname_atleta",
        "lastname_atleta",
        "registro_cuca",  # Adicionado à listagem
        "registro_cbv",   # Adicionado à listagem
        "email",
        "equipe_id",
        "status_id",
        "created_at",
    ]

    column_labels = {
        "firstname_atleta": "Nome",
        "lastname_atleta": "Sobrenome",
        "registro_cuca": "Registro CUCA", # Rótulo amigável
        "registro_cbv": "Registro CBV",   # Rótulo amigável
        "equipe_id": "Equipe",
        "status_id": "Status",
        "cpf": "CPF",
        "rg": "RG"
    }

    column_formatters = {
        "equipe_id": lambda v, c, m, p:
            Equipe.query.get(m.equipe_id).nome_equipe if m.equipe_id else "-",
        "status_id": lambda v, c, m, p:
            Status.query.get(m.status_id).nome_status if m.status_id else "-"
    }

    form_columns = [
        "firstname_atleta",
        "lastname_atleta",
        "email",
        "rg",
        "cpf",
        "registro_cuca", # Campo para preencher no Admin
        "registro_cbv",  # Campo para preencher no Admin
        "data_nascimento",
        "telefone1",
        "telefone2",
        "equipe_id",
        "sexo_id",
        "modalidade_id",
        "posicao_id",
        "categoria_id",
        "nivel_id",
        "status_id",
    ]

    form_extra_fields = {
        "equipe_id": Select2Field(
            "Equipe",
            coerce=int,
            choices=lambda: [
                (e.id, e.nome_equipe)
                for e in Equipe.query.order_by(Equipe.nome_equipe).all()
            ]
        ),
        "sexo_id": Select2Field(
            "Sexo",
            coerce=int,
            choices=lambda: [(s.id, s.sexo) for s in Sexo.query.all()]
        ),
        "modalidade_id": Select2Field(
            "Modalidade",
            coerce=int,
            choices=lambda: [(m.id, m.nome_modalidade) for m in Modalidade.query.all()]
        ),
        "posicao_id": Select2Field(
            "Posição",
            coerce=int,
            choices=lambda: [(p.id, p.nome_posicao) for p in Posicao.query.all()]
        ),
        "categoria_id": Select2Field(
            "Categoria",
            coerce=int,
            choices=lambda: [(c.id, c.nome_categoria) for c in Categoria.query.all()]
        ),
        "nivel_id": Select2Field(
            "Nível",
            coerce=int,
            choices=lambda: [(n.id, n.nome_nivel) for n in Nivel.query.all()]
        ),
        "status_id": Select2Field(
            "Status",
            coerce=int,
            choices=lambda: [(s.id, s.nome_status) for s in Status.query.all()]
        ),
    }

class EquipeAdmin(AdminModelView):

    form_columns = ["nome_equipe", "projeto_id", "tecnico_id", "is_active"]

    form_extra_fields = {
        "projeto_id": Select2Field(
            "Projeto",
            coerce=int,
            choices=lambda: [(p.id, p.nome_projeto) for p in Projeto.query.all()]
        ),
        "tecnico_id": Select2Field(
            "Técnico",
            coerce=int,
            choices=lambda: [
                (u.id, f"{u.firstname_usuario} {u.lastname_usuario}")
                for u in Usuario.query.all()
            ]
        ),
    }

class CidadeAdmin(AdminModelView):

    column_list = ["id", "nome_cidade", "estado_id"]

    column_formatters = {
        "estado_id": lambda v, c, m, p: Estado.query.get(m.estado_id).nome_estado if m.estado_id else ""
    }

    form_columns = ["nome_cidade", "estado_id"]

    form_extra_fields = {
        "estado_id": Select2Field(
            "Estado",
            coerce=int,
            choices=lambda: [(e.id, e.nome_estado) for e in Estado.query.all()]
        )
    }

class TransferenciaAdmin(AdminModelView):

    column_list = [
        "id",
        "atleta_id",
        "equipe_origem_id",
        "equipe_destino_id",
        "responsavel_id",
        "created_at",
    ]

    column_formatters = {
        "atleta_id": lambda v, c, m, p:
            f"{Atleta.query.get(m.atleta_id).firstname_atleta} "
            f"{Atleta.query.get(m.atleta_id).lastname_atleta}",
        "equipe_origem_id": lambda v, c, m, p:
            Equipe.query.get(m.equipe_origem_id).nome_equipe,
        "equipe_destino_id": lambda v, c, m, p:
            Equipe.query.get(m.equipe_destino_id).nome_equipe,
        "responsavel_id": lambda v, c, m, p:
            f"{Usuario.query.get(m.responsavel_id).firstname_usuario}"
    }

    form_columns = [
        "atleta_id",
        "projeto_origem_id",
        "equipe_origem_id",
        "projeto_destino_id",
        "equipe_destino_id",
        "motivo",
        "responsavel_id",
    ]

    form_extra_fields = {
        "atleta_id": Select2Field(
            "Atleta",
            coerce=int,
            choices=lambda: [
                (a.id, f"{a.firstname_atleta} {a.lastname_atleta}")
                for a in Atleta.query.all()
            ]
        ),
        "projeto_origem_id": Select2Field(
            "Projeto Origem",
            coerce=int,
            choices=lambda: [(p.id, p.nome_projeto) for p in Projeto.query.all()]
        ),
        "equipe_origem_id": Select2Field(
            "Equipe Origem",
            coerce=int,
            choices=lambda: [(e.id, e.nome_equipe) for e in Equipe.query.all()]
        ),
        "projeto_destino_id": Select2Field(
            "Projeto Destino",
            coerce=int,
            choices=lambda: [(p.id, p.nome_projeto) for p in Projeto.query.all()]
        ),
        "equipe_destino_id": Select2Field(
            "Equipe Destino",
            coerce=int,
            choices=lambda: [(e.id, e.nome_equipe) for e in Equipe.query.all()]
        ),
        "responsavel_id": Select2Field(
            "Responsável",
            coerce=int,
            choices=lambda: [
                (u.id, f"{u.firstname_usuario} {u.lastname_usuario}")
                for u in Usuario.query.all()
            ]
        ),
    }

class AtletaHistoricoAdmin(AdminModelView):

    column_list = [
        "id",
        "atleta_id",
        "projeto_id",
        "equipe_id",
        "status_id",
        "motivo",
        "created_at",
    ]

    column_formatters = {
        "atleta_id": lambda v, c, m, p:
            f"{Atleta.query.get(m.atleta_id).firstname_atleta} "
            f"{Atleta.query.get(m.atleta_id).lastname_atleta}",
        "projeto_id": lambda v, c, m, p:
            Projeto.query.get(m.projeto_id).nome_projeto,
        "equipe_id": lambda v, c, m, p:
            Equipe.query.get(m.equipe_id).nome_equipe,
        "status_id": lambda v, c, m, p:
            Status.query.get(m.status_id).nome_status,
    }

    form_columns = [
        "atleta_id",
        "projeto_id",
        "equipe_id",
        "status_id",
        "motivo",
        "responsavel_id",
    ]

    form_extra_fields = {
        "atleta_id": Select2Field(
            "Atleta",
            coerce=int,
            choices=lambda: [
                (a.id, f"{a.firstname_atleta} {a.lastname_atleta}")
                for a in Atleta.query.all()
            ]
        ),
        "projeto_id": Select2Field(
            "Projeto",
            coerce=int,
            choices=lambda: [(p.id, p.nome_projeto) for p in Projeto.query.all()]
        ),
        "equipe_id": Select2Field(
            "Equipe",
            coerce=int,
            choices=lambda: [(e.id, e.nome_equipe) for e in Equipe.query.all()]
        ),
        "status_id": Select2Field(
            "Status",
            coerce=int,
            choices=lambda: [(s.id, s.nome_status) for s in Status.query.all()]
        ),
        "responsavel_id": Select2Field(
            "Responsável",
            coerce=int,
            choices=lambda: [
                (u.id, f"{u.firstname_usuario} {u.lastname_usuario}")
                for u in Usuario.query.all()
            ]
        ),
    }

class AtletaEnderecoAdmin(AdminModelView):

    column_list = [
        "id",
        "atleta_id",
        "logradouro",
        "numero",
        "bairro",
        "cidade_id",
        "cep",
        "created_at",
    ]

    column_labels = {
        "atleta_id": "Atleta",
        "cidade_id": "Cidade",
    }

    column_formatters = {
        "atleta_id": lambda v, c, m, p:
            f"{Atleta.query.get(m.atleta_id).firstname_atleta} "
            f"{Atleta.query.get(m.atleta_id).lastname_atleta}"
            if m.atleta_id else "-",
        "cidade_id": lambda v, c, m, p:
            Cidade.query.get(m.cidade_id).nome_cidade if m.cidade_id else "-"
    }

    form_columns = [
        "atleta_id",
        "logradouro",
        "numero",
        "complemento",
        "bairro",
        "cidade_id",
        "cep",
    ]

    form_extra_fields = {
        "atleta_id": Select2Field(
            "Atleta",
            coerce=int,
            choices=lambda: [
                (a.id, f"{a.firstname_atleta} {a.lastname_atleta}")
                for a in Atleta.query.all()
            ]
        ),
        "cidade_id": Select2Field(
            "Cidade",
            coerce=int,
            choices=lambda: [
                (c.id, c.nome_cidade)
                for c in Cidade.query.all()
            ]
        ),
    }



def init_admin(app):
    admin = Admin(app, name="Administração", index_view=AdminIndex(url="/admin"))

    admin.add_view(AdminModelView(Usuario, db.session))
    admin.add_view(ProjetoAdmin(Projeto, db.session))
    admin.add_view(EquipeAdmin(Equipe, db.session))
    admin.add_view(AtletaAdmin(Atleta, db.session))
    admin.add_view(AtletaEnderecoAdmin(AtletaEndereco, db.session))
    admin.add_view(AtletaHistoricoAdmin(AtletaHistorico, db.session))
    admin.add_view(TransferenciaAdmin(Transferencia, db.session))
    admin.add_view(AdminModelView(Estado, db.session))
    admin.add_view(CidadeAdmin(Cidade, db.session))
    admin.add_view(AdminModelView(Modalidade, db.session))
    admin.add_view(AdminModelView(Posicao, db.session))
    admin.add_view(AdminModelView(Categoria, db.session))
    admin.add_view(AdminModelView(Nivel, db.session))
    admin.add_view(AdminModelView(Status, db.session))
    admin.add_view(AdminModelView(Sexo, db.session))