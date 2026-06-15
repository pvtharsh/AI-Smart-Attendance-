import sqlite3

conn = sqlite3.connect('data/attendai.db')
cursor = conn.cursor()

cursor.execute("SELECT id, name, roll_no, registered_on FROM students")
students = cursor.fetchall()

print("\nRegistered Students:")
print("-" * 50)
for s in students:
    print(f"ID: {s[0]} | Name: {s[1]} | Roll: {s[2]} | Date: {s[3]}")

conn.close()