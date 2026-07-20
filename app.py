from flask import Flask, jsonify, request

app = Flask(__name__)

items = {}
_next_id = 1

@app.route('/')
def home():
    return b"Hello from Bajaj Capital Python Demo!"

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/calculate')
def calculate():
    op = request.args.get('op')
    a = request.args.get('a')
    b = request.args.get('b')

    if not op or a is None or b is None:
        return jsonify({"error": "missing parameters"}), 400

    try:
        a = float(a)
        b = float(b)
    except ValueError:
        return jsonify({"error": "non-numeric parameters"}), 400

    if op == 'add':
        result = a + b
    elif op == 'subtract':
        result = a - b
    elif op == 'multiply':
        result = a * b
    elif op == 'divide':
        if b == 0:
            return jsonify({"error": "division by zero"}), 400
        result = a / b
    else:
        return jsonify({"error": "invalid op"}), 400

    return jsonify({"result": result})

@app.route('/api/items', methods=['GET', 'POST'])
def manage_items():
    global _next_id
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        if 'name' not in data:
            return jsonify({"error": "missing name"}), 400
        
        item_id = _next_id
        _next_id += 1
        items[item_id] = {"id": item_id, "name": data['name']}
        return jsonify(items[item_id]), 201
    else:
        return jsonify({"items": list(items.values())})

@app.route('/api/items/<int:item_id>', methods=['GET', 'DELETE'])
def item_detail(item_id):
    if item_id not in items:
        return jsonify({"error": "not found"}), 404
    
    if request.method == 'GET':
        return jsonify(items[item_id])
    else:
        del items[item_id]
        return jsonify({"status": "deleted"})

@app.route('/api/echo', methods=['POST'])
def echo_payload():
    data = request.get_json(silent=True)
    if data is None or not data:
        return jsonify({"error": "Empty payload"}), 400
    
    return jsonify({"message": f"You sent: {data}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
