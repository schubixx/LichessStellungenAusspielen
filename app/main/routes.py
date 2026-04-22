from flask import Blueprint, redirect, render_template, session, url_for, current_app
from app.utils import get_current_collection
from ..config import FEN_PRESETS

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    collection = get_current_collection()
    presets = current_app.config["FEN_PRESETS"]

    if not session.get("lichess_user_id"):
        return render_template(
            "index.html",
            collection=collection,
            presets=presets
        )

    return redirect(url_for("game.select_fen"))