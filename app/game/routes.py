import requests
from flask import Blueprint, current_app, jsonify, redirect, render_template, session, url_for

from ..config import DEFAULT_AI_SETTINGS, FEN_PRESETS
from ..models import LichessToken

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

    return render_template(
        "fen_select.html",
        presets=FEN_PRESETS,
        username=token_record.lichess_username,
    )


@game_bp.route("/start/<preset_key>", methods=["POST"])
def start_game(preset_key):
    user_id = session.get("lichess_user_id")
    if not user_id:
        return jsonify({"error": "Nicht eingeloggt."}), 401

    token_record = LichessToken.query.filter_by(lichess_user_id=user_id).first()
    if token_record is None:
        return jsonify({"error": "Kein gespeichertes Token gefunden."}), 401

    preset = FEN_PRESETS.get(preset_key)
    if preset is None:
        return jsonify({"error": "Ungültiges Preset."}), 400

    payload = {
        "level": DEFAULT_AI_SETTINGS["level"],
        "clock.limit": DEFAULT_AI_SETTINGS["clock_limit"],
        "clock.increment": DEFAULT_AI_SETTINGS["clock_increment"],
        "color": DEFAULT_AI_SETTINGS["color"],
        "variant": DEFAULT_AI_SETTINGS["variant"],
        "fen": preset["fen"],
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
            "preset": preset_key,
        }
    )
