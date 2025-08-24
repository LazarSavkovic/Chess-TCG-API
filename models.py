# models.py
from datetime import datetime
import enum
import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PileType(enum.Enum):
    MAIN = "MAIN"
    LAND = "LAND"
    SIDE = "SIDE"

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    clerk_user_id = db.Column(db.String(128), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Deck(db.Model):
    __tablename__ = "decks"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # ✅ make this a proper FK to users.id (int)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("decks", lazy="dynamic", cascade="all, delete"))

class DeckPile(db.Model):
    __tablename__ = "deck_piles"
    id = db.Column(db.Integer, primary_key=True)

    # ✅ match Deck.id type (String(36)), not PostgreSQL UUID
    deck_id = db.Column(
        db.String(36),
        db.ForeignKey("decks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    pile_type = db.Column(db.Enum(PileType), nullable=False)

    deck = db.relationship("Deck", backref=db.backref("piles", lazy="dynamic", cascade="all, delete"))

    __table_args__ = (
        db.UniqueConstraint("deck_id", "pile_type", name="uq_deck_pile_once_each"),
    )

class DeckCard(db.Model):
    __tablename__ = "deck_cards"
    id = db.Column(db.Integer, primary_key=True)
    pile_id = db.Column(db.Integer, db.ForeignKey("deck_piles.id", ondelete="CASCADE"), nullable=False, index=True)
    card_id = db.Column(db.String(128), nullable=False)  # e.g. 'bonecrawler'
    qty = db.Column(db.Integer, nullable=False, default=1)
    position = db.Column(db.Integer)  # optional explicit ordering

    pile = db.relationship("DeckPile", backref=db.backref("cards", lazy="dynamic", cascade="all, delete"))

    __table_args__ = (
        db.UniqueConstraint("pile_id", "card_id", name="uq_one_row_per_card_in_pile"),
    )
