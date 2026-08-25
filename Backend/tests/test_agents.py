def test_agent_crud(client, auth_headers):
    r = client.post(
        "/agents/", json={"AgentName": "Ann", "mobile": "9000000001"}, headers=auth_headers
    )
    assert r.status_code == 201
    agent_id = r.json()["agentId"]

    assert client.get(f"/agents/{agent_id}", headers=auth_headers).json()["AgentName"] == "Ann"

    r = client.put(f"/agents/{agent_id}", json={"AgentName": "Anne"}, headers=auth_headers)
    assert r.status_code == 200 and r.json()["AgentName"] == "Anne"
    # Untouched field survives the partial update.
    assert r.json()["mobile"] == "9000000001"

    assert client.delete(f"/agents/{agent_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/agents/{agent_id}", headers=auth_headers).status_code == 404


def test_agent_search(client, auth_headers, agent):
    assert len(client.get("/agents/?q=john", headers=auth_headers).json()) == 1
    assert len(client.get("/agents/?q=nobody", headers=auth_headers).json()) == 0


def test_invalid_mobile_rejected(client, auth_headers):
    r = client.post("/agents/", json={"AgentName": "X", "mobile": "abc"}, headers=auth_headers)
    assert r.status_code == 422


def test_deleting_agent_nulls_party_link_not_the_party(client, auth_headers, agent):
    """ondelete=SET NULL: losing an agent must not cascade away their customers."""
    client.post(
        "/parties/",
        json={"id": "CUST500", "name": "Linked", "mobile": "1234567", "agentId": agent["agentId"]},
        headers=auth_headers,
    )
    client.delete(f"/agents/{agent['agentId']}", headers=auth_headers)
    r = client.get("/parties/CUST500", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["agentId"] is None
