import os
import base64
from pymongo import MongoClient
from bson.binary import Binary
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import streamlit as st

class DownloadPhotos:
    def __init__(self):
        # Database connections
        self.client = MongoClient("mongodb://localhost:27017/")
        self.scheduledDB = self.client["ScheduledExams"]
        self.studentsDB = self.client["StudentsDB"]
        self.studentsCollection = self.studentsDB["StudentsCollection"]
        self.teachersDB = self.client["TeachersDB"]
        self.teachersCollection = self.teachersDB["TeachersCollection"]
        self.departmentsDB = self.client["DepartmentsDB"]
        self.departmentsCollection = self.departmentsDB["Departments"]
        self.roomsDB = self.client["RoomsDB"]
        self.roomsCollection = self.roomsDB["RoomsCollection"]
        self.validationDB = self.client["validationDB"]
        self.invigilatorDB = self.client["InvigilatorDB"]
        self.invigilatorCollection = self.invigilatorDB["Invigilators Collection"]

    def save_photo(self, photo_data, folder_path, filename):
        try:
            # Handle Binary, Base64, or raw bytes
            if isinstance(photo_data, Binary) or isinstance(photo_data, bytes):
                image_data = photo_data
            elif isinstance(photo_data, str):
                if photo_data.startswith("data:image"):
                    photo_data = photo_data.split(",")[-1]
                image_data = base64.b64decode(photo_data)
            else:
                print(f"Skipping unsupported photo format for {filename}")
                return

            # Decode and save the image
            image = Image.open(BytesIO(image_data))
            image.save(os.path.join(folder_path, filename))
            print(f"✅ Saved photo: {filename}")  # Debug log

        except (UnidentifiedImageError, base64.binascii.Error, Exception) as e:
            print(f"❌ Skipping invalid image for {filename}: {e}")

    def download_photos(self):
        students = self.studentsCollection.find()

        for student in students:
            batch = student.get("batch")
            branch = student.get("branch")
            semester = student.get("semester")
            roll_number = student.get("roll_number")

            # Skip documents where all photos are None
            if not (student.get("front_photo") or student.get("left_photo") or student.get("right_photo")):
                continue

            # Folder structure: batch/branch/semester
            base_folder = os.path.join(batch, branch, f"Semester_{semester}")
            os.makedirs(base_folder, exist_ok=True)

            # Subfolders for photos
            folders = {
                "front_photo": os.path.join(base_folder, "Front Photos"),
                "left_photo": os.path.join(base_folder, "Left Photos"),
                "right_photo": os.path.join(base_folder, "Right Photos")
            }

            for key, folder_path in folders.items():
                os.makedirs(folder_path, exist_ok=True)
                photo_data = student.get(key)
                if photo_data:
                    print(f"🔍 Processing {key} for {roll_number}")  # Debug log
                    self.save_photo(photo_data, folder_path, f"{roll_number}_{key}.jpg")

# Streamlit App
st.title("📥 Download Student Photos")

if st.button("Download Photos"):
    downloader = DownloadPhotos()
    downloader.download_photos()
    st.success("✅ Photos downloaded successfully!")
