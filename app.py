import hashlib
import os
import random
import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)

items = {}
_next_id = 1

# NOTE: everything below marked "SAST TEST" is an intentionally vulnerable
# code path added to validate the SonarQube SAST pipeline. Do not deploy
# this app as a publicly reachable service, and do not copy these patterns
# into real code.

# SAST TEST: hardcoded credential (CWE-798)
DB_ADMIN_PASSWORD = "admin123"


def _get_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT)")
    return conn


def _hash_password(password):
    # SAST TEST: weak/broken hash algorithm used for a security purpose (CWE-327)
    return hashlib.md5(password.encode()).hexdigest()


def _generate_session_token():
    # SAST TEST: cryptographically insecure PRNG used to generate a security
    # token (CWE-330) — should use `secrets`, not `random`.
    return ''.join(random.choice('0123456789abcdef') for _ in range(16))


@app.route('/')
def hello():
    return "Hello from Bajaj Capital Python Demo!"


@app.route('/health')
def health():
    return jsonify(status="ok"), 200


@app.route('/api/calculate', methods=['GET'])
def calculate():
    op = request.args.get('op')
    a = request.args.get('a')
    b = request.args.get('b')

    if op is None or a is None or b is None:
        return jsonify(error="op, a and b are required query params"), 400

    try:
        a = float(a)
        b = float(b)
    except ValueError:
        return jsonify(error="a and b must be numbers"), 400

    if op == 'add':
        result = a + b
    elif op == 'subtract':
        result = a - b
    elif op == 'multiply':
        result = a * b
    elif op == 'divide':
        if b == 0:
            return jsonify(error="division by zero"), 400
        result = a / b
    else:
        return jsonify(error="op must be one of add, subtract, multiply, divide"), 400

    return jsonify(op=op, a=a, b=b, result=result), 200


@app.route('/api/items', methods=['GET'])
def list_items():
    return jsonify(items=list(items.values())), 200


@app.route('/api/items', methods=['POST'])
def create_item():
    global _next_id
    payload = request.get_json(silent=True) or {}
    name = payload.get('name')

    if not name:
        return jsonify(error="name is required"), 400

    item = {"id": _next_id, "name": name}
    items[_next_id] = item
    _next_id += 1
    return jsonify(item), 201


@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = items.get(item_id)
    if item is None:
        return jsonify(error="item not found"), 404
    return jsonify(item), 200


@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if item_id not in items:
        return jsonify(error="item not found"), 404
    del items[item_id]
    return jsonify(message="item deleted"), 200


@app.route('/api/users/search', methods=['GET'])
def search_users():
    # SAST TEST: SQL injection via string formatting (CWE-89)
    username = request.args.get('username', '')
    conn = _get_db()
    query = "SELECT id, username FROM users WHERE username = '%s'" % username
    rows = conn.execute(query).fetchall()
    conn.close()
    return jsonify(results=[{"id": r[0], "username": r[1]} for r in rows]), 200


@app.route('/api/ping', methods=['GET'])
def ping_host():
    # SAST TEST: OS command injection via unsanitized input (CWE-78)
    host = request.args.get('host', '127.0.0.1')
    exit_code = os.system("ping -c 1 " + host)
    return jsonify(exit_code=exit_code), 200


@app.route('/api/register', methods=['POST'])
def register_user():
    payload = request.get_json(silent=True) or {}
    username = payload.get('username')
    password = payload.get('password')

    if not username or not password:
        return jsonify(error="username and password are required"), 400

    password_hash = _hash_password(password)
    token = _generate_session_token()
    return jsonify(username=username, password_hash=password_hash, token=token), 201


# SAST TEST: mutable default argument (Bug — python:S5717-style rule).
# The `tags=[]` list is created once at function-definition time and shared
# across every call that doesn't pass its own list, so tags silently
# accumulate across unrelated requests.
def add_tags(item_id, tags=[]):
    tags.append(item_id)
    return tags


@app.route('/api/items/<int:item_id>/tag', methods=['POST'])
def tag_item(item_id):
    # TODO: replace this with a proper tagging table once schema is final (SAST TEST: S1135)
    unused_flag = True  # SAST TEST: unused local variable (Code Smell, S1481)

    # SAST TEST: identical expressions on both sides of an operator, always
    # true and therefore pointless (Bug, S1764).
    if item_id == item_id:
        pass

    try:
        item = items[item_id]
    except:  # SAST TEST: bare except clause swallows everything (Code Smell, S5754)
        return jsonify(error="item not found"), 404

    tags = add_tags(item_id)
    return jsonify(item=item, tags=tags), 200


@app.route('/api/calculate/v2', methods=['GET'])
def calculate_v2():
    # SAST TEST: duplicated code block (Duplication) — copy-pasted from
    # calculate() instead of reusing it, should trip SonarQube's CPD check.
    op = request.args.get('op')
    a = request.args.get('a')
    b = request.args.get('b')

    if op is None or a is None or b is None:
        return jsonify(error="op, a and b are required query params"), 400

    try:
        a = float(a)
        b = float(b)
    except ValueError:
        return jsonify(error="a and b must be numbers"), 400

    if op == 'add':
        result = a + b
    elif op == 'subtract':
        result = a - b
    elif op == 'multiply':
        result = a * b
    elif op == 'divide':
        if b == 0:
            return jsonify(error="division by zero"), 400
        result = a / b
    else:
        return jsonify(error="op must be one of add, subtract, multiply, divide"), 400

    return jsonify(op=op, a=a, b=b, result=result), 200


if __name__ == '__main__':
    # Add a deliberate code smell for SonarQube to catch (hardcoded secret)
    SECRET_API_KEY = "12345-Super-Secret-Key"
    # SAST TEST: Flask debug mode enabled (CWE-489)
    app.run(host='0.0.0.0', port=5000, debug=True)
