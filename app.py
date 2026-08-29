from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>Simple Calculator</h1>

    <p>Use the API like this:</p>

    <ul>
        <li>/add?a=10&b=5</li>
        <li>/subtract?a=10&b=5</li>
        <li>/multiply?a=10&b=5</li>
        <li>/divide?a=10&b=5</li>
    </ul>
    """


@app.route("/add")
def add():
    a = float(request.args.get("a", 0))
    b = float(request.args.get("b", 0))

    return jsonify({
        "operation": "addition",
        "result": a + b
    })


@app.route("/subtract")
def subtract():
    a = float(request.args.get("a", 0))
    b = float(request.args.get("b", 0))

    return jsonify({
        "operation": "subtraction",
        "result": a - b
    })


@app.route("/multiply")
def multiply():
    a = float(request.args.get("a", 0))
    b = float(request.args.get("b", 0))

    return jsonify({
        "operation": "multiplication",
        "result": a * b
    })


@app.route("/divide")
def divide():
    a = float(request.args.get("a", 0))
    b = float(request.args.get("b", 0))

    if b == 0:
        return jsonify({
            "error": "Cannot divide by zero"
        }), 400

    return jsonify({
        "operation": "division",
        "result": a / b
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8084
    )
