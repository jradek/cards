"""Command Line Interface (CLI) for cards project."""
import os
import pathlib
from contextlib import contextmanager
from typing import List

import cards
import typer
from cards import CardState
from tabulate import tabulate

DEFAULT_TABLEFORMAT = os.environ.get("CARDSTABLEFORMAT", "simple")

app = typer.Typer()


@app.command()
def version():
    """Return version of cards application"""
    print(cards.__version__)


@app.command()
def add(
    summary: List[str], owner: str = typer.Option(None, "-o", "--owner"),
):
    """Add a card to db."""
    summary = " ".join(summary) if summary else None
    with cards_db() as db:
        db.add_card(cards.Card(summary, owner))


@app.command()
def delete(card_id: int):
    """Remove card in db with given id."""
    with cards_db() as db:
        db.delete_card(card_id)


state_str = {
    CardState.TODO: "",
    CardState.IN_PROGRESS: "in prog",
    CardState.DONE: "done",
}


@app.command("list")
def list_cards(
    noowner: bool = typer.Option(None, "-n", "--noowner", "--no-owner"),
    owner: str = typer.Option(None, "-o", "--owner"),
    state: str = typer.Option(None, "-s", "--state"),
):
    """
    List cards in db.
    """
    filter = {"noowner": noowner, "owner": owner, "state": state}
    with cards_db() as db:
        the_cards = db.list_cards(filter=filter)

        items = []
        for t in the_cards:
            owner = "" if t.owner is None else t.owner
            items.append((t.id, t.state, owner, t.summary))

        print(
            tabulate(
                items, headers=("ID", "state", "owner", "summary"), tablefmt=format,
            ),
        )


@app.command()
def update(
    card_id: int,
    owner: str = typer.Option(None, "-o", "--owner"),
    summary: List[str] = typer.Option(None, "-s", "--summary"),
    state: str = typer.Option(None, "-s", "--state"),
):
    """Modify a card in db with given id with new info."""
    summary = " ".join(summary) if summary else None
    state = CardState(state) if state is not None else None
    with cards_db() as db:
        db.update_card(card_id, cards.Card(summary, owner, state))


@app.command()
def path():
    """List the path."""
    with cards_db() as db:
        print(db.path())


@app.command()
def count():
    """Return number of cards in db."""
    with cards_db() as db:
        print(db.count())


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Call list_cards of nothing else
    """
    if ctx.invoked_subcommand is None:
        list_cards(
            noowner=None, owner=None, state=None,
        )


def get_db_path():
    db_path = os.getenv("CARDS_DB_DIR", "")
    if db_path:
        return pathlib.Path(db_path)
    else:  # pragma: no cover
        return pathlib.Path().home()


@contextmanager
def cards_db():
    db_path = get_db_path() / ".cards_db.json"
    db = cards.CardsDB(db_path)
    yield db
    db.close()
