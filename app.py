from flask import Flask, jsonify, request

app = Flask(__name__)

items = {}
_next_id = 1


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


if __name__ == '__main__':
    # Add a deliberate code smell for SonarQube to catch (hardcoded secret)
    SECRET_API_KEY = "12345-Super-Secret-Key"
    app.run(host='0.0.0.0', port=5000)
