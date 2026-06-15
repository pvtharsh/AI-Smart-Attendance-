import cv2
import face_recognition
import sqlite3
import numpy as np
import os

def register_student(name, roll_no):
    print(f"\nRegistering: {name} | Roll No: {roll_no}")
    print("Camera khulegi — 's' press karo photo lene ke liye, 'q' press karo quit karne ke liye\n")

    cap = cv2.VideoCapture(0)

    captured_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera nahi mili!")
            break

        frame = cv2.flip(frame, 1)
        cv2.putText(frame, "Press 'S' to Capture | 'Q' to Quit",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Student: {name} | Roll: {roll_no}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("Face Registration - AttendAI", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            captured_frame = frame.copy()
            print("Photo captured!")
            break
        elif key == ord('q'):
            print("Registration cancelled.")
            cap.release()
            cv2.destroyAllWindows()
            return

    cap.release()
    cv2.destroyAllWindows()

    if captured_frame is None:
        return

    rgb_frame = cv2.cvtColor(captured_frame, cv2.COLOR_BGR2RGB)
    rgb_frame = np.ascontiguousarray(rgb_frame)
    print("DEBUG:", rgb_frame.shape, rgb_frame.dtype)


    face_locations = face_recognition.face_locations(rgb_frame)

    if len(face_locations) == 0:
        print("Koi face nahi mila! Dobara try karo.")
        return

    if len(face_locations) > 1:
        print("Multiple faces detected! Sirf ek student saamne rahe.")
        return

    face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
    encoding_blob = face_encoding.tobytes()

    photo_path = f"student_photos/{roll_no}_{name}.jpg"
    cv2.imwrite(photo_path, captured_frame)

    try:
        conn = sqlite3.connect('data/attendai.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO students (name, roll_no, encoding, photo_path)
            VALUES (?, ?, ?, ?)
        ''', (name, roll_no, encoding_blob, photo_path))

        conn.commit()
        conn.close()
        print(f"{name} successfully registered!")
        print(f"Photo saved at: {photo_path}")

    except sqlite3.IntegrityError:
        print(f"Roll No {roll_no} already registered hai!")


if __name__ == "__main__":
    print("=" * 40)
    print("   AttendAI - Student Registration")
    print("=" * 40)

    name = input("Student ka naam daalo: ").strip()
    roll_no = input("Roll Number daalo: ").strip()

    if name and roll_no:
        register_student(name, roll_no)
    else:
        print("Naam aur Roll Number dono zaroori hain!")