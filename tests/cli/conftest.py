import click.testing
import pytest
import pathlib
import cards.cli
import shlex


@pytest.fixture()
def runner():
    """Shortcut for click.testing.CliRunner()"""
    return click.testing.CliRunner()


@pytest.fixture()
def db_empty(tmpdir, monkeypatch):
    """Cards DB initialized, but with no items in it."""
    fake_home = pathlib.Path(str(tmpdir.mkdir('fake_home')))

    class FakePathLibPath():
        def home(self):
            return fake_home

    monkeypatch.setattr(cards.cli.pathlib, 'Path', FakePathLibPath)


@pytest.fixture()
def cards_cli():
    """Run command line through cards and return output."""
    runner = click.testing.CliRunner()

    def _invoke_cards(input_string):
        input_list = shlex.split(input_string)
        return runner.invoke(cards.cli.cards_cli, input_list).output.rstrip()

    return _invoke_cards


@pytest.fixture()
def db_non_empty(db_empty, cards_cli):
    """Cards DB with items 'first item', 'second item', 'third item'"""
    cards_cli('add "first item"')
    cards_cli('add "second item"')
    cards_cli('add "third item"')
