import cards
import pytest


@pytest.fixture(scope="module")
def db_dir(tmp_path_factory):
    """A temp dir for the db"""
    return tmp_path_factory.mktemp("tmp_db_dir")


@pytest.fixture(scope="module")
def db_module(db_dir):
    """A db that can be used for all tests"""
    return cards.CardsDB(db_dir / ".cards_db.json")


@pytest.fixture()
def db_empty(db_module):
    db_module.delete_all()
    return db_module
