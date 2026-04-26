from flask import Blueprint, flash, redirect, render_template, session, url_for, current_app, request
from app.utils import get_current_collection, generate_collection_id, is_admin
from ..extensions import db 
from app.models import Position, Collection, LichessToken

main_bp = Blueprint("main", __name__)

@main_bp.route("/new-collection", methods=["GET", "POST"])
def new_collection():
    if not is_admin():
        return "Nicht erlaubt", 403

    if request.method == "POST":
        collection_id = generate_collection_id()
        valid_rows = 0

        # Stellungen der Collection speichern   
        for i in range(8):
            title = (request.form.get(f"title_{i}") or "").strip()
            position_description = (request.form.get(f"position_description_{i}") or "").strip()
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
                description=position_description,
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

        # Collection speichern
        description = (request.form.get("description") or "").strip()
        explanation = (request.form.get("explanation") or "").strip()
        user_id = session.get("lichess_user_id")
        token_record = LichessToken.query.filter_by(lichess_user_id=user_id).first()
        creator_name = token_record.lichess_username if token_record else "unbekannt"
        collection_record = Collection(
            collection_id=collection_id,
            creator_name=creator_name,
            description=description,
            explanation=explanation,
        )
        db.session.add(collection_record)


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

@main_bp.route("/collections")
def my_collections():
    if not is_admin():
        return "Nicht erlaubt", 403

    user_id = session.get("lichess_user_id")
    token_record = LichessToken.query.filter_by(lichess_user_id=user_id).first()

    if not token_record:
        return redirect(url_for("main.index"))

    collections = (
        Collection.query
        .filter_by(creator_name=token_record.lichess_username)
        .order_by(Collection.id.desc())
        .all()
    )

    return render_template("collections.html", collections=collections)


@main_bp.route("/collections/<collection_id>/edit", methods=["GET", "POST"])
def edit_collection(collection_id):
    if not is_admin():
        return "Nicht erlaubt", 403

    user_id = session.get("lichess_user_id")
    token_record = LichessToken.query.filter_by(lichess_user_id=user_id).first()

    collection = Collection.query.filter_by(
        collection_id=collection_id,
        creator_name=token_record.lichess_username
    ).first_or_404()

    if request.method == "POST":
        collection.description = (request.form.get("description") or "").strip()
        db.session.commit()

        return redirect(url_for("main.my_collections"))

    positions = (
        Position.query
        .filter_by(collection_id=collection_id)
        .order_by(Position.id.asc())
        .all()
    )

    return render_template(
        "edit_collection.html",
        collection=collection,
        positions=positions
    )


@main_bp.route("/collections/<collection_id>/delete", methods=["POST"])
def delete_collection(collection_id):
    if not is_admin():
        return "Nicht erlaubt", 403

    user_id = session.get("lichess_user_id")
    token_record = LichessToken.query.filter_by(lichess_user_id=user_id).first()

    collection = Collection.query.filter_by(
        collection_id=collection_id,
        creator_name=token_record.lichess_username
    ).first_or_404()

    Position.query.filter_by(collection_id=collection_id).delete()
    db.session.delete(collection)
    db.session.commit()

    return redirect(url_for("main.my_collections"))