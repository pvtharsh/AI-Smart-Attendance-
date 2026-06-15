import cv2
import mediapipe as mp 
import numpy as np
import sqlite3
from datetime import datetime
import time

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces = 1,
    refine_landmarks = True,
    min_detection_confidence = 0.5,
    min_tracking_confidence=0.5
)

#mediapipe face mesh model setup for 468points to detect.

LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

# its specific points the 6-6 specific left and right eye 

EAR_THRESHOLD = 0.21
DROWSY_TIME_LIMIT = 2.0
#if ear value is 0.21 is lesser than marks Drowsy

def ear_distance(p1,p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

#calculate ear 

def calcualte_ear(landmarks , eye_indices , frame_w , frame_h):
    points = []
    for idx in eye_indices:
        lm = landmarks[idx]
        points.append((lm.x * frame_w , lm.y * frame_h))


    vertical1 = ear_distance(points[1], points[5])
    vertical2 = ear_distance(points[2] , points[4])
    horizontal = ear_distance(points[0] , points[3])

    ear = (vertical1 + vertical2) / (2.0 * horizontal)
    return ear


def log_engagement(status):
    conn = sqlite3.connect('data/attendai.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS engagement_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            time TIME,
            status TEXT
        )
    ''')

# it creates a new table for engagement_logs status (Attentive / Drowsy)

    today = datetime.now().strftime('%Y-%m-%d')
    now_time = datetime.now().strftime('%H:%M:%S')

    cursor.execute('INSERT INTO engagement_logs (date, time, status) VALUES (?, ?, ?)', (today, now_time, status))
    conn.commit()
    conn.close()

def run_engagement_detection():
    cap = cv2.VideoCapture(0)
    eyes_closed_start = None
    last_log_time = 0

    print("camera opens - 'q' press karo quit kare ke liye\n" )

    while True:
        ret , frame = cap.read()
        if not ret:
            print("Camera not found ..!")
            break

        frame = cv2.flip(frame , 1)
        frame_h, frame_w = frame.shape[:2]

        rgb_frame = cv2.cvtColor(frame , cv2.COLOR_BGR2RGB)
        rgb_frame = np.ascontiguousarray(rgb_frame)
        results = face_mesh.process(rgb_frame)

        status = "NO Face"
        color = (0,0,255)

        # There is a frame in which RGB convert into mediapipe 

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            left_ear = calcualte_ear(landmarks , LEFT_EYE , frame_w , frame_h)
            right_ear = calcualte_ear(landmarks , RIGHT_EYE , frame_w , frame_h)
            avg_ear = (left_ear + right_ear) / 2.0

            # if face finds then calculate the EAR then find average

            if avg_ear < EAR_THRESHOLD:
                if eyes_closed_start is None:
                    eyes_closed_start = time.time()

                closed_duration = time.time() - eyes_closed_start

                if closed_duration >= DROWSY_TIME_LIMIT:
                    status = 'Drowsy'
                    color = (0, 0 , 255)
                else:
                    status = "Eyes Closed"
                    color = (0 , 165 , 255)
            else:
                eyes_closed_start = None
                status = "Attentive"
                color = (0 , 255 , 0)

        #if eyes time taken of 2sec then it is Drowsy

            #log every 5 seconds
            # Log every 5 seconds
            if time.time() - last_log_time > 5:
                log_engagement(status)
                last_log_time = time.time()

            cv2.putText(frame, f"EAR: {avg_ear:.2f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        cv2.putText(frame, f"Status: {status}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("AttendAI - Engagement Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_engagement_detection()