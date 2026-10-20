from flask import Flask, render_template, request

app = Flask(__name__)


def validate_score(value):
    value = value.strip()

    if value == "":
        return None, "Vui lòng nhập điểm."

    try:
        score = float(value.replace(",", "."))
    except ValueError:
        return None, "Vui lòng nhập một số."

    if score < 0 or score > 10:
        return None, "Điểm phải từ 0 đến 10."

    return score, None


@app.route("/", methods=["GET", "POST"])
def tinh_diem():

    values = {
        "cc": "",
        "gk": "",
        "ck": ""
    }

    errors = {}
    result = None

    if request.method == "POST":

        values["cc"] = request.form.get("cc", "")
        values["gk"] = request.form.get("gk", "")
        values["ck"] = request.form.get("ck", "")

        cc, error = validate_score(values["cc"])
        if error:
            errors["cc"] = error

        gk, error = validate_score(values["gk"])
        if error:
            errors["gk"] = error

        ck, error = validate_score(values["ck"])
        if error:
            errors["ck"] = error

        if not errors:

            diem_hp = cc * 0.1 + gk * 0.3 + ck * 0.6

            diem_hp = round(diem_hp, 1)

            if ck < 1:
                diem_chu = "F"
                ghi_chu = "Điểm liệt"

            elif diem_hp >= 8.5:
                diem_chu = "A"
                ghi_chu = ""

            elif diem_hp >= 7.0:
                diem_chu = "B"
                ghi_chu = ""

            elif diem_hp >= 5.5:
                diem_chu = "C"
                ghi_chu = ""

            elif diem_hp >= 4.0:
                diem_chu = "D"
                ghi_chu = ""

            else:
                diem_chu = "F"
                ghi_chu = ""

            result = {
                "diem": diem_hp,
                "chu": diem_chu,
                "ghi_chu": ghi_chu
            }

    return render_template(
        "tinhdiem.html",
        values=values,
        errors=errors,
        result=result
    )


if __name__ == "__main__":
    app.run(debug=True, port=9990)