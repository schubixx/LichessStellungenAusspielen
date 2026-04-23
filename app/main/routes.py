from flask import Blueprint, flash, redirect, render_template, session, url_for, current_app, request
from app.utils import get_current_collection, generate_collection_id, is_admin
from ..extensions import db 
from app.models import Position

main_bp = Blueprint("main", __name__)

@main_bp.route("/new-collection", methods=["GET", "POST"])
def new_collection():
    if not is_admin():
        return "Nicht erlaubt", 403

    if request.method == "POST":
        collection_id = generate_collection_id()
        valid_rows = 0

        for i in range(8):
            title = (request.form.get(f"title_{i}") or "").strip()
            fen = (request.form.get(f"fen_{i}") or "").strip()
            ai_level_raw = (request.form.get(f"ai_level_{i}") or "").strip()
            color = (request.form.get(f"color_{i}") or "random").strip().lower()
            clock_limit_raw = (request.form.get(f"clock_limit_{i}") or "").strip()
            clock_increment_raw = (request.form.get(f"clock_increment_{i}") or "").strip()

            if not fen:
                continue

            try:
                ai_level = int(ai_level_raw)
            except ValueError:
                flash(f"Stellung {i + 1}: Level muss eine ganze Zahl sein.", "error")
                return render_template("new_collection.html"), 400

            try:
                clock_limit = int(clock_limit_raw)
            except ValueError:
                flash(f"Stellung {i + 1}: Clock Limit muss eine ganze Zahl sein.", "error")
                return render_template("new_collection.html"), 400

            try:
                clock_increment = int(clock_increment_raw)
            except ValueError:
                flash(f"Stellung {i + 1}: Clock Increment muss eine ganze Zahl sein.", "error")
                return render_template("new_collection.html"), 400

            if ai_level < 1 or ai_level > 8:
                flash(f"Stellung {i + 1}: Level ist nur von 1 bis 8 erlaubt.", "error")
                return render_template("new_collection.html"), 400

            if clock_limit < 0 or clock_limit > 10800:
                flash(f"Stellung {i + 1}: Clock Limit ist nur von 0 bis 10800 erlaubt.", "error")
                return render_template("new_collection.html"), 400

            if clock_increment < 0 or clock_increment > 60:
                flash(f"Stellung {i + 1}: Clock Increment ist nur von 0 bis 60 erlaubt.", "error")
                return render_template("new_collection.html"), 400

            if color not in {"white", "black", "random"}:
                flash(f"Stellung {i + 1}: Color muss white, black oder random sein.", "error")
                return render_template("new_collection.html"), 400

            pos = Position(
                collection_id=collection_id,
                title=title or f"Stellung {i + 1}",
                fen=fen,
                ai_level=ai_level,
                color=color,
                clock_limit=clock_limit,
                clock_increment=clock_increment,
            )
            db.session.add(pos)
            valid_rows += 1

        if valid_rows == 0:
            flash("Bitte mindestens eine Stellung mit FEN eingeben.", "error")
            return render_template("new_collection.html"), 400

        db.session.commit()
        return render_template("collection_created.html", collection_id=collection_id)

    return render_template("new_collection.html")

@main_bp.route("/")
def index():
    collection = get_current_collection()

    if not session.get("lichess_user_id"):
        return render_template(
            "index.html",
            collection=collection
        )

    return redirect(url_for("game.select_fen"))