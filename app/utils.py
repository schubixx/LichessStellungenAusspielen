import base64
import hashlib
import os
import time
import random
import string

from flask import request, session

from .models import Position, LichessToken

def generate_code_verifier() -> str:
    return base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("=")

def is_admin():
    user_id = session.get("lichess_user_id")
    if not user_id:
        return False

    user = LichessToken.query.filter_by(lichess_user_id=user_id).first()
    return user and user.admin


def generate_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")

from typing import Optional

def generate_collection_id():
    timestamp = int(time.time() * 1000)
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"{timestamp}{random_part}"

def store_collection_from_request() -> Optional[str]:
    """Speichert den optionalen GET-Parameter COLLECTION in der Session.

    Wird bei jedem Request aufgerufen. Sobald ?COLLECTION=<wert> vorhanden ist,
    wird der Wert in der Session aktualisiert. Ohne Parameter bleibt der
    vorhandene Session-Wert unveraendert."""

    collection = request.args.get("COLLECTION", type=str)
    if collection:
        session["collection"] = collection.strip()
    return session.get("collection")


def get_current_collection() -> Optional[str]:
    """Liefert den aktuell in der Session gespeicherten COLLECTION-Wert."""
    return session.get("collection")

def get_positions_for_current_collection():
    collection = get_current_collection()
    if not collection:
        return []

    return (
        Position.query
        .filter_by(collection_id=collection)
        .order_by(Position.title.asc())
        .all()
    )