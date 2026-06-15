import sqlite3

conn = sqlite3.connect('data/attendai.db')
cursor = conn.cursor()

roll_no_to_delete = "7887"

# Pehle student ka id nikalo
cursor.execute("SELECT id FROM students WHERE roll_no = ?", (roll_no_to_delete,))
result = cursor.fetchone()

if result:
    student_id = result[0]

    # Attendance table se delete karo
    cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))

    # Students table se delete karo
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))

    conn.commit()
    print(f"Roll No {roll_no_to_delete}Deleted succesfully!")
else:
    print(f"Roll No {roll_no_to_delete} Not Found Data.")

conn.close()