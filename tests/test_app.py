import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config['TESTING'] = True
    app_module.items.clear()
    app_module._next_id = 1
    with app_module.app.test_client() as client:
        yield client


def test_hello(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b"Hello from Bajaj Capital Python Demo!" in resp.data


def test_health(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


@pytest.mark.parametrize(
    "op,a,b,expected",
    [
        ("add", 2, 3, 5),
        ("subtract", 5, 3, 2),
        ("multiply", 4, 3, 12),
        ("divide", 10, 2, 5),
    ],
)
def test_calculate_ops(client, op, a, b, expected):
    resp = client.get(f'/api/calculate?op={op}&a={a}&b={b}')
    assert resp.status_code == 200
    assert resp.get_json()['result'] == expected


def test_calculate_divide_by_zero(client):
    resp = client.get('/api/calculate?op=divide&a=1&b=0')
    assert resp.status_code == 400
    assert "division by zero" in resp.get_json()['error']


def test_calculate_invalid_op(client):
    resp = client.get('/api/calculate?op=modulo&a=1&b=2')
    assert resp.status_code == 400


def test_calculate_non_numeric(client):
    resp = client.get('/api/calculate?op=add&a=foo&b=2')
    assert resp.status_code == 400


def test_calculate_missing_params(client):
    resp = client.get('/api/calculate?op=add&a=1')
    assert resp.status_code == 400


def test_create_and_get_item(client):
    resp = client.post('/api/items', json={"name": "widget"})
    assert resp.status_code == 201
    created = resp.get_json()
    assert created['name'] == 'widget'
    item_id = created['id']

    resp = client.get(f'/api/items/{item_id}')
    assert resp.status_code == 200
    assert resp.get_json()['name'] == 'widget'


def test_create_item_missing_name(client):
    resp = client.post('/api/items', json={})
    assert resp.status_code == 400


def test_list_items(client):
    client.post('/api/items', json={"name": "a"})
    client.post('/api/items', json={"name": "b"})
    resp = client.get('/api/items')
    assert resp.status_code == 200
    assert len(resp.get_json()['items']) == 2


def test_get_item_not_found(client):
    resp = client.get('/api/items/999')
    assert resp.status_code == 404


def test_delete_item(client):
    created = client.post('/api/items', json={"name": "temp"}).get_json()
    resp = client.delete(f"/api/items/{created['id']}")
    assert resp.status_code == 200

    resp = client.get(f"/api/items/{created['id']}")
    assert resp.status_code == 404


def test_delete_item_not_found(client):
    resp = client.delete('/api/items/999')
    assert resp.status_code == 404
