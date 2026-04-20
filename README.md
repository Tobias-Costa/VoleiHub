# 🏐 VoleiHub

Sistema web completo para gestão de projetos esportivos de voleibol.  
O **VoleiHub** permite o gerenciamento de atletas, equipes, projetos e conteúdos (blog), com controle de acesso baseado em perfis de usuário.

---

## 📌 Visão Geral

O VoleiHub foi desenvolvido para facilitar a organização de projetos esportivos, oferecendo:

- Gestão de atletas
- Controle de equipes
- Organização de projetos
- Registro de histórico dos atletas
- Gerenciamento de endereços
- Sistema de blog integrado
- Controle de permissões por perfil

---

## 🚀 Funcionalidades

### 👤 Usuários e Permissões
- **Administrador**
  - Acesso total ao sistema
- **Coordenador**
  - Gerencia projetos sob sua responsabilidade
- **Técnico**
  - Gerencia equipes e atletas vinculados

---

### 🏆 Projetos
- Criação e visualização de projetos
- Associação com equipes
- Controle de status (ativo/inativo)
- Visualização detalhada com:
  - Número de equipes
  - Número de atletas
  - Responsável

---

### 👥 Equipes
- Cadastro e visualização de equipes
- Associação com projetos
- Definição de técnico responsável
- Listagem de atletas por equipe

---

### 🧍 Atletas
- Cadastro completo de atletas
- Dados:
  - Pessoais
  - Esportivos (modalidade, posição, nível, etc.)
  - Contato
- Histórico completo de movimentações
- Controle de status

---

### 📍 Endereço de Atletas
- Cadastro e edição de endereço
- Validação de permissões
- Associação com cidade e estado

---

### 📝 Blog Interno
- Criação de posts
- Upload de imagens
- Edição e exclusão
- Feed com posts ordenados por data
- Controle de permissões para edição

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python + Flask
- **ORM:** SQLAlchemy
- **Frontend:** Jinja2 (Templates)
- **Banco de Dados:** SQLite (ou compatível)
- **Autenticação:** Flask-Login
- **Upload de arquivos:** Werkzeug

---

## ⚙️ Instalação

Siga os passos abaixo para rodar o projeto localmente.

---

### 🧩 1. Pré-requisitos

Certifique-se de ter instalado:

- Python 3.10 ou superior
- pip
- Git (opcional)

Verifique com:

```bash
python --version
pip --version
git --version
```

### 📥 2. Clonar o repositório

git clone https://github.com/seu-usuario/voleiHub.git  
cd voleiHub  

---

### 🧪 3. Criar ambiente virtual

python -m venv venv  

---

### ▶️ 4. Ativar o ambiente virtual

#### Windows

venv\Scripts\activate  

#### Linux / Mac

source venv/bin/activate  

---

### 📦 5. Instalar dependências

pip install -r requirements.txt  

---

### 🔐 6. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

ADMIN_EMAIL=admin@email.com  
ADMIN_PASSWORD=123456  

---

### 🗄️ 7. Executar o projeto

python app.py  

Na primeira execução, o sistema irá:

- Criar o banco de dados automaticamente  
- Criar o usuário administrador inicial  

---

### 🌐 8. Acessar a aplicação

http://127.0.0.1:5000  
