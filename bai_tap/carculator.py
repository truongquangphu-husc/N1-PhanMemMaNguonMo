from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def calculator():

    values = {
        "a": "",
        "b": "",
        "op": "+"
    }

    errors = {}
    result = None

    if request.method == "POST":

        values["a"] = request.form.get("a", "").strip()
        values["b"] = request.form.get("b", "").strip()
        values["op"] = request.form.get("op", "+")

 
        try:
            a = float(values["a"].replace(",", "."))
        except ValueError:
            errors["a"] = "Số thứ nhất không hợp lệ."

  
        try:
            b = float(values["b"].replace(",", "."))
        except ValueError:
            errors["b"] = "Số thứ hai không hợp lệ."


        if values["op"] not in ["+", "-", "*", "/"]:
            errors["op"] = "Phép toán không hợp lệ."

        if not errors:

            op = values["op"]

            if op == "+":
                kq = a + b

            elif op == "-":
                kq = a - b

            elif op == "*":
                kq = a * b

            elif op == "/":
                if b == 0:
                    errors["b"] = "Không thể chia cho 0."
                else:
                    kq = a / b

            if not errors:
                result = f"{a:g} {op} {b:g} = {kq:g}"

    return render_template(
        "calculator.html",
        values=values,
        errors=errors,
        result=result
    )


if __name__ == "__main__":
    app.run(debug=True, port=9900)