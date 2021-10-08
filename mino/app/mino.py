from flask import Flask, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

@app.route('/minos')
def minos():
    with open('minos.json') as f:
        jsn = json.load(f)

    return jsonify(jsn)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
