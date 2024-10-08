import cv2
import face_recognition
import mysql.connector
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import numpy as np
import datetime

# เชื่อมต่อกับฐานข้อมูล
db_conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="",
    database="face_db"
)

# สร้างโฟลเดอร์สำหรับเก็บรูปภาพใบหน้า
IMAGE_DIRECTORY = "vuejs_api/app/public/yovle8/face_pics"
if not os.path.exists(IMAGE_DIRECTORY):
    os.makedirs(IMAGE_DIRECTORY)

# ตัวแปรเก็บข้อมูลใบหน้า
face_encodings_list = []
captured_faces = []

# ฟังก์ชันบันทึกข้อมูลลงฐานข้อมูล
def register_face_data():
    global face_encodings_list, captured_faces
    person_name = name_entry.get().strip()
    department = department_entry.get().strip()

    if not person_name:
        messagebox.showwarning("Warning", "กรุณากรอกชื่อ")
        return

    if not department:
        messagebox.showwarning("Warning", "กรุณากรอกแผนก")
        return

    cursor = db_conn.cursor()
    
    # ตรวจสอบว่ามีชื่ออยู่ในฐานข้อมูลแล้วหรือไม่
    cursor.execute("SELECT id FROM staffs WHERE displayName = %s", (person_name,))
    result = cursor.fetchone()

    if result:
        messagebox.showwarning("Warning", "ชื่อซ้ำ กรุณาใช้ชื่ออื่น")
        return

    # บันทึกข้อมูลใหม่
    if captured_faces:
        image_path = save_face_image(captured_faces[0], person_name)
        cursor.execute("INSERT INTO staffs (displayName, dept, face_img) VALUES (%s, %s, %s)", (person_name, department, image_path))
        new_staff_id = cursor.lastrowid

        if face_encodings_list:
            encoding_data = face_encodings_list[0].tobytes()
            cursor.execute("INSERT INTO faces (staffId, faceData) VALUES (%s, %s)", (new_staff_id, encoding_data))
            db_conn.commit()
            messagebox.showinfo("Success", f"บันทึกข้อมูลสำเร็จ: ชื่อ {person_name}, แผนก {department}")
        else:
            messagebox.showwarning("Error", "ไม่พบข้อมูลใบหน้า")
    else:
        messagebox.showwarning("Error", "ไม่สามารถบันทึกภาพใบหน้าได้")

# ฟังก์ชันบันทึกรูปใบหน้า
def save_face_image(face_img, name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name.replace(' ', '_')}_{timestamp}.jpg"
    save_path = os.path.join(IMAGE_DIRECTORY, filename)

    if face_img.ndim == 3 and face_img.shape[2] == 3:
        image_to_save = Image.fromarray(face_img)
        image_to_save.save(save_path)
    else:
        raise ValueError("รูปภาพที่บันทึกไม่ถูกต้อง")

    return f"face_pics/{filename}"

# ฟังก์ชันอัพเดตภาพจากกล้อง
def refresh_frame():
    global face_encodings_list, captured_faces
    ret, frame = webcam_feed.read()

    if ret:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        try:
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            face_encodings_list = face_recognition.face_encodings(rgb_frame, face_locations)
        except Exception as e:
            print(f"Error during face recognition: {e}")
            return

        captured_faces = []
        for (top, right, bottom, left) in face_locations:
            margin = 15
            top = max(0, top - margin)
            right = min(frame.shape[1], right + margin)
            bottom = min(frame.shape[0], bottom + margin)
            left = max(0, left - margin)

            face_region = frame[top:bottom, left:right]
            if face_region.shape[2] == 3:
                captured_faces.append(cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB))

            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)

        frame_for_display = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=frame_for_display)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    window.after(10, refresh_frame)

# ฟังก์ชันปิดโปรแกรม
def close_program():
    webcam_feed.release()
    db_conn.close()
    window.destroy()

# ตั้งค่า GUI ใหม่
window = tk.Tk()
window.title("ระบบลงทะเบียนใบหน้า")
window.geometry("800x600")

video_label = tk.Label(window)
video_label.grid(row=0, column=0, columnspan=2)

name_entry = tk.Entry(window, font=('Arial', 16))
name_entry.grid(row=1, column=0, padx=10, pady=10)
name_entry.insert(0, "ชื่อ")

department_entry = tk.Entry(window, font=('Arial', 16))
department_entry.grid(row=1, column=1, padx=10, pady=10)
department_entry.insert(0, "แผนก")

save_button = tk.Button(window, text="บันทึกข้อมูล", command=register_face_data, font=('Arial', 16))
save_button.grid(row=2, column=0, padx=10, pady=10)

exit_button = tk.Button(window, text="ออก", command=close_program, font=('Arial', 16))
exit_button.grid(row=2, column=1, padx=10, pady=10)

# เริ่มกล้อง
webcam_feed = cv2.VideoCapture(0)

refresh_frame()
window.mainloop()
