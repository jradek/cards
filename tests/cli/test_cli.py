"""
Tests using cards CLI (command line interface).
"""
import shlex
from textwrap import dedent

import pytest
from cards import Card
from cards import CardState
from cards.cli import app
from typer.testing import CliRunner


@pytest.fixture()
def cards_cli(db_dir, monkeypatch):
    monkeypatch.setenv("CARDS_DB_DIR", str(db_dir))
    runner = CliRunner()

    def _invoke_cards(input_string):
        input_list = shlex.split(input_string)
        return runner.invoke(app, input_list).output.rstrip()

    return _invoke_cards


def test_equal_paths(db_dir, db_empty, cards_cli):
    fixture_path = str(db_dir)
    api_path = str(db_empty.path())
    cli_path = cards_cli("path")
    assert fixture_path == api_path == cli_path


def test_empty(db_empty, cards_cli):
    cards_db = db_empty
    all_cards = cards_db.list_cards()
    assert cards_db.count() == len(all_cards) == 0


def test_add(db_empty, cards_cli):
    cards_db = db_empty
    # GIVEN an empty database
    # WHEN a new card is added
    cards_cli("add something -o okken")

    # THEN The listing returns just the new card
    all_cards = cards_db.list_cards()
    the_card = all_cards[0]
    assert cards_db.count() == len(all_cards) == 1
    assert the_card.summary == "something"
    assert the_card.owner == "okken"


@pytest.fixture()
def mix_of_items(db_empty):
    cards_db = db_empty
    cards_db.add_card(Card(summary="one", owner="brian"))
    cards_db.add_card(Card(summary="two", owner="brian", state=CardState.DONE))
    cards_db.add_card(Card(summary="three", owner="okken", state=CardState.DONE))
    cards_db.add_card(Card(summary="four", owner=None, state=CardState.IN_PROGRESS))
    cards_db.add_card(Card(summary="five", owner="brian", state=CardState.IN_PROGRESS))
    return cards_db


expected_output_mix_of_items = """\
  ID  state    owner    summary
----  -------  -------  ---------
   1  todo     brian    one
   2  done     brian    two
   3  done     okken    three
   4  in prog           four
   5  in prog  brian    five"""


expected_output_no_owner = """\
  ID  state    owner    summary
----  -------  -------  ---------
   4  in prog           four"""

expected_output_owner_brian = """\
  ID  state    owner    summary
----  -------  -------  ---------
   1  todo     brian    one
   2  done     brian    two
   5  in prog  brian    five"""


expected_output_state_done = """\
  ID  state    owner    summary
----  -------  -------  ---------
   2  done     brian    two
   3  done     okken    three"""


expected_output_owner_okken_and_no_owner = """\
  ID  state    owner    summary
----  -------  -------  ---------
   3  done     okken    three
   4  in prog           four"""


def test_list(cards_cli, mix_of_items):
    """Check the format of list"""
    output = cards_cli("list")
    assert output == expected_output_mix_of_items


def test_list_if_no_subcommands(cards_cli, mix_of_items):
    """Check the format of list"""
    output = cards_cli("")
    assert output == expected_output_mix_of_items


@pytest.mark.parametrize("flags", ("-n", "--noowner", "--no-owner"))
def test_list_no_owner(cards_cli, mix_of_items, flags):
    """Check the format of list"""
    output = cards_cli(f"list {flags}")
    assert output == expected_output_no_owner


@pytest.mark.parametrize("flags", ("-o brian", "--owner brian"))
def test_list_owner_brian(cards_cli, mix_of_items, flags):
    """Check the format of list"""
    output = cards_cli(f"list {flags}")
    assert output == expected_output_owner_brian


@pytest.mark.parametrize("flags", ("-s done", "--state done"))
def test_list_state_done(cards_cli, mix_of_items, flags):
    """Check the format of list"""
    output = cards_cli(f"list {flags}")
    assert output == expected_output_state_done


def test_update(cards_cli, mix_of_items):
    expected_output = """\
      ID  state    owner    summary
    ----  -------  -------  ---------
       1  done     brian    one
       2  done     okken    two
       3  done     okken    three
       4  in prog           foo
       5  in prog  brian    five"""

    cards_cli("update 1 -s done")
    cards_cli("update 2 -o okken")
    cards_cli("update 4 --summary foo")
    output = cards_cli("list")
    assert output == dedent(expected_output)


def test_list_owner_okken_and_no_owner(cards_cli, mix_of_items):
    """Check the format of list"""
    output = cards_cli("list -o okken -n")
    assert output == expected_output_owner_okken_and_no_owner


def test_count(cards_cli, mix_of_items):
    assert cards_cli("count") == "5"


@pytest.fixture()
def a_card(mix_of_items):
    cards_db = mix_of_items
    an_id = 3
    _card = cards_db.get_card(an_id)
    all_cards = cards_db.list_cards()
    assert cards_db.count() == 5
    assert _card in all_cards
    return _card


def test_delete(cards_cli, a_card, mix_of_items):
    cards_db = mix_of_items

    # GIVEN a db with 5 items
    # WHEN we delete one item
    an_id = a_card.id

    cards_cli(f"delete {an_id}")

    # THEN the other cards remain
    all_cards = cards_db.list_cards()
    assert cards_db.count() == 4

    # AND the deleted card is missing
    assert a_card not in all_cards
    # AND retrieving it again returns None
    assert cards_db.get_card(an_id) is None


def test_version(cards_cli):
    """
    Should return 3 digits separated by a dot
    """
    version = cards_cli("version").split(".")
    assert len(version) == 3
    assert all([d.isdigit() for d in version])
