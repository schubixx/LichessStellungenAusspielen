import requests
from flask import Blueprint, current_app, jsonify, redirect, render_template, session, url_for

from ..config import DEFAULT_AI_SETTINGS
from ..models import LichessToken, Position, Collection
from ..utils import get_current_collection, get_positions_for_current_collection, fen_to_board

game_bp = Blueprint("game", __name__)


@game_bp.route("/fen-select")
def select_fen():
    user_id = session.get("lichess_user_id")
    if not user_id:
        return redirect(url_for("main.index"))

    token_record = LichessToken.query.filter_by(lichess_user_id=user_id).first()
    if token_record is None:
        session.clear()
        return redirect(url_for("main.index"))

    collection_id = get_current_collection()
    positions = get_positions_for_current_collection()

    collection_record = None
    if collection_id:
        collection_record = Collection.query.filter_by(collection_id=collection_id).first()

    for position in positions:
        position.board = fen_to_board(position.fen)

    return render_template(
        "fen_select.html",
        positions=positions,
        username=token_record.lichess_username,
        collection=collection_id,
        collection_record=collection_record,
    )

@game_bp.route("/start/<int:position_id>", methods=["POST"])
def start_game(position_id):
    user_id = session.get("lichess_user_id")
    if not user_id:
        return jsonify({"error": "Nicht eingeloggt."}), 401

    token_record = LichessToken.query.filter_by(lichess_user_id=user_id).first()
    if token_record is None:
        return jsonify({"error": "Kein gespeichertes Token gefunden."}), 401

    collection = get_current_collection()
    if not collection:
        return jsonify({"error": "Keine COLLECTION gesetzt."}), 400

    position = Position.query.filter_by(
        id=position_id,
        collection_id=collection
    ).first()

    if position is None:
        return jsonify({"error": "Stellung nicht gefunden."}), 404

    payload = {
        "level": position.ai_level if position.ai_level is not None else DEFAULT_AI_SETTINGS["level"],
        "clock.limit": position.clock_limit if position.clock_limit is not None else DEFAULT_AI_SETTINGS["clock_limit"],
        "clock.increment": position.clock_increment if position.clock_increment is not None else DEFAULT_AI_SETTINGS["clock_increment"],
        "color": position.color if position.color else DEFAULT_AI_SETTINGS["color"],
        "variant": DEFAULT_AI_SETTINGS["variant"],
        "fen": position.fen,
    }

    response = requests.post(
        current_app.config["LICHESS_CHALLENGE_AI_URL"],
        headers={"Authorization": f"Bearer {token_record.access_token}"},
        data=payload,
        timeout=20,
    )

    if not response.ok:
        return jsonify(
            {
                "error": "Lichess konnte die Partie nicht erstellen.",
                "details": f"{response.status_code}: {response.text}",
            }
        ), 400

    game_data = response.json()
    game_id = game_data.get("id")

    if not game_id:
        return jsonify({"error": "Keine Spiel-ID in der Lichess-Antwort gefunden."}), 500

    return jsonify(
        {
            "game_id": game_id,
            "game_url": f"https://lichess.org/{game_id}",
            "position_id": position.id,
            "title": position.title,
            "collection": collection,
        }
    )
