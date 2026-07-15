from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Bajaj Capital Python Demo!"

if __name__ == '__main__':
    # Add a deliberate code smell for SonarQube to catch (hardcoded secret)
    SECRET_API_KEY = "12345-Super-Secret-Key"
    app.run(host='0.0.0.0', port=5000)