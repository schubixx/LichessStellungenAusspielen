import os

from dotenv import load_dotenv
from flask import Flask

from .extensions import db


def create_app():
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///lichess_tokens.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["LICHESS_CLIENT_ID"] = os.getenv("LICHESS_CLIENT_ID", "")
    app.config["LICHESS_REDIRECT_URI"] = os.getenv(
        "LICHESS_REDIRECT_URI", "http://127.0.0.1:5000/auth/callback"
    )
    app.config["LICHESS_OAUTH_AUTHORIZE_URL"] = "https://lichess.org/oauth"
    app.config["LICHESS_OAUTH_TOKEN_URL"] = "https://lichess.org/api/token"
    app.config["LICHESS_ACCOUNT_URL"] = "https://lichess.org/api/account"
    app.config["LICHESS_CHALLENGE_AI_URL"] = "https://lichess.org/api/challenge/ai"

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    from .auth.routes import auth_bp
    from .game.routes import game_bp
    from .main.routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(game_bp, url_prefix="/game")

    with app.app_context():
        db.create_all()

    return app
