from datetime import datetime, timezone

from .extensions import db


class LichessToken(db.Model):
    __tablename__ = "lichess_tokens"

    id = db.Column(db.Integer, primary_key=True)
    lichess_user_id = db.Column(db.String(120), unique=True, nullable=False)
    lichess_username = db.Column(db.String(120), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
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
