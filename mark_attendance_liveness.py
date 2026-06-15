import cv2
import face_recognition
import sqlite3
import numpy as np
import time
from datetime import datetime

EAR_THRESHOLD = 0.21
BLINK_CHECK_DURATION = 5.0  # seconds


def ear_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


def calculate_ear(eye_points):
    # eye_points = list of 6 (x, y) tuples
    vertical1 = ear_distance(eye_points[1], eye_points[5])
    vertical2 = ear_distance(eye_points[2], eye_points[4])
    horizontal = ear_distance(eye_points[0], eye_points[3])

    return (vertical1 + vertical2) / (2.0 * horizontal)


def load_known_faces():
    conn = sqlite3.connect('data/attendai.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, roll_no, encoding FROM students")
    students = cursor.fetchall()
    conn.close()

    known_encodings, known_ids, known_names, known_rolls = [], [], [], []

    for student_id, name, roll_no, encoding_blob in students:
        encoding = np.frombuffer(encoding_blob, dtype=np.float64)
        known_encodings.append(encoding)
        known_ids.append(student_id)
        known_names.append(name)
        known_rolls.append(roll_no)

    return known_encodings, known_ids, known_names, known_rolls


def mark_attendance(student_id):
    conn = sqlite3.connect('data/attendai.db')
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')
    now_time = datetime.now().strftime('%H:%M:%S')

    cursor.execute('SELECT * FROM attendance WHERE student_id = ? AND date = ?', (student_id, today))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return False
    else:
        cursor.execute('INSERT INTO attendance (student_id, date, time, status) VALUES (?, ?, ?, ?)',
                       (student_id, today, now_time, 'Present'))
        conn.commit()
        conn.close()
        return True


def run_attendance_with_liveness():
    known_encodings, known_ids, known_names, known_rolls = load_known_faces()

    if len(known_encodings) == 0:
        print("Koi student registered nahi hai!")
        return

    print(f"{len(known_encodings)} students loaded.")
    print("Camera khulegi — 'q' press karo quit karne ke liye\n")

    cap = cv2.VideoCapture(0)

    blink_check_start = {}
    eyes_were_closed = {}
    blink_detected = {}
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
        face_landmarks_list = face_recognition.face_landmarks(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding, landmarks in zip(face_locations, face_encodings, face_landmarks_list):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)

            name = "Unknown"
            color = (0, 0, 255)
            status_text = ""

            # EAR calculate karo agar eyes landmarks available hain
            avg_ear = None
            if 'left_eye' in landmarks and 'right_eye' in landmarks:
                left_eye = landmarks['left_eye']
                right_eye = landmarks['right_eye']
                left_ear = calculate_ear(left_eye)
                right_ear = calculate_ear(right_eye)
                avg_ear = (left_ear + right_ear) / 2.0

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    student_id = known_ids[best_match_index]
                    name = known_names[best_match_index]
                    roll_no = known_rolls[best_match_index]

                    if student_id in marked_today:
                        color = (0, 255, 0)
                        status_text = "Already Marked"
                    else:
                        if student_id not in blink_check_start:
                            blink_check_start[student_id] = time.time()
                            eyes_were_closed[student_id] = False
                            blink_detected[student_id] = False

                        elapsed = time.time() - blink_check_start[student_id]

                        if avg_ear is not None:
                            if avg_ear < EAR_THRESHOLD:
                                eyes_were_closed[student_id] = True
                            else:
                                if eyes_were_closed[student_id]:
                                    blink_detected[student_id] = True
                                eyes_were_closed[student_id] = False

                        if blink_detected[student_id]:
                            color = (0, 255, 0)
                            status_text = "LIVE - Marking..."
                            marked = mark_attendance(student_id)
                            if marked:
                                print(f"Attendance marked: {name} ({roll_no}) - Liveness verified")
                            marked_today.add(student_id)
                        elif elapsed > BLINK_CHECK_DURATION:
                            color = (0, 0, 255)
                            status_text = "SPOOF? No blink detected"
                        else:
                            color = (0, 165, 255)
                            status_text = f"Checking liveness... {int(BLINK_CHECK_DURATION - elapsed)}s"

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            cv2.putText(frame, status_text, (left, top - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if avg_ear is not None:
                cv2.putText(frame, f"EAR: {avg_ear:.2f}", (left, bottom + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("AttendAI - Liveness Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_attendance_with_liveness()