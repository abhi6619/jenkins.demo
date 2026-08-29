from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple Calculator</title>
    <style>
        body {
            font-family: Arial;
            text-align: center;
            margin-top: 80px;
        }

        .calculator {
            width: 300px;
            margin: auto;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 10px;
        }

        input {
            width: 90%;
            padding: 10px;
            margin: 10px;
        }

        button {
            width: 60px;
            padding: 10px;
            margin: 5px;
            font-size: 18px;
        }

        h2 {
            color: #333;
        }

        #result {
            margin-top: 20px;
            font-size: 22px;
            font-weight: bold;
        }
    </style>
</head>

<body>

<div class="calculator">
    <h2>Simple Calculator</h2>

    <input type="number" id="num1" placeholder="Enter first number">
    <input type="number" id="num2" placeholder="Enter second number">

    <br>

    <button onclick="calculate('+')">+</button>
    <button onclick="calculate('-')">-</button>
    <button onclick="calculate('*')">*</button>
    <button onclick="calculate('/')">/</button>

    <div id="result">Result: </div>
</div>

<script>
function calculate(operator) {

    let a = document.getElementById("num1").value;
    let b = document.getElementById("num2").value;

    if (a === "" || b === "") {
        document.getElementById("result").innerHTML =
            "Please enter both numbers";
        return;
    }

    let operation;

    if (operator === "+") {
        operation = "add";
    } else if (operator === "-") {
        operation = "subtract";
    } else if (operator === "*") {
        operation = "multiply";
    } else if (operator === "/") {
        operation = "divide";
    }

    fetch(`/${operation}?a=${a}&b=${b}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("result").innerHTML =
                "Result: " + data.result;
        });
}
</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/add")
def add():
    a = float(request.args.get("a"))
    b = float(request.args.get("b"))

    return {"result": a + b}


@app.route("/subtract")
def subtract():
    a = float(request.args.get("a"))
    b = float(request.args.get("b"))

    return {"result": a - b}


@app.route("/multiply")
def multiply():
    a = float(request.args.get("a"))
    b = float(request.args.get("b"))

    return {"result": a * b}


@app.route("/divide")
def divide():
    a = float(request.args.get("a"))
    b = float(request.args.get("b"))

    if b == 0:
        return {"result": "Cannot divide by zero"}

    return {"result": a / b}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8084)
