import base64
import hashlib
import os
import time
import random
import string
from datetime import datetime, timezone
import random
import base64

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
    # timestamp = int(time.time() * 1000)
    # random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    # return f"{timestamp}{random_part}"
    return snowflake44()

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

def _ticks(dt: datetime) -> int:
    dt = dt.astimezone(timezone.utc)
    YEAR1 = datetime(1, 1, 1, tzinfo=timezone.utc)
    delta = dt - YEAR1
    return delta.days * 864_000_000_000 + delta.seconds * 10_000_000 + delta.microseconds * 10


def to_44bit_salted(dt: datetime) -> int:
    global _previous_time_frame

    _randoms_of_previous_time_frame = set()
    _random_generator = random.Random()
    CENTURY_BEGIN = datetime(1900, 1, 1, tzinfo=timezone.utc)
    dt_ticks = _ticks(dt)

    elapsed_milliseconds = dt_ticks // 10_000 - _ticks(CENTURY_BEGIN) // 10_000

    elapsed_milliseconds <<= 19

    while True:
        rv = _random_generator.randrange(524_287)
        if rv not in _randoms_of_previous_time_frame:
            _randoms_of_previous_time_frame.add(rv)
            break

    _previous_time_frame = dt_ticks
    return elapsed_milliseconds | rv

def uid_to_base64_urlsafe(uid: int) -> str:
    b = uid.to_bytes(8, byteorder="big", signed=False)
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")


def base64_urlsafe_to_uid(b64: str) -> int:
    padding = "=" * (-len(b64) % 4)
    b = base64.urlsafe_b64decode(b64 + padding)
    return int.from_bytes(b, byteorder="big", signed=False)


def snowflake44() -> str:
    return uid_to_base64_urlsafe(to_44bit_salted(datetime.now(timezone.utc)))
