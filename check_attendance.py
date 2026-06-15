import sqlite3

conn = sqlite3.connect('data/attendai.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT students.name, students.roll_no, attendance.date, attendance.time, attendance.status
    FROM attendance
    JOIN students ON attendance.student_id = students.id
''')

records = cursor.fetchall()

print("\nAttendance Records:")
print("-" * 60)
for r in records:
    print(f"Name: {r[0]} | Roll: {r[1]} | Date: {r[2]} | Time: {r[3]} | Status: {r[4]}")

conn.close()