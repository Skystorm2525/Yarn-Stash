from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, abort
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)
DATABASE = "yarnstash.db"
app.secret_key = "yarnstash_secret"
app.config["UPLOAD_FOLDER"] = "uploads"

if not os.path.exists("uploads"):
    os.makedirs("uploads")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------
# INIT DB
# -------------------------
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS yarn (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT,
            color_name TEXT,
            yarn_weight TEXT,
            skeins_owned INTEGER DEFAULT 0,
            image_filename TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            required_skeins INTEGER,
            pattern_id INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS project_yarn (
            project_id INTEGER,
            yarn_id INTEGER,
            skeins_used INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            file_name TEXT,
            folder_id INTEGER
        )
    """)

    conn.commit()
    conn.close()


# -------------------------
# DASHBOARD
# -------------------------

@app.route("/")
def dashboard():
    conn = get_db()

    total_owned = conn.execute(
        "SELECT COALESCE(SUM(skeins_owned),0) FROM yarn"
    ).fetchone()[0]

    total_allocated = conn.execute(
        "SELECT COALESCE(SUM(skeins_used),0) FROM project_yarn"
    ).fetchone()[0]

    total_projects = conn.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_owned=total_owned,
        total_allocated=total_allocated,
        total_projects=total_projects
    )


# -------------------------
# YARN
# -------------------------

@app.route("/yarn")
def yarn():
    sort = request.args.get("sort", "brand")

    sort_options = {
        "brand": "y.brand_name ASC",
        "available": "(y.skeins_owned - COALESCE(SUM(py.skeins_used),0)) DESC",
        "weight": "y.yarn_weight ASC",
        "newest": "y.id DESC"
    }

    order_by = sort_options.get(sort, "y.brand_name ASC")

    conn = get_db()

    yarn_list = conn.execute(f"""
        SELECT y.*,
               COALESCE(SUM(py.skeins_used),0) AS allocated
        FROM yarn y
        LEFT JOIN project_yarn py ON y.id = py.yarn_id
        GROUP BY y.id
        ORDER BY {order_by}
    """).fetchall()

    conn.close()

    return render_template("yarn.html", yarn_list=yarn_list, current_sort=sort)


@app.route("/add", methods=["POST"])
def add_yarn():
    image = request.files.get("image")
    image_filename = None

    if image and image.filename:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        image_filename = filename

    conn = get_db()
    conn.execute(
        """INSERT INTO yarn 
           (brand_name, color_name, yarn_weight, skeins_owned, image_filename)
           VALUES (?, ?, ?, ?, ?)""",
        (
            request.form.get("brand_name"),
            request.form.get("color_name"),
            request.form.get("yarn_weight"),
            request.form.get("skeins_owned"),
            image_filename
        )
    )
    conn.commit()
    conn.close()
    return redirect(url_for("yarn"))


@app.route("/yarn/add", methods=["GET"])
def add_yarn_page():
    return render_template("add_yarn.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_yarn(id):
    conn = get_db()

    if request.method == "POST":
        current = conn.execute(
            "SELECT skeins_owned FROM yarn WHERE id=?",
            (id,)
        ).fetchone()["skeins_owned"]

        adjustment = int(request.form.get("skeins_owned") or 0)
        new_total = current + adjustment
        if new_total < 0:
            new_total = 0

        conn.execute(
            "UPDATE yarn SET brand_name=?, color_name=?, yarn_weight=?, skeins_owned=? WHERE id=?",
            (
                request.form.get("brand_name"),
                request.form.get("color_name"),
                request.form.get("yarn_weight"),
                new_total,
                id
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for("yarn"))

    yarn = conn.execute("SELECT * FROM yarn WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit_yarn.html", yarn=yarn)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_yarn(id):
    conn = get_db()
    conn.execute("DELETE FROM project_yarn WHERE yarn_id=?", (id,))
    conn.execute("DELETE FROM yarn WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("yarn"))


# -------------------------
# PROJECTS
# -------------------------

@app.route("/projects")
def projects():
    conn = get_db()
    projects = conn.execute("""
        SELECT p.*, patterns.name AS pattern_name
        FROM projects p
        LEFT JOIN patterns ON p.pattern_id = patterns.id
        ORDER BY p.name
    """).fetchall()
    conn.close()
    return render_template("projects.html", projects=projects)


@app.route("/projects/create", methods=["GET", "POST"])
def create_project():
    conn = get_db()

    if request.method == "POST":
        conn.execute(
            "INSERT INTO projects (name, required_skeins, pattern_id) VALUES (?, ?, ?)",
            (
                request.form.get("name"),
                request.form.get("required_skeins"),
                request.form.get("pattern_id") or None,
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for("projects"))

    patterns = conn.execute("SELECT id, name FROM patterns ORDER BY name").fetchall()
    conn.close()
    return render_template("create_project.html", patterns=patterns)


@app.route("/projects/<int:id>")
def project_detail(id):
    conn = get_db()

    project = conn.execute(
        "SELECT * FROM projects WHERE id=?",
        (id,)
    ).fetchone()

    yarn_used = conn.execute("""
        SELECT yarn.id AS yarn_id,
               yarn.brand_name,
               yarn.color_name,
               project_yarn.skeins_used
        FROM project_yarn
        JOIN yarn ON yarn.id = project_yarn.yarn_id
        WHERE project_yarn.project_id=?
    """, (id,)).fetchall()

    total_allocated = conn.execute("""
        SELECT COALESCE(SUM(skeins_used),0)
        FROM project_yarn
        WHERE project_id=?
    """, (id,)).fetchone()[0]

    remaining_needed = project["required_skeins"] - total_allocated

    all_yarn = conn.execute("SELECT * FROM yarn").fetchall()

    conn.close()

    return render_template(
        "project_detail.html",
        project=project,
        yarn_used=yarn_used,
        total_allocated=total_allocated,
        remaining_needed=remaining_needed,
        all_yarn=all_yarn
    )


@app.route("/projects/<int:id>/add_yarn", methods=["POST"])
def add_yarn_to_project(id):
    yarn_id = request.form.get("yarn_id")
    skeins_used = int(request.form.get("skeins_used") or 0)

    conn = get_db()

    owned = conn.execute(
        "SELECT skeins_owned FROM yarn WHERE id=?",
        (yarn_id,)
    ).fetchone()["skeins_owned"]

    allocated = conn.execute("""
        SELECT COALESCE(SUM(skeins_used),0)
        FROM project_yarn
        WHERE yarn_id=?
    """, (yarn_id,)).fetchone()[0]

    available = owned - allocated

    if skeins_used > available:
        flash("Not enough yarn available.", "error")
        conn.close()
        return redirect(url_for("project_detail", id=id))

    conn.execute(
        "INSERT INTO project_yarn (project_id, yarn_id, skeins_used) VALUES (?, ?, ?)",
        (id, yarn_id, skeins_used)
    )

    conn.commit()
    conn.close()
    return redirect(url_for("project_detail", id=id))


@app.route("/projects/<int:id>/remove_yarn/<int:yarn_id>", methods=["POST"])
def remove_yarn_from_project(id, yarn_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM project_yarn WHERE project_id=? AND yarn_id=?",
        (id, yarn_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("project_detail", id=id))


@app.route("/projects/delete/<int:id>", methods=["POST"])
def delete_project(id):
    conn = get_db()
    conn.execute("DELETE FROM project_yarn WHERE project_id=?", (id,))
    conn.execute("DELETE FROM projects WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("projects"))


# -------------------------
# PATTERNS
# -------------------------

@app.route("/patterns")
def patterns():
    conn = get_db()

    folders = conn.execute("SELECT * FROM folders ORDER BY name").fetchall()
    patterns = conn.execute("""
        SELECT *
        FROM patterns
        WHERE folder_id IS NULL
        ORDER BY name
    """).fetchall()

    conn.close()
    return render_template("patterns.html", folders=folders, patterns=patterns)


@app.route("/patterns/create", methods=["GET", "POST"])
def create_pattern():
    conn = get_db()

    if request.method == "POST":
        name = request.form.get("name")
        folder_id = request.form.get("folder_id")
        file = request.files.get("file")

        if not name:
            flash("Pattern name is required.", "error")
            conn.close()
            return redirect(url_for("create_pattern"))

        filename = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn.execute(
            "INSERT INTO patterns (name, file_name, folder_id) VALUES (?, ?, ?)",
            (name, filename, folder_id if folder_id else None)
        )

        conn.commit()
        conn.close()
        return redirect(url_for("patterns"))

    folders = conn.execute("SELECT * FROM folders ORDER BY name").fetchall()
    conn.close()
    return render_template("create_pattern.html", folders=folders)


@app.route("/folders/create", methods=["GET", "POST"])
def create_folder():
    conn = get_db()

    if request.method == "POST":
        name = request.form.get("name")

        if not name:
            flash("Folder name is required.", "error")
            conn.close()
            return redirect(url_for("create_folder"))

        conn.execute(
            "INSERT INTO folders (name) VALUES (?)",
            (name,)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("patterns"))

    conn.close()
    return render_template("create_folder.html")


@app.route("/folders/<int:id>")
def folder_detail(id):
    conn = get_db()
    folder = conn.execute(
        "SELECT * FROM folders WHERE id=?",
        (id,)
    ).fetchone()

    patterns = conn.execute(
        "SELECT * FROM patterns WHERE folder_id=? ORDER BY name",
        (id,)
    ).fetchall()

    conn.close()
    return render_template("folder_detail.html", folder=folder, patterns=patterns)


@app.route("/folders/delete/<int:id>", methods=["POST"])
def delete_folder(id):
    conn = get_db()

    # Delete all patterns inside this folder
    conn.execute(
        "DELETE FROM patterns WHERE folder_id=?",
        (id,)
    )

    # Then delete the folder
    conn.execute(
        "DELETE FROM folders WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()
    return redirect(url_for("patterns"))


@app.route("/patterns/<int:id>")
def pattern_detail(id):
    conn = get_db()
    pattern = conn.execute(
        "SELECT patterns.*, folders.name AS folder_name "
        "FROM patterns LEFT JOIN folders ON patterns.folder_id = folders.id "
        "WHERE patterns.id=?",
        (id,)
    ).fetchone()
    conn.close()
    return render_template("pattern_detail.html", pattern=pattern)


@app.route("/patterns/delete/<int:id>", methods=["POST"])
def delete_pattern(id):
    conn = get_db()
    conn.execute("DELETE FROM patterns WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("patterns"))


@app.route("/patterns/download/<int:id>")
def download_pattern(id):
    conn = get_db()
    pattern = conn.execute(
        "SELECT file_name FROM patterns WHERE id=?",
        (id,)
    ).fetchone()
    conn.close()

    if not pattern or not pattern["file_name"]:
        abort(404)

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        pattern["file_name"],
        as_attachment=True
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)