from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json(force=True, silent=True) or {}
    return jsonify({"you_sent": data}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
