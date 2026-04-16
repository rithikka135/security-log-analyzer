from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB = "logs.db"

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        ip TEXT,
        status TEXT,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return "Security Log Analyzer Running"

# Add log
@app.route("/log", methods=["POST"])
def add_log():
    data = request.json

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs(username, ip, status) VALUES(?,?,?)",
        (data["username"], data["ip"], data["status"])
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Log added successfully"})

# Get logs
@app.route("/logs", methods=["GET"])
def get_logs():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs ORDER BY time DESC")
    rows = cur.fetchall()
    conn.close()

    logs = []
    for r in rows:
        logs.append({
            "id": r[0],
            "username": r[1],
            "ip": r[2],
            "status": r[3],
            "time": r[4]
        })

    return jsonify({"logs": logs})

# Analyze logs
@app.route("/analyze", methods=["GET"])
def analyze():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM logs")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM logs WHERE status='failed'")
    failed = cur.fetchone()[0]

    success = total - failed

    cur.execute("""
    SELECT ip, COUNT(*) as count
    FROM logs
    WHERE status='failed'
    GROUP BY ip
    HAVING count > 2
    """)
    suspicious = cur.fetchall()

    conn.close()

    return jsonify({
        "total_logs": total,
        "failed_attempts": failed,
        "successful_attempts": success,
        "suspicious_ips": suspicious
    })

# Serve UI
@app.route("/ui")
def ui():
    return send_file("../frontend/index.html")

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)