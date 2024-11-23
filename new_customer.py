import cv2
import numpy as np
import face_recognition as face_rec
import os
import base64
import mysql.connector
from flask import jsonify
from datetime import datetime

# Path for saving face images
path = 'images_database'
os.makedirs(path, exist_ok=True)  # Ensure the directory exists

# Load known faces and names from the database
known_faces = []
known_names = []

# MySQL database connection
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'supermarket'
}

# Function to connect to the database
def connect_to_db():
    return mysql.connector.connect(**db_config)

# Load known faces from the database
def load_known_faces_from_db():
    global known_faces, known_names
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("SELECT name, face_encoding, image_path FROM customers")
    rows = cursor.fetchall()
    for name, encoding, image_path in rows:
        known_names.append(name)
        known_faces.append(np.frombuffer(encoding, dtype=np.float64))
    cursor.close()
    connection.close()

load_known_faces_from_db()

# Function to save new customer to the database
def save_new_customer_to_db(name, phone, id_number, area, face_encoding, image_path):
    connection = connect_to_db()
    cursor = connection.cursor()
    sql = """
    INSERT INTO customers (name, phone, id_number, area, face_encoding, image_path)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE name=%s, phone=%s, area=%s, image_path=%s
    """
    cursor.execute(sql, (name, phone, id_number, area, face_encoding.tobytes(), image_path,
                         name, phone, area, image_path))
    connection.commit()
    cursor.close()
    connection.close()

# Function to generate video frames
def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break

        resized_frame = cv2.resize(frame, (640, 480))
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

        # Detect faces and draw bounding boxes
        face_locations = face_rec.face_locations(rgb_frame)
        face_encodings = face_rec.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_rec.compare_faces(known_faces, face_encoding, tolerance=0.5)  # Adjusted tolerance
            name = ""
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]

            # Draw bounding box and label the recognized face
            cv2.rectangle(resized_frame, (left, top), (right, bottom), (255, 0, 255), 2)
            cv2.putText(resized_frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Encode the frame for streaming
        ret, buffer = cv2.imencode('.jpg', resized_frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Function to recognize and store face
def recognize_and_store_face(request, enroll=False):
    image_data = request.json['image']
    # Decode the image
    image_data = image_data.split(',')[1]
    image_data = base64.b64decode(image_data)
    np_array = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_rec.face_locations(rgb_frame)
    face_encodings = face_rec.face_encodings(rgb_frame, face_locations)

    if len(face_encodings) == 0:
        return jsonify(status='error', message='No face detected')

    if enroll:
        # Enroll new user
        data = request.get_json()
        name = data['name']
        phone = data['phone']
        id_number = data['id']
        area = data['area']

        # Save the image with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{name}_{timestamp}.jpg"
        path = 'static/images_database'
        image_path = os.path.join(path, image_filename)

        # Save the image
        cv2.imwrite(image_path, img)

        path = 'images_database'
        image_path = os.path.join(path, image_filename)
        
        # Save customer details to the database
        save_new_customer_to_db(name, phone, id_number, area, face_encodings[0], image_path)
        return jsonify(message="Face enrolled and stored successfully!")
    
    matches = face_rec.compare_faces(known_faces, face_encodings[0], tolerance=0.5)  # Adjusted tolerance
    if True in matches:
        first_match_index = matches.index(True)
        name = known_names[first_match_index]
        return jsonify(status='success', message=name)
    else:
        return jsonify(status='success', message='Unknown')
