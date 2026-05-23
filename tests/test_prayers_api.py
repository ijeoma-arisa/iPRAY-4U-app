import json
import pytest

from app import app
from helpers import get_auth_headers, make_prayer_payload

# Constants
ENDPOINT = '/prayers'

# Sample data
SAMPLE_PRAYER = make_prayer_payload(title='Healing', description='Pray for healing', urgent=False)
UPDATED_PRAYER = make_prayer_payload(title='Healing Updated', description='Updated description', urgent=True)


# GET /prayers - when empty list
def test_get_prayers_empty(client):
    resp = client.get(ENDPOINT)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


# POST /prayers - happy path
def test_post_prayer_success(client):
    headers = get_auth_headers()
    resp = client.post(ENDPOINT, json=SAMPLE_PRAYER, headers=headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'id' in data
    assert data['title'] == SAMPLE_PRAYER['title']


# POST /prayers - missing required fields (unhappy path)
def test_post_prayer_missing_fields(client):
    headers = get_auth_headers()
    bad = { 'description': 'no title provided' }
    resp = client.post(ENDPOINT, json=bad, headers=headers)
    assert resp.status_code in (400, 422)


# POST /prayers - invalid JSON (edge case)
def test_post_prayer_invalid_json(client):
    headers = get_auth_headers()
    resp = client.post(ENDPOINT, data='not-a-json', headers={**headers, 'Content-Type': 'application/json'})
    assert resp.status_code in (400, 415)


# GET /prayers/<id> - happy path
def test_get_prayer_by_id(client):
    headers = get_auth_headers()
    post = client.post(ENDPOINT, json=SAMPLE_PRAYER, headers=headers)
    pid = post.get_json()['id']
    resp = client.get(f"{ENDPOINT}/{pid}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['id'] == pid


# GET /prayers/<id> - not found
def test_get_prayer_not_found(client):
    resp = client.get(f"{ENDPOINT}/999999")
    assert resp.status_code == 404


# PUT /prayers/<id> - happy path
def test_put_prayer_success(client):
    headers = get_auth_headers()
    post = client.post(ENDPOINT, json=SAMPLE_PRAYER, headers=headers)
    pid = post.get_json()['id']
    resp = client.put(f"{ENDPOINT}/{pid}", json=UPDATED_PRAYER, headers=headers)
    assert resp.status_code in (200, 204)
    # verify update via GET
    get = client.get(f"{ENDPOINT}/{pid}")
    assert get.get_json()['title'] == UPDATED_PRAYER['title']


# PUT /prayers/<id> - not found
def test_put_prayer_not_found(client):
    headers = get_auth_headers()
    resp = client.put(f"{ENDPOINT}/999999", json=UPDATED_PRAYER, headers=headers)
    assert resp.status_code == 404


# DELETE /prayers/<id> - happy path
def test_delete_prayer_success(client):
    headers = get_auth_headers()
    post = client.post(ENDPOINT, json=SAMPLE_PRAYER, headers=headers)
    pid = post.get_json()['id']
    resp = client.delete(f"{ENDPOINT}/{pid}", headers=headers)
    assert resp.status_code in (200, 204)
    # subsequent GET should be 404
    assert client.get(f"{ENDPOINT}/{pid}").status_code == 404


# DELETE /prayers/<id> - not found
def test_delete_prayer_not_found(client):
    headers = get_auth_headers()
    resp = client.delete(f"{ENDPOINT}/999999", headers=headers)
    assert resp.status_code == 404


# GET /prayers - pagination/edge case (large offset)
def test_get_prayers_pagination_edge(client):
    # request a very large page offset/size to ensure service handles gracefully
    resp = client.get(ENDPOINT + '?page=9999&per_page=1000')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
