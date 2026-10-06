from flask import (
    Flask,
    request,
    jsonify,
    url_for,
    render_template_string,
    abort,
    redirect,
    make_response
)

import csv
import io

app = Flask(__name__)
app.json.ensure_ascii = False


# ==========================================================
# DỮ LIỆU MẪU
# ==========================================================
STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "lop": "K47A",
        "scores": {
            "PMMNM": 8.5,
            "CSDL": 7.0,
            "MMT": 9.0
        }
    },
    "23T1020002": {
        "name": "Trần Thị Bình",
        "lop": "K47A",
        "scores": {
            "PMMNM": 6.0,
            "CSDL": 5.5,
            "MMT": 7.0
        }
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "lop": "K47B",
        "scores": {
            "PMMNM": 9.5,
            "CSDL": 9.0
        }
    },
    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "lop": "K47B",
        "scores": {
            "PMMNM": 4.0,
            "CSDL": 3.5,
            "MMT": 5.0
        }
    },
    "23T1020005": {
        "name": "Hoàng Thu Hà",
        "lop": "K47A",
        "scores": {}
    },
    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "lop": "K47C",
        "scores": {
            "PMMNM": 7.5,
            "MMT": 8.0
        }
    }
}


# ==========================================================
# HTML TRANG CHỦ
# ==========================================================
INDEX_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Trang chủ</title>
</head>
<body>
    <h1>Thống kê tổng quan</h1>

    <p>
        Tổng số sinh viên:
        <strong>{{ total_students }}</strong>
    </p>

    <p>
        Số lớp (không trùng):
        <strong>{{ total_classes }}</strong>
    </p>

    <p>
        <a href="{{ url_for('student_list') }}">
            Xem danh sách sinh viên (/students)
        </a>
        |
        <a href="{{ url_for('search_student') }}">
            Tìm kiếm sinh viên
        </a>
        |
        <a href="{{ url_for('api_students') }}">
            Dữ liệu API (/api/students)
        </a>
    </p>
</body>
</html>
"""


# ==========================================================
# HTML DANH SÁCH SINH VIÊN
# ==========================================================
STUDENTS_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Danh sách sinh viên</title>

    <style>
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            padding: 8px;
        }

        .filter-bar a {
            margin-right: 10px;
            text-decoration: none;
        }

        .filter-bar a.active {
            font-weight: bold;
            text-decoration: underline;
            color: red;
        }
    </style>
</head>

<body>

    <h2>Danh sách sinh viên</h2>

    <div class="filter-bar">

        <span>Thanh lọc:</span>

        <a
            href="{{ url_for('student_list') }}"
            class="{% if not selected_lop %}active{% endif %}"
        >
            Tất cả
        </a>

        {% for lop in all_classes %}

            <a
                href="{{ url_for('student_list', lop=lop) }}"
                class="{% if selected_lop.lower() == lop.lower() %}active{% endif %}"
            >
                {{ lop }}
            </a>

        {% endfor %}

    </div>

    <br>

    {% if students %}

    <table>

        <thead>
            <tr>
                <th>MSSV</th>
                <th>Họ tên</th>
                <th>Lớp</th>
                <th>Điểm TB</th>
                <th>Xếp loại</th>
            </tr>
        </thead>

        <tbody>

            {% for s in students %}

            <tr>

                <td>
                    <a href="{{ url_for('student_detail', mssv=s.mssv) }}">
                        {{ s.mssv }}
                    </a>
                </td>

                <td>{{ s.name }}</td>

                <td>{{ s.lop }}</td>

                <td>{{ s.avg }}</td>

                <td>{{ s.rank }}</td>

            </tr>

            {% endfor %}

        </tbody>

    </table>

    {% else %}

        <p>Không có sinh viên phù hợp.</p>

    {% endif %}

    <br>

    <a href="{{ url_for('index') }}">
        Quay lại trang chủ
    </a>

</body>
</html>
"""


# ==========================================================
# HTML CHI TIẾT SINH VIÊN
# ==========================================================
DETAIL_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">

    <title>
        Chi tiết sinh viên - {{ student.name }}
    </title>

    <style>
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            padding: 8px;
        }
    </style>
