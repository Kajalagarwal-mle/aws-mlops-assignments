import os
import pymysql
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# Database connection details
DB_HOST = os.getenv("DB_HOST", "database-3.cc8rwhxooogl.ap-southeast-1.rds.amazonaws.com")  # Update with actual RDS endpoint
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password")
DB_NAME = os.getenv("DB_NAME", "mydb")

def insert_log():
    """Inserts a log entry with the current timestamp."""
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
        conn.close()
        return None
    except Exception as e:
        return str(e)

@app.route("/")
def home():
    """API route that inserts a log and returns a response."""
    error = insert_log()
    if error:
        return f"Error: {error}", 500
    return "Log Inserted Successfully!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085)

