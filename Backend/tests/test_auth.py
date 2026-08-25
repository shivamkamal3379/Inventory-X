def test_register_and_login(client):
    r = client.post("/auth/register", json={"username": "alice", "password": "supersecret1"})
    assert r.status_code == 201
    assert r.json()["username"] == "alice"
    assert "hashed_password" not in r.json()

    r = client.post("/auth/login", data={"username": "alice", "password": "supersecret1"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
    assert r.json()["access_token"]


def test_duplicate_username_is_409(client):
    client.post("/auth/register", json={"username": "bob", "password": "supersecret1"})
    r = client.post("/auth/register", json={"username": "bob", "password": "supersecret1"})
    assert r.status_code == 409


def test_short_password_rejected(client):
    r = client.post("/auth/register", json={"username": "carol", "password": "short"})
    assert r.status_code == 422


def test_wrong_password_rejected(client):
    client.post("/auth/register", json={"username": "dave", "password": "supersecret1"})
    r = client.post("/auth/login", data={"username": "dave", "password": "wrongpassword"})
    assert r.status_code == 401


def test_unknown_user_and_wrong_password_are_indistinguishable(client):
    """The two failures must return the same status and body, or the endpoint
    becomes a username-enumeration oracle."""
    client.post("/auth/register", json={"username": "erin", "password": "supersecret1"})
    wrong_pw = client.post("/auth/login", data={"username": "erin", "password": "nope12345"})
    no_user = client.post("/auth/login", data={"username": "ghost", "password": "nope12345"})
    assert wrong_pw.status_code == no_user.status_code == 401
    assert wrong_pw.json()["detail"] == no_user.json()["detail"]


def test_me_returns_current_user(client, auth_headers):
    r = client.get("/auth/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["username"] == "tester"


def test_change_password(client, auth_headers):
    r = client.post(
        "/auth/change-password",
        json={"current_password": "testpassword123", "new_password": "brandnewpass99"},
        headers=auth_headers,
    )
    assert r.status_code == 204
    assert (
        client.post(
            "/auth/login", data={"username": "tester", "password": "brandnewpass99"}
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/auth/login", data={"username": "tester", "password": "testpassword123"}
        ).status_code
        == 401
    )
