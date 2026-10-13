import pytest

from src.auth import AuthStore


@pytest.fixture
def store(tmp_path):
    s = AuthStore(tmp_path / "fresh.sqlite3")
    yield s
    s.close()


def test_fresh_database_initialises_and_seeds_demo_accounts(store):
    # Regression: on a fresh database this used to fail with
    # "no such table: student_knowledge_graph".
    assert store.get_user_by_username("aarav")["role"] == "student"


def test_register_authenticate_and_session_round_trip(store):
    user = store.register_user("meera_k", "meera@example.com", "s3cret-pass", "Meera K", "student")
    assert store.authenticate_user("meera_k", "s3cret-pass")["id"] == user["id"]
    assert store.authenticate_user("meera_k", "wrong-pass") is None
    token = store.create_session(user["id"])
    assert store.get_user_by_token(token)["username"] == "meera_k"
    assert store.invalidate_session(token)
    assert store.get_user_by_token(token) is None


@pytest.mark.parametrize("username,email,password", [
    ("ab", "a@example.com", "s3cret-pass"),        # username too short
    ("valid_user", "not-an-email", "s3cret-pass"),  # bad email
    ("valid_user", "v@example.com", "123"),         # password too short
])
def test_register_rejects_invalid_input(store, username, email, password):
    with pytest.raises(ValueError):
        store.register_user(username, email, password, "Name", "student")


def test_passwords_are_not_stored_in_plain_text(store):
    store.register_user("ravi_s", "ravi@example.com", "plain-text-pw", "Ravi", "student")
    rows = store.conn.execute("SELECT * FROM users WHERE username='ravi_s'").fetchone()
    assert "plain-text-pw" not in [str(v) for v in tuple(rows)]
