import cv2
import face_recognition
import sqlite3
import numpy as np
from datetime import datetime

def load_known_faces():
    conn = sqlite3.connect('data/attendai.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, roll_no, encoding FROM students")
    students = cursor.fetchall()
    conn.close()

    known_encodings = []
    known_ids = []
    known_names = []
    known_rolls = []

    for student_id, name, roll_no, encoding_blob in students:
        encoding = np.frombuffer(encoding_blob, dtype=np.float64)
        known_encodings.append(encoding)
        known_ids.append(student_id)
        known_names.append(name)
        known_rolls.append(roll_no)

    return known_encodings, known_ids, known_names, known_rolls


def mark_attendance(student_id, name, roll_no):
    conn = sqlite3.connect('data/attendai.db')
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')
    now_time = datetime.now().strftime('%H:%M:%S')

    cursor.execute('''
        SELECT * FROM attendance WHERE student_id = ? AND date = ?
    ''', (student_id, today))

    existing = cursor.fetchone()

    if existing:
        conn.close()
        return False
    else:
        cursor.execute('''
            INSERT INTO attendance (student_id, date, time, status)
            VALUES (?, ?, ?, 'Present')
        ''', (student_id, today, now_time))
        conn.commit()
        conn.close()
        return True


def run_attendance():
    print("Known faces load ho rahe hain...")
    known_encodings, known_ids, known_names, known_rolls = load_known_faces()

    if len(known_encodings) == 0:
        print("Koi student registered nahi hai! Pehle register karo.")
        return

    print(f"{len(known_encodings)} students loaded.")
    print("Camera khulegi — 'q' press karo quit karne ke liye\n")

    cap = cv2.VideoCapture(0)
    marked_today = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera nahi mili!")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame = np.ascontiguousarray(rgb_frame)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)

            name = "Unknown"
            color = (0, 0, 255)

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    student_id = known_ids[best_match_index]
                    name = known_names[best_match_index]
                    roll_no = known_rolls[best_match_index]
                    color = (0, 255, 0)

                    if student_id not in marked_today:
                        marked = mark_attendance(student_id, name, roll_no)
                        if marked:
                            print(f"Attendance marked: {name} ({roll_no})")
                        marked_today.add(student_id)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("AttendAI - Mark Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_attendance()