import os

from dotenv import load_dotenv
from flask import g
from flask import Flask

from .extensions import db
from .utils import get_current_collection, store_collection_from_request


def create_app():
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)

    app.config["FEN_PRESETS"] = {
        "preset_1": {
            "label": "Mattsetzen mit Dame",
            "description": "",
            "fen": "6Q1/8/8/4k3/1K6/8/8/8 w - - 0 1",
        },
        "preset_2": {
            "label": "Mattsetzen mit Turm",
            "description": "",
            "fen": "8/2k5/8/8/6K1/8/8/6R1 w - - 0 0",
        },
        "preset_3": {
            "label": "Bauernendspiel",
            "description": "",
            "fen": "3k4/8/8/8/8/8/4P3/3K4 w - - 0 1",
        },
    }

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

    @app.before_request
    def persist_collection_parameter():
        g.collection = store_collection_from_request()

    @app.context_processor
    def inject_collection():
        return {"current_collection": get_current_collection()}

    from .auth.routes import auth_bp
    from .game.routes import game_bp
    from .main.routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(game_bp, url_prefix="/game")

    with app.app_context():
        db.create_all()

    return app
