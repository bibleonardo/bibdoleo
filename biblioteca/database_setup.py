from models import db, create_app, Usuario, Livro

app = create_app()

with app.app_context():
    db.create_all()

    # Adicionar dados iniciais
    if not Livro.query.first():
        livros = [
            Livro(
                titulo="Python para Todos",
                autor="John Doe",
                categoria="Programação",
                descricao="Este livro aborda conceitos básicos e avançados de Python.",
                disponibilidade=True
            ),
            Livro(
                titulo="Flask Avançado",
                autor="Jane Roe",
                categoria="Web Development",
                descricao="Guia completo para construir aplicações web com Flask.",
                disponibilidade=True
            ),
            Livro(
                titulo="Banco de Dados",
                autor="Alice Smith",
                categoria="Database",
                descricao="Uma introdução prática aos bancos de dados e SQL.",
                disponibilidade=False
            ),
        ]
        db.session.add_all(livros)
        db.session.commit()

    print("Banco de dados configurado com livros detalhados!")

with app.app_context():
    if not Usuario.query.filter_by(email="leonardo@bibdoleonardo.com").first():
        leandro = Usuario(nome="Leonardo", email="leonardo@bibdoleonardo.com", senha="123456")
        db.session.add(leandro)
        db.session.commit()
        print("Usuário Leonardo criado com sucesso!")