# AttendAI — Smart Attendance & Engagement Monitoring System

A face-recognition based attendance system that I built to automate classroom attendance and also keep a basic check on student engagement (drowsiness, emotions) during lectures. Started as a simple "mark attendance with a webcam" idea and ended up growing into a small multi-module project with liveness detection and emotion analysis as well.

---

## Why I built this

Manual attendance in a classroom of 50-60 students takes up a good chunk of lecture time, and proxy attendance (one student marking present for another) is a common problem. The idea was to remove both issues — a camera recognizes each student's face automatically, marks them present, and also gives a rough sense of whether students are actually paying attention or dozing off.

---

## Tech Stack

- **Python 3.10**
- **OpenCV** — webcam access, image handling, drawing boxes/text on frames
- **face_recognition** (built on dlib) — face detection and face encoding/matching
- **MediaPipe** — face mesh landmarks for eye-aspect-ratio based drowsiness detection
- **DeepFace** (with TensorFlow backend) — facial emotion analysis
- **SQLite** — local database for students, attendance, and engagement logs
- **NumPy** — array handling for face encodings and EAR calculations

---

## Project Structure

```
AttendAI/
├── data/
│   └── attendai.db              # SQLite database
├── student_photos/              # captured photos during registration
├── faces_db/                    # (reserved for future use)
├── database.py                  # creates the database tables
├── register_student.py          # captures a student's face and saves encoding
├── check_students.py            # lists all registered students
├── delete_student.py            # removes a student record (used for cleaning test data)
├── mark_attendance.py            # basic face-match based attendance marking
├── mark_attendance_liveness.py  # attendance marking + blink-based liveness check
├── check_attendance.py          # shows attendance records with student names
├── engagement_detection.py      # EAR-based drowsiness detection + logging
├── check_engagement.py          # shows recent engagement logs
└── emotion_detection.py         # real-time emotion detection (top-2 emotions)
```

---

## How it actually works

### 1. Student Registration (`register_student.py`)

When a new student needs to be added, the webcam opens and the student presses `s` to capture a photo. The captured frame goes through `face_recognition.face_locations()` to detect the face, and then `face_recognition.face_encodings()` generates a 128-dimensional numeric vector — basically a "fingerprint" of that face.

This encoding (converted to bytes), along with the student's name, roll number, and photo path, gets inserted into the `students` table in SQLite.

A couple of safety checks are built in:
- If no face is detected in the captured frame, it asks to retry.
- If more than one face is detected, it rejects the capture (only one student should be in front of the camera at a time).
- Roll numbers are unique — trying to register the same roll number twice throws an `IntegrityError`, which is caught and reported.

### 2. Attendance Marking (`mark_attendance.py`)

This is the core loop. On startup, it loads every student's stored encoding from the database into memory (as lists of encodings, ids, names, roll numbers — all in the same order so they can be cross-referenced by index).

Then for every webcam frame:
- Detect all faces in the frame and generate their encodings
- Compare each detected face against every known encoding using `face_recognition.compare_faces()` (returns True/False matches) and `face_recognition.face_distance()` (returns actual numeric distances — lower means more similar)
- Pick the closest match using `np.argmin()` on the distances
- If that closest match is also within the tolerance (0.5 in this case — a bit stricter than the default 0.6), the face is considered recognized

Once recognized, the system checks the `attendance` table to see if that student already has an entry for today's date. If not, it inserts a new row with status "Present" and the current timestamp. A `marked_today` set keeps track of who's already been processed in the current session so the same person isn't repeatedly written to the database every frame.

Recognized faces get a green bounding box with their name; unrecognized faces get a red box labeled "Unknown."

### 3. Liveness Detection (`mark_attendance_liveness.py`)

This was added after realizing a flaw — a student could just hold up a photo of someone's face to the camera and mark fake attendance. To prevent that, this version adds a **blink check** before marking anyone present.

The core idea is **Eye Aspect Ratio (EAR)**: when eyes are open, the ratio of eye height to eye width is around 0.3; when closed, it drops below ~0.21. A real person blinks naturally within a few seconds, but a photograph never will.

`face_recognition.face_landmarks()` directly returns the coordinates of the `left_eye` and `right_eye` points, so EAR can be calculated without needing MediaPipe here.

For each recognized (but not-yet-marked) student, the system starts a 5-second "liveness window." During this window:
- If EAR drops below the threshold and then comes back up, that's registered as a blink (`blink_detected = True`)
- If a blink is detected within the window, the box turns green, attendance is marked, and the console prints "Liveness verified"
- If 5 seconds pass with no blink, the box turns red with "SPOOF? No blink detected" — and attendance is **not** marked

