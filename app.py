from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


# ==============================
# DATABASE CONNECTION
# ==============================

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


# ==============================
# HOME PAGE
# ==============================

@app.route("/")
def home():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM tasks
        ORDER BY id DESC
    """)

    tasks = cursor.fetchall()

    cursor.close()
    db.close()

    total_tasks = len(tasks)

    completed_tasks = sum(
        1 for task in tasks
        if task["status"] == "Completed"
    )

    pending_tasks = total_tasks - completed_tasks

    return render_template(
        "index.html",
        tasks=tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks
    )


# ==============================
# ADD TASK
# ==============================

@app.route("/add", methods=["POST"])
def add_task():

    title = request.form["title"]
    description = request.form["description"]
    priority = request.form["priority"]

    db = get_db_connection()
    cursor = db.cursor()

    query = """
        INSERT INTO tasks
        (title, description, priority, status)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (title, description, priority, "Pending")
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("home"))


# ==============================
# COMPLETE TASK
# ==============================

@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE tasks
        SET status = 'Completed'
        WHERE id = %s
    """, (task_id,))

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("home"))


# ==============================
# DELETE TASK
# ==============================

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM tasks
        WHERE id = %s
    """, (task_id,))

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("home"))


# ==============================
# RUN APPLICATION
# ==============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)