import base64
import hashlib
import os

from flask import request, session

from .models import Position

def generate_code_verifier() -> str:
    return base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("=")


def generate_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")

from typing import Optional

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