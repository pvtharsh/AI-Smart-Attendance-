import sqlite3

def create_database():
    connection = sqlite3.connect('data/attendai.db')
    cursor = connection.cursor()

    #students Table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            encoding BLOB,
            photo_path TEXT,
            registered_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Attendance Table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date DATE,
            time TIME,
            status TEXT DEFAULT 'Present',
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')

    connection.commit()
    connection.close()
    print("Database created Successfully!")


if __name__ == "__main__":
    create_database()
    