This is obviously not foolproof (a video of someone blinking could still pass), but it's a meaningful first layer of defense against the most common spoofing attempt — a static photo.

### 4. Engagement Detection (`engagement_detection.py`)

Separate from attendance — this module focuses on whether a student is actually awake and attentive during class, using **MediaPipe Face Mesh** (468 facial landmark points).

Out of those 468 points, 6 specific indices correspond to the left eye and 6 to the right eye. The same EAR formula from liveness detection is reused here, but for a different purpose:

- EAR above threshold → "Attentive"
- EAR below threshold for less than 2 seconds → "Eyes Closed" (probably just a blink)
- EAR below threshold for 2+ seconds continuously → "Drowsy"

Every 5 seconds, the current status gets logged into an `engagement_logs` table (date, time, status) — logging every single frame would flood the database given ~30fps video.

### 5. Emotion Detection (`emotion_detection.py`)

Uses **DeepFace** to analyze the dominant facial emotions (happy, sad, angry, neutral, surprise, fear, disgust) once every second (running it every frame would be too heavy — DeepFace loads a CNN model for this).

Instead of just showing the single "dominant" emotion (which tends to default to "neutral" most of the time for normal, non-exaggerated expressions), the output is sorted by confidence score and the **top 2 emotions with their percentages** are displayed — gives a more honest picture of what the model is actually seeing, e.g. "neutral (62.3%) | happy (18.1%)".

### 6. Verification scripts

- `check_students.py` — simple SELECT query listing all registered students
- `check_attendance.py` — uses a JOIN between `attendance` and `students` tables (since the attendance table only stores `student_id`, not names — this is basic normalization, avoids duplicating student info in every attendance row)
- `check_engagement.py` — shows the last 10 engagement log entries
- `delete_student.py` — removes a student's records from both `students` and `attendance` tables (used to clean up test/dummy entries)

---

## Database Schema

**students**
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | auto-increment |
| name | TEXT | |
| roll_no | TEXT | UNIQUE |
| encoding | BLOB | 128-d face encoding stored as bytes |
| photo_path | TEXT | |
| registered_on | TIMESTAMP | default current time |

**attendance**
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | auto-increment |
| student_id | INTEGER | FK → students.id |
| date | DATE | |
| time | TIME | |
| status | TEXT | default 'Present' |

**engagement_logs**
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | auto-increment |
| date | DATE | |
| time | TIME | |
| status | TEXT | Attentive / Eyes Closed / Drowsy |

---

## Setbacks & Debugging Notes (the real story)

Honestly, a huge chunk of the time on this project went into environment setup, not logic. A few things worth noting for anyone trying to replicate this on Windows:

- **dlib build failures**: `pip install dlib` tries to compile from source and needs CMake + Visual Studio C++ build tools. Eventually got it working through a prebuilt wheel instead of compiling.
- **numpy version conflicts**: this was the big one. `dlib`/`face_recognition` need numpy 1.x, while `opencv-python` and `tensorflow`/`deepface` pull in numpy 2.x. Ended up pinning `numpy<2` since face recognition is the core feature — opencv and tensorflow still work fine with the older numpy despite the dependency warnings.
- **protobuf conflicts**: MediaPipe 0.10.x needs `protobuf<4`, but TensorFlow 2.21 (which DeepFace depends on) needs `protobuf>=6`. Both libraries can't be satisfied at once in the same environment. The eventual workaround for the liveness module was to **avoid MediaPipe altogether** and use `face_recognition.face_landmarks()` instead, which already returns eye coordinates — so EAR could be calculated without MediaPipe in that script.
- **`np.ascontiguousarray()`**: after `cv2.flip()`, the numpy array sometimes becomes non-contiguous in memory, which dlib's face detector doesn't accept ("Unsupported image type" error) — wrapping the frame with this fixed it.
- **PowerShell execution policy**: had to run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once to allow venv activation scripts to run.

---

## Possible Future Additions

- Streamlit dashboard for attendance %, engagement trends, and low-attendance alerts
- Head pose estimation to flag "looking away" as a separate distraction signal
- Exporting attendance/engagement reports to Excel or PDF
- Multi-face engagement tracking (currently engagement detection is single-face)
- Email/SMS alerts to parents if attendance drops below 75%

---

## How to Run

```bash
# 1. Set up the database (one-time)
python database.py

# 2. Register students (run once per student)
python register_student.py

# 3. Mark attendance (with liveness check)
python mark_attendance_liveness.py

# 4. Run engagement detection during a lecture
python engagement_detection.py

# 5. Check records
python check_students.py
python check_attendance.py
python check_engagement.py
```
