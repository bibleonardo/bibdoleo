from flask import Flask
from models import db, create_app
from routes import configure_routes

# Criar aplicação Flask
app = create_app()

# Adicionar uma secret key para gerenciar sessões com segurança
app.secret_key = "a4f903fda839f3b50e6d8f837e9bc2cf5b67c1b14a1e459c"

# Configurar rotas
configure_routes(app)

if __name__ == "__main__":
    # Rodar o servidor no modo de desenvolvimento
    app.run(host="0.0.0.0", port=5000, debug=True)