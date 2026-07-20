from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
      <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h1>Welcome to Python App!</h1>
        <p>This is a fully functional Flask backend API ready for the demo.</p>
      </body>
    </html>
    '''

@app.route('/api/status')
def status():
    return jsonify({"status": "success", "message": "API is running flawlessly."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
