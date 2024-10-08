import cv2
from ultralytics import YOLO
import face_recognition
import mysql.connector
import numpy as np
import os
from datetime import datetime
import sys

# รับ ID จาก arguments ที่ส่งมา
current_time_id = sys.argv[1]
print(f"Processing ID: {current_time_id}")

# โหลดโมเดล YOLO
yolo_model = YOLO('yolov8n.pt')

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def connect_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="face_db"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection failed: {err}")
        exit()

# เชื่อมต่อฐานข้อมูล
conn = connect_database()
cursor = conn.cursor(dictionary=True)

# ดึงข้อมูลใบหน้าจากฐานข้อมูล
cursor.execute('''
SELECT f.staffId, s.displayName as name, f.id as faceId, f.faceData 
FROM staffs s
JOIN faces f ON f.staffId=s.id
''')
faces_in_db = cursor.fetchall()

# ตรวจสอบการดึงข้อมูล
if len(faces_in_db) == 0:
    print("No face data found.")
    conn.close()
    exit()

# แปลงข้อมูลใบหน้าให้เป็น numpy array
all_face_encodings = [np.frombuffer(face["faceData"], dtype=np.float64) for face in faces_in_db]
print("Faces loaded from database.")

# ฟังก์ชันบันทึกข้อมูลการข้ามเส้น
def log_passage(person_name, direction, captured_frame):
    timestamp = datetime.now()
    filename = f"vuejs_api/app/public/yovle8/captures/{person_name}_{direction}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    cv2.imwrite(filename, captured_frame)
    file_for_db = f"captures/{person_name}_{direction}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"

    cursor.execute('''
        INSERT INTO passes (time_id, name, timestamp, direction, image_path)
        VALUES (%s, %s, %s, %s, %s)
    ''', (current_time_id, person_name, timestamp, direction, file_for_db))
    conn.commit()

    print(f"Logged: {person_name} crossed {direction} at {timestamp}")

# เปิดการจับภาพวิดีโอจากกล้อง
video_stream = cv2.VideoCapture(0)
if not video_stream.isOpened():
    print("Error: Cannot open video stream.")
    conn.close()
    exit()

count_in, count_out = 0, 0
object_tracking = {}
recognized_faces = {}
center_x = None

# วนลูปการจับภาพ
while True:
    ret, frame = video_stream.read()
    if not ret:
        print("Failed to capture video frame.")
        break

    h, w, _ = frame.shape
    if center_x is None:
        center_x = int(w / 2)

    # ตรวจจับวัตถุด้วย YOLO
    yolo_results = yolo_model.track(frame, conf=0.5, verbose=False, classes=[0], persist=True)
    if not yolo_results:
        continue

    # แสดงผลเส้นกลางจอและการนับ
    display_frame = yolo_results[0].plot()
    cv2.line(display_frame, (center_x, 0), (center_x, h), (0, 0, 255), 2)
    cv2.putText(display_frame, f"IN={count_in} OUT={count_out}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # ย่อขนาด frame สำหรับการตรวจจับใบหน้า
    resized_frame = cv2.resize(frame, (frame.shape[1] // 4, frame.shape[0] // 4))
    rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

    # ตรวจจับใบหน้าและเข้ารหัสใบหน้า
    face_locations = face_recognition.face_locations(rgb_resized_frame)
    face_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
        cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)

        name = "Unknown"
        face_distances = face_recognition.face_distance(all_face_encodings, face_encoding)
        if face_distances.size > 0:
            min_dist_idx = np.argmin(face_distances)
            min_dist = face_distances[min_dist_idx]
            threshold = 0.5

            if min_dist < threshold:
                name = faces_in_db[min_dist_idx]["name"]
                if name not in recognized_faces:
                    recognized_faces[name] = True

        cv2.putText(display_frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # ตรวจจับวัตถุและอัพเดทการติดตาม
    for result in yolo_results:
        for idx, box in enumerate(result.boxes.xyxy):
            track_id = str(int(result.boxes.id[idx])) if result.boxes.id is not None else None
            if not track_id:
                continue

            if track_id not in object_tracking:
                object_tracking[track_id] = {"left": int(box[0]), "right": int(box[2])}
            else:
                current_left = int(box[0])
                current_right = int(box[2])
                previous_position = object_tracking[track_id]
                object_tracking[track_id] = {"left": current_left, "right": current_right}

                if previous_position["left"] < center_x and current_left >= center_x:
                    count_in += 1
                    log_passage(name, "in", frame)
                elif previous_position["right"] > center_x and current_right <= center_x:
                    count_out += 1
                    log_passage(name, "out", frame)

    cv2.imshow('YOLO and Face Recognition', display_frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # กด ESC เพื่อออก
        break

# ปิดการทำงานเมื่อออก
video_stream.release()
cv2.destroyAllWindows()
conn.close()
