from flask import render_template, request, redirect, url_for, session, flash
from functools import wraps
from models import db, Usuario, Livro, Carrinho
from werkzeug.security import generate_password_hash, check_password_hash


# Verificação de autenticação
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Faça login para acessar esta página.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def configure_routes(app):
    @app.route("/")
    def home():
        # Redireciona para a página de login
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            senha = request.form["senha"]
            usuario = Usuario.query.filter_by(email=email, senha=senha).first()
            if usuario:
                session["usuario_id"] = usuario.id
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for("index"))
            else:
                return render_template("login.html", erro="E-mail ou senha incorretos.")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.pop("usuario_id", None)
        flash("Logout realizado com sucesso!", "success")
        return redirect(url_for("login"))

    @app.route("/minha_conta", methods=["GET", "POST"])
    @login_required
    def minha_conta():
        usuario_id = session.get("usuario_id")
        usuario = Usuario.query.get_or_404(usuario_id)

        if request.method == "POST":
            novo_email = request.form.get("email")
            senha_atual = request.form.get("senha_atual")
            nova_senha = request.form.get("nova_senha")

            # Valida a senha atual antes de qualquer alteração
            if not check_password_hash(usuario.senha, senha_atual):
                flash("Senha atual incorreta. Nenhuma alteração foi feita.", "danger")
                return redirect(url_for("minha_conta"))

            # Atualizar e-mail se for diferente do atual
            if novo_email and novo_email != usuario.email:
                usuario.email = novo_email

            # Atualizar senha se uma nova senha for fornecida
            if nova_senha:
                usuario.senha = generate_password_hash(nova_senha)

            # Salvar alterações no banco de dados
            db.session.commit()
            flash("Informações atualizadas com sucesso!", "success")
            return redirect(url_for("minha_conta"))

        return render_template("minha_conta.html", usuario=usuario)


    @app.route("/index")
    @login_required
    def index():
        livros = Livro.query.all()
        return render_template("index.html", livros=livros)

    @app.route("/buscar", methods=["GET"])
    @login_required
    def buscar():
        termo = request.args.get("q", "")
        livros = Livro.query.filter(Livro.titulo.contains(termo)).all()
        return render_template("search.html", livros=livros, termo=termo)

    @app.route("/adicionar/<int:livro_id>")
    @login_required
    def adicionar_ao_carrinho(livro_id):
        livro = Livro.query.get_or_404(livro_id)
        usuario_id = session.get("usuario_id")

        # Verificar se o livro já está no carrinho
        item_existente = Carrinho.query.filter_by(usuario_id=usuario_id, livro_id=livro.id).first()
        if item_existente:
            flash("O livro já está no carrinho.", "info")
        else:
            # Adicionar o livro ao carrinho
            novo_item = Carrinho(usuario_id=usuario_id, livro_id=livro.id)
            db.session.add(novo_item)
            db.session.commit()
            flash(f"{livro.titulo} foi adicionado ao carrinho.", "success")

        return redirect(url_for("carrinho"))

    @app.route("/carrinho")
    @login_required
    def carrinho():
        itens = Carrinho.query.all()
        return render_template("cart.html", itens=itens)

    @app.route("/remover/<int:livro_id>")
    @login_required
    def remover_carrinho(livro_id):
        usuario_id = session.get("usuario_id")
        item = Carrinho.query.filter_by(usuario_id=usuario_id, livro_id=livro_id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            flash("Livro removido do carrinho.", "success")
        else:
            flash("Livro não encontrado no carrinho.", "error")
        return redirect(url_for("carrinho"))


    @app.route("/finalizar_compra", methods=["POST"])
    @login_required
    def finalizar_compra():
        # Obtém o usuário logado
        usuario_id = session.get("usuario_id")

        # Obtém todos os itens no carrinho do usuário
        itens_carrinho = Carrinho.query.filter_by(usuario_id=usuario_id).all()

        if not itens_carrinho:
            flash("Seu carrinho está vazio. Adicione itens antes de finalizar a compra.", "warning")
            return redirect(url_for("carrinho"))

        # Marca os livros no carrinho como indisponíveis
        for item in itens_carrinho:
            livro = Livro.query.get(item.livro_id)
            if livro and livro.disponibilidade:
                livro.disponibilidade = False
                db.session.add(livro)
            # Remove o item do carrinho após finalizar a compra
            db.session.delete(item)

        db.session.commit()
        flash("Compra finalizada com sucesso! Livros marcados como indisponíveis.", "success")
        return redirect(url_for("index"))


    @app.route("/detalhes/<int:livro_id>")
    @login_required
    def detalhes(livro_id):
        livro = Livro.query.get_or_404(livro_id)
        return render_template("details.html", livro=livro)

    @app.route("/checkout", methods=["GET", "POST"])
    @login_required
    def checkout():
        if request.method == "POST":
            flash("Compra finalizada com sucesso!", "success")
            return redirect(url_for("index"))
        return render_template("checkout.html")
