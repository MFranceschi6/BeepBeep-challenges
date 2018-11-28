from beepbeep.challenges.app import create_app
from beepbeep.challenges.database import db
import pytest
import os


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/beepbeep.challenges_test.db'

    yield app
    os.unlink('/tmp/beepbeep.challenges_test.db')


@pytest.fixture
def db_instance(app):
    db.init_app(app)
    db.create_all(app=app)

    with app.app_context():
        yield db


@pytest.fixture
def client(app):
    client = app.test_client()

    yield client
