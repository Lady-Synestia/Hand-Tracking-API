from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def home():
    data = {
        "vector": {"x": 1.0, "y": 2.0, "z": 3.0},
        "integer": 42,
        "float": 3.14
    }
    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
