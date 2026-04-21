from flask import Blueprint, redirect, render_template, session, url_for

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if session.get("lichess_user_id"):
        return redirect(url_for("game.select_fen"))
    return render_template("index.html")
