import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banking_survey.db")

def create_connection():
    db_path = os.path.join(os.path.expanduser("~"), "banking_survey.db")
    connection = sqlite3.connect(db_path)
    return connection

def create_tables():
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survey_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            answers TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

create_tables()

print("Database and table created successfully!")
