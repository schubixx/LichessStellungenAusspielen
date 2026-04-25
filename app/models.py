from datetime import datetime, timezone

from .extensions import db


class LichessToken(db.Model):
    __tablename__ = "lichess_tokens"

    id = db.Column(db.Integer, primary_key=True)
    lichess_user_id = db.Column(db.String(120), unique=True, nullable=False)
    lichess_username = db.Column(db.String(120), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    admin =db.Column(db.Boolean, default=False)
    scope = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<LichessToken {self.lichess_username}>"

class Collection(db.Model):
    __tablename__ = "collections"

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.String(120), unique=True, nullable=False, index=True)
    creator_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)

class Position(db.Model):
    __tablename__ = "positions"

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.String(120), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    fen = db.Column(db.Text, nullable=False)
    ai_level = db.Column(db.Integer, nullable=True)
    color = db.Column(db.String(20), nullable=True)
    clock_limit = db.Column(db.Integer, nullable=True)
    clock_increment = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Position {self.collection_id}: {self.title}>"