import pytest
from cards import Card
from cards import CardState


def test_add_card(db_empty):
    cards_db = db_empty
    c = Card(summary="something", owner="okken")
    id = cards_db.add_card(c)
    assert id is not None
    assert cards_db.count() == 1


@pytest.fixture()
def db_non_empty(db_empty):
    cards_db = db_empty
    some_cards = (
        Card(summary="first item"),
        Card(summary="second item"),
        Card(summary="third item"),
    )
    for c in some_cards:
        cards_db.add_card(c)
    return cards_db


def test_get_card(db_empty):
    cards_db = db_empty
    c = Card(summary="something", owner="okken")
    id = cards_db.add_card(c)

    retrieved_card = cards_db.get_card(id)

    assert retrieved_card == c
    assert retrieved_card.id == id


def test_list(db_empty):
    cards_db = db_empty
    some_cards = [Card(summary="one"), Card(summary="two")]
    for c in some_cards:
        cards_db.add_card(c)

    all_cards = cards_db.list_cards()
    assert all_cards == some_cards


def test_count(db_empty):
    cards_db = db_empty
    some_cards = [Card(summary="one"), Card(summary="two")]
    for c in some_cards:
        cards_db.add_card(c)

    assert cards_db.count() == 2


def test_update(db_non_empty):
    cards_db = db_non_empty
    # GIVEN a card known to be in the db
    all_cards = cards_db.list_cards()
    a_card = all_cards[0]

    # WHEN we update() the card with new info
    cards_db.update_card(a_card.id, Card(owner="okken", state=CardState.DONE))

    # THEN we can retrieve the card with get() and
    # and it has all of our changes
    updated_card = cards_db.get_card(a_card.id)
    expected = Card(summary=a_card.summary, owner="okken", state=CardState.DONE)
    assert updated_card == expected


def test_delete(db_non_empty):
    cards_db = db_non_empty
    # GIVEN a non empty db
    a_card = cards_db.list_cards()[0]
    id = a_card.id
    count_before = cards_db.count()

    # WHEN we delete one item
    cards_db.delete_card(id)
    count_after = cards_db.count()

    # THEN the card is no longer in the db
    all_cards = cards_db.list_cards()
    assert a_card not in all_cards
    assert count_after == count_before - 1


def test_delete_all(db_non_empty):
    cards_db = db_non_empty
    # GIVEN a non empty db

    # WHEN we delete_all()
    cards_db.delete_all()

    # THEN the count is 0
    count = cards_db.count()
    assert count == 0