</head>

<body>

    <h2>Thông tin sinh viên</h2>

    <p>
        <strong>MSSV:</strong>
        {{ student.mssv }}
    </p>

    <p>
        <strong>Họ tên:</strong>
        {{ student.name }}
    </p>

    <p>
        <strong>Lớp:</strong>

        <a href="{{ url_for('student_list', lop=student.lop) }}">
            {{ student.lop }}
        </a>
    </p>

    <p>
        <strong>Điểm TB:</strong>
        {{ student.avg }}
    </p>

    <p>
        <strong>Xếp loại:</strong>
        {{ student.rank }}
    </p>

    <hr>

    <h3>Bảng điểm từng học phần</h3>

    {% if scores %}

    <table>

        <thead>
            <tr>
                <th>Môn học</th>
                <th>Điểm số</th>
            </tr>
        </thead>

        <tbody>

            {% for subject, score in scores.items() %}

            <tr>
                <td>{{ subject }}</td>
                <td>{{ score }}</td>
            </tr>

            {% endfor %}

        </tbody>

    </table>

    {% else %}

        <p>Sinh viên chưa có điểm môn nào.</p>

    {% endif %}

    <br>

    <p>
        <a href="{{ url_for('export_student', mssv=student.mssv) }}">
            Tải bảng điểm (CSV)
        </a>
    </p>

    <p>
        Link rút gọn:

        <a href="{{ url_for('short_url', mssv=student.mssv) }}">
            {{ url_for('short_url', mssv=student.mssv) }}
        </a>
    </p>

    <p>
        <a href="{{ url_for('student_list') }}">
            Quay lại danh sách
        </a>
        |
        <a href="{{ url_for('index') }}">
            Trang chủ
        </a>
    </p>

</body>
</html>
"""


# ==========================================================
# HTML TÌM KIẾM SINH VIÊN
# ==========================================================
SEARCH_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Tìm kiếm sinh viên</title>

    <style>
        body {
            font-family: Arial, sans-serif;
        }

        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            padding: 8px;
        }

        input {
            padding: 6px;
            width: 300px;
        }

        button {
            padding: 6px 12px;
        }
    </style>
</head>

<body>

    <h2>Tìm kiếm sinh viên</h2>

    <form
        method="GET"
        action="{{ url_for('search_student') }}"
    >

        <input
            type="text"
            name="q"
            value="{{ q }}"
            placeholder="Nhập họ tên hoặc MSSV"
        >

        <button type="submit">
            Tìm kiếm
        </button>

    </form>

    <br>

    {% if q %}

        <p>
            Từ khóa tìm kiếm:
            <strong>{{ q }}</strong>
        </p>

        {% if results %}

            <table>

                <thead>
                    <tr>
                        <th>MSSV</th>
                        <th>Họ tên</th>
                        <th>Lớp</th>
                        <th>Điểm TB</th>
                        <th>Xếp loại</th>
                    </tr>
                </thead>

                <tbody>

                    {% for student in results %}

                    <tr>

                        <td>
                            <a href="{{ url_for('student_detail', mssv=student.mssv) }}">
                                {{ student.mssv }}
                            </a>
                        </td>

                        <td>{{ student.name }}</td>

                        <td>{{ student.lop }}</td>

                        <td>{{ student.avg }}</td>

                        <td>{{ student.rank }}</td>

                    </tr>

                    {% endfor %}

                </tbody>

            </table>

        {% else %}

            <p>
                Không tìm thấy sinh viên phù hợp.
            </p>

        {% endif %}

    {% endif %}

    <br>

    <p>
        <a href="{{ url_for('student_list') }}">
            Danh sách sinh viên
        </a>
        |
        <a href="{{ url_for('index') }}">
            Trang chủ
        </a>
    </p>

</body>
</html>
"""


