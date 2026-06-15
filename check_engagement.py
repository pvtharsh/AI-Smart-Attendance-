import sqlite3

conn = sqlite3.connect('data/attendai.db')
cursor = conn.cursor()

cursor.execute("SELECT date , time , status FROM engagement_logs ORDER BY id DESC LIMIT 10")
logs = cursor.fetchall()

print('\n Engagement logs (latest 10):')
print("-" * 50)

for l in logs:
    print(f"Date: {l[0]} | Time: {l[1]} | Status: {l[2]}")

conn.close()