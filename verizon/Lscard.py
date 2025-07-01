from app import app, db
from app import Card, User  # Import your models

with app.app_context():
    cards = Card.query.all()
    for card in cards:
        print(card.card_number, card.user.firstname if card.user else "no user")

