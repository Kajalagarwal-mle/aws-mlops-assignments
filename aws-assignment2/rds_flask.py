import os
import pymysql
from flask import Flask
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

# Database connection details
DB_HOST = os.getenv("DB_HOST", "database-3.cc8rwhxooogl.ap-southeast-1.rds.amazonaws.com")  # Update with actual RDS endpoint
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password")
DB_NAME = os.getenv("DB_NAME", "mydb")

def insert_log():
    """Inserts a log entry with the current timestamp and returns the last inserted log."""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO logs (timestamp) VALUES (NOW())")
            conn.commit()

            # Fetch the last inserted log entry
            cursor.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 1")
            last_log = cursor.fetchone()

        conn.close()
        return last_log, None
    except Exception as e:
        return None, str(e)

def get_all_logs():
    """Fetches all log entries from the database."""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM logs ORDER BY id DESC")
            logs = cursor.fetchall()
        
        conn.close()
        return logs, None
    except Exception as e:
        return None, str(e)
		
@app.route("/")
def home():
    """API route that inserts a log and returns the last inserted log."""
    log_entry, error = insert_log()
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"message": "Log Inserted Successfully!", "log_entry": log_entry}), 200
	
@app.route("/logs")
def logs():
    """API route to fetch all logs."""
    logs, error = get_all_logs()
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"logs": logs}), 200
	

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085)
