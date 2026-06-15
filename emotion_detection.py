import cv2
from deepface import DeepFace
import numpy as np
import time

print("Camera opens - 'q' press it and for quiting \n")

cap = cv2.VideoCapture(0)

last_check_time = 0
current_emotion = "Detecting..."
while True:
    ret , frame = cap.read()
    if not ret:
        print("Camera not found")
        break

    frame = cv2.flip(frame , 1)

    #har 1 secound mein emotion check kro it is very heavy 
    if time.time() - last_check_time > 1:
        try:
            result = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=False
            )
            emotions = result[0]['emotion']

            # Sabse zyada 2 emotions nikaalo
            sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
            top1_name, top1_score = sorted_emotions[0]
            top2_name, top2_score = sorted_emotions[1]

            current_emotion = f"{top1_name} ({top1_score:.1f}%) | {top2_name} ({top2_score:.1f}%)"

        except Exception as e:
            current_emotion = "No Face"

        last_check_time = time.time()

    cv2.putText(frame, f"Emotion: {current_emotion}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    cv2.imshow("AteendAI - Emotion Detection" , frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()