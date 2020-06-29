"""
API for the cards project
"""
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import List

import tinydb

__all__ = [
    "CardState",
    "Card",
    "CardsDB",
]


class CardState(str, Enum):
    TODO: str = "todo"
    IN_PROGRESS: str = "in prog"
    WAITING: str = "waiting"
    DONE: str = "done"


@dataclass
class Card:
    summary: str = None
    owner: str = None
    state: CardState = CardState.TODO
    id: int = field(default=None, compare=False)

    @classmethod
    def from_dict(cls, d):
        return Card(**d)

    def to_dict(self):
        return asdict(self)


class CardsDB:
    def __init__(self, db_path):
        self._db_path = db_path
        self._db = tinydb.TinyDB(db_path)

    def add_card(self, card: Card) -> int:
        """Add a card, return the id of card."""
        card.id = self._db.insert(card.to_dict())
        self._db.update(card.to_dict(), doc_ids=[card.id])
        return card.id

    def get_card(self, card_id: int) -> Card:
        """Return a card with a matching id."""
        db_item = self._db.get(doc_id=card_id)
        if db_item is not None:
            return Card.from_dict(db_item)
        else:
            return None

    def list_cards(self, filter=None) -> List[Card]:
        """Return a list of all cards."""
        q = tinydb.Query()
        if filter:
            noowner = filter.get("noowner", None)
            owner = filter.get("owner", None)
            state = filter.get("state", None)
        else:
            noowner = None
            owner = None
            state = None
        if noowner and owner:
            # #E711 comparison to None should be 'if cond is None:'
            # However, that doesn't work for tinydb
            results = self._db.search(
                (q.owner == owner) | (q.owner == None) | (q.owner == ""),  # noqa: E711
            )
        elif noowner or owner == "":
            results = self._db.search((q.owner == None) | (q.owner == ""))  # noqa: E711
        elif owner:
            results = self._db.search(q.owner == owner)
        else:
            results = self._db

        if state is None:
            return [Card.from_dict(t) for t in results]
        else:
            return [Card.from_dict(t) for t in results if t["state"] == state]

    def count(self) -> int:
        """Return the number of cards in db."""
        return len(self.list_cards())

    def update_card(self, card_id: int, card_mods: Card) -> None:
        """Update a card with modifications."""
        d = card_mods.to_dict()
        changes = {k: v for k, v in d.items() if v is not None}
        self._db.update(changes, doc_ids=[card_id])

    def delete_card(self, card_id: int) -> None:
        """Remove a card from db with given card_id."""
        self._db.remove(doc_ids=[card_id])

    def delete_all(self) -> None:
        """Remove all tasks from db."""
        self._db.purge()

    def close(self):
        self._db.close()

    def path(self):
        return self._db_path.parent
