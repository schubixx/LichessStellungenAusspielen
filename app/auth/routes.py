import secrets
from urllib.parse import urlencode

import requests
from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from ..extensions import db
from ..models import LichessToken
from ..utils import generate_code_challenge, generate_code_verifier

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    client_id = current_app.config["LICHESS_CLIENT_ID"]
    if not client_id:
        return render_template(
            "error.html",
            title="Fehlende Konfiguration",
            message="LICHESS_CLIENT_ID ist nicht gesetzt.",
        ), 500

    state = secrets.token_urlsafe(16)
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    session["oauth_state"] = state
    session["code_verifier"] = code_verifier

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": current_app.config["LICHESS_REDIRECT_URI"],
        "scope": "challenge:write",
        "state": state,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
    }

    authorize_url = (
        f"{current_app.config['LICHESS_OAUTH_AUTHORIZE_URL']}?{urlencode(params)}"
    )
    return redirect(authorize_url)


@auth_bp.route("/callback")
def callback():
    if "error" in request.args:
        return render_template(
            "error.html",
            title="OAuth-Fehler",
            message=request.args.get("error", "Unbekannter OAuth-Fehler"),
        ), 400

    code = request.args.get("code")
    returned_state = request.args.get("state")

    if not code:
        return render_template(
            "error.html", title="OAuth-Fehler", message="Kein Code empfangen."
        ), 400

    if returned_state != session.get("oauth_state"):
        return render_template(
            "error.html", title="OAuth-Fehler", message="Ungültiger state-Wert."
        ), 400

    code_verifier = session.get("code_verifier")
    if not code_verifier:
        return render_template(
            "error.html",
            title="OAuth-Fehler",
            message="PKCE code_verifier fehlt in der Session.",
        ), 400

    token_response = requests.post(
        current_app.config["LICHESS_OAUTH_TOKEN_URL"],
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": current_app.config["LICHESS_REDIRECT_URI"],
            "client_id": current_app.config["LICHESS_CLIENT_ID"],
            "code_verifier": code_verifier,
        },
        timeout=20,
    )

    if not token_response.ok:
        return render_template(
            "error.html",
            title="Token-Austausch fehlgeschlagen",
            message=f"{token_response.status_code}: {token_response.text}",
        ), 400

    token_data = token_response.json()
    access_token = token_data["access_token"]
    scope = token_data.get("scope", "")

    account_response = requests.get(
        current_app.config["LICHESS_ACCOUNT_URL"],
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20,
    )

    if not account_response.ok:
        return render_template(
            "error.html",
            title="Lichess-Konto konnte nicht geladen werden",
            message=f"{account_response.status_code}: {account_response.text}",
        ), 400

    account_data = account_response.json()
    lichess_user_id = account_data["id"]
    lichess_username = account_data["username"]

    token_record = LichessToken.query.filter_by(lichess_user_id=lichess_user_id).first()
    if token_record is None:
        token_record = LichessToken(
            lichess_user_id=lichess_user_id,
            lichess_username=lichess_username,
            access_token=access_token,
            scope=scope,
        )
        db.session.add(token_record)
    else:
        token_record.lichess_username = lichess_username
        token_record.access_token = access_token
        token_record.scope = scope

    db.session.commit()

    session["lichess_user_id"] = lichess_user_id
    session["lichess_username"] = lichess_username
    session.pop("oauth_state", None)
    session.pop("code_verifier", None)

    return redirect(url_for("game.select_fen"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))