# ==========================================================
# HÀM XỬ LÝ SINH VIÊN
# ==========================================================
def process_student(mssv, info):

    scores = list(
        info.get("scores", {}).values()
    )

    if not scores:

        avg_display = "-"

        rank_display = "-"

    else:

        avg = round(
            sum(scores) / len(scores),
            2
        )

        avg_display = avg

        if avg >= 8.5:

            rank_display = "Xuất sắc"

        elif avg >= 7.0:

            rank_display = "Khá"

        elif avg >= 5.0:

            rank_display = "Trung bình"

        else:

            rank_display = "Yếu"

    return {
        "mssv": mssv,
        "name": info["name"],
        "lop": info["lop"],
        "avg": avg_display,
        "rank": rank_display
    }


# ==========================================================
# CÂU 1 - TRANG CHỦ
# /
# ==========================================================
@app.route("/")
def index():

    total_students = len(STUDENTS)

    total_classes = len(
        set(
            student["lop"]
            for student in STUDENTS.values()
        )
    )

    return render_template_string(
        INDEX_HTML,
        total_students=total_students,
        total_classes=total_classes
    )


# ==========================================================
# CÂU 1 - API DANH SÁCH SINH VIÊN
# /api/students
# ==========================================================
@app.route("/api/students")
def api_students():

    return jsonify(STUDENTS)


# ==========================================================
# CÂU 2 - DANH SÁCH SINH VIÊN
# /students
# ==========================================================
@app.route("/students")
def student_list():

    lop_filter = request.args.get(
        "lop",
        ""
    ).strip()

    all_classes = sorted(
        list(
            set(
                student["lop"]
                for student in STUDENTS.values()
            )
        )
    )

    filtered_students = []

    for mssv, info in STUDENTS.items():

        if lop_filter:

            if info["lop"].lower() != lop_filter.lower():

                continue

        filtered_students.append(
            process_student(
                mssv,
                info
            )
        )

    return render_template_string(
        STUDENTS_HTML,
        students=filtered_students,
        all_classes=all_classes,
        selected_lop=lop_filter
    )


# ==========================================================
# CÂU 3 - CHI TIẾT SINH VIÊN
# /students/<mssv>
# ==========================================================
@app.route("/students/<mssv>")
def student_detail(mssv):

    if mssv not in STUDENTS:

        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    info = STUDENTS[mssv]

    student_processed = process_student(
        mssv,
        info
    )

    return render_template_string(
        DETAIL_HTML,
        student=student_processed,
        scores=info.get("scores", {})
    )


# ==========================================================
# CÂU 4 - LINK RÚT GỌN
# /sv/<mssv>
# Redirect 301 -> /students/<mssv>
# ==========================================================
@app.route("/sv/<mssv>")
def short_url(mssv):

    return redirect(
        url_for(
            "student_detail",
            mssv=mssv
        ),
        code=301
    )


# ==========================================================
# CÂU 5 - XUẤT BẢNG ĐIỂM CSV
# /students/<mssv>/export
# ==========================================================
@app.route("/students/<mssv>/export")
def export_student(mssv):

    if mssv not in STUDENTS:

        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    info = STUDENTS[mssv]

    output = io.StringIO()

    writer = csv.writer(
        output,
        lineterminator="\n"
    )

    writer.writerow([
        "hoc_phan",
        "diem"
    ])

    for subject, score in info.get(
        "scores",
        {}
    ).items():

        writer.writerow([
            subject,
            score
        ])

    response = make_response(
        output.getvalue()
    )

    response.headers["Content-Type"] = (
        "text/csv; charset=utf-8"
    )

    response.headers["Content-Disposition"] = (
        f'attachment; filename=diem_{mssv}.csv'
    )

    return response


# ==========================================================
# CÂU 6 - TÌM KIẾM AN TOÀN
# /search?q=...
# ==========================================================
@app.route("/search")
def search_student():

    q = request.args.get(
        "q",
        ""
    ).strip()

    results = []

    if q:

        keyword = q.lower()

        for mssv, info in STUDENTS.items():

            name = info["name"]

            if (
                keyword in name.lower()
                or keyword in mssv.lower()
            ):

                results.append(
                    process_student(
                        mssv,
                        info
                    )
                )

    return render_template_string(
        SEARCH_HTML,
        q=q,
        results=results
    )


# ==========================================================
# CHẠY ỨNG DỤNG
# ==========================================================
if __name__ == "__main__":

    app.run(
        debug=True,
        port=8000
    )
