from pymongo import MongoClient
import streamlit as st
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from io import *


class DForms:
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
        self.invigilatorDB=self.client["InvigilatorDB"]
        self.invigilatorCollection=self.invigilatorDB["Invigilators Collection"]

    def __del__(self):
        self.client.close()

    def display(self):
        # Tabs in Streamlit
        col1, col2 = st.columns([1,2],border=True)
        self.view(col1, col2)
    def generate_pdf(self, dataframe, invigDict, date, time, session):
        buffer = BytesIO()

        c = canvas.Canvas(buffer, pagesize=letter)

        # Page 1 - Basic Details
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, f"Exam Date: {date}")
        c.drawString(100, 735, f"Exam Time: {time}")
        c.drawString(100, 720, f"Session: {session}")

        # Table for Invigilator Details
        c.drawString(100, 700, "Invigilators Details:")
        y_position = 680
        for index, row in invigDict.iterrows():
            c.drawString(100, y_position, f"Room: {index} | {row['Invigilators']} (ID: {row['InvigilatorsID']})")
            y_position -= 20

        # Page 2 - Room Assignments
        c.showPage()  # New page for Room Assignments
        c.drawString(100, 750, "Room Assignments:")
        y_position = 730
        for room, hall_ticket_numbers in dataframe.items():
            c.drawString(100, y_position, f"Room {room}: {', '.join(map(str, hall_ticket_numbers))}")
            y_position -= 20

        # Final page - Stats (Student numbers)
        c.showPage()  # New page for Stats
        c.drawString(100, 750, "Student Stats:")
        c.drawString(100, 735, f"Number of Students Registered: {len(dataframe)}")
        # Example for present/absent stats, modify as needed
        c.drawString(100, 720, f"Present: {50}")  # Replace 50 with actual present count
        c.drawString(100, 705, f"Absent: {len(dataframe) - 50}")  # Replace with actual absent count

        c.save()  # Save the PDF into the buffer

        # Get the PDF data from the buffer
        buffer.seek(0)
        pdf_data = buffer.read()

        return pdf_data


    def view(self, col1, col2):
        # Exam Selection
        self.ExamName = col1.selectbox("Select the Exam", ["Mid 1", "Mid 2", "End Semester", "Lab Exams"])
        self.ExamType = col1.selectbox("Select the Exam Type", ["Regular", "Supplementary"])
        self.Batch = col1.selectbox("Select the Batch Year", self.studentsCollection.distinct("batch"))
        self.Branch = col1.selectbox("Select the Department", self.studentsCollection.distinct("branch"))

        # Define semester-related fields
        semesters = ["semister 1", "semister 2", "semister 3", "semister 4", 
                    "semister 5", "semister 6", "semister 7", "semister 8"]
        self.Semester = col1.selectbox("Select the Semester", semesters)
        
        # Check if all fields are selected
        if self.ExamName and self.ExamType and self.Batch and self.Branch and self.Semester:
            collection = f"{self.ExamName}-{self.ExamType}-{self.Batch}-{self.Branch}-{self.Semester}-Schedule"
            self.collection = self.scheduledDB[collection]
            
            # Get subjects for the selected exam schedule
            subject = self.collection.distinct("subject_name")
            selectedSubject = col2.selectbox("Please select the scheduled Subjects To See Room Arrangements", subject)
            
            if selectedSubject:
                retrievedDocuments = self.collection.find_one({"subject_name": selectedSubject})
                if retrievedDocuments:  # Check if any documents are returned
                    # Display Basic Details
                    col2.subheader("Basic Details", divider='blue')
                    col2.text(f"Date Of Conduction: {retrievedDocuments['date']}")
                    col2.text(f"Time Of Conduction: {retrievedDocuments['time']}")
                    col2.text(f"Session Of Conduction: {retrievedDocuments['session']}")
                    
                    # Invigilator Details
                    roomsList = retrievedDocuments['room_numbers']
                    invigilatorsList = retrievedDocuments['invigilators']
                    invigilatorIDList = retrievedDocuments['invigilator_ids']
                    invigDict = pd.DataFrame({'Invigilators': invigilatorsList, 'InvigilatorsID': invigilatorIDList}, index=roomsList)
                    
                    col2.subheader("Invigilation Details", divider='blue')
                    col2.dataframe(invigDict)
                    
                    # Room Assignments (Rooming Arrangements)
                    col2.subheader("Rooming Arrangements Are Like This", divider='blue')
                    roomsDict = {}
                    for i in range(len(retrievedDocuments['room_numbers'])):
                        room = retrievedDocuments["room_numbers"][i]
                        roomValues = retrievedDocuments['room_details'][i]['hallTicketNumbers']
                        roomsDict[room] = roomValues
                    
                    # Prepare DataFrame for Room Assignments
                    dataframe = pd.DataFrame(roomsDict, index=[x for x in range(1, 21)])
                    col2.dataframe(dataframe)
                    
                    # Button to trigger PDF generation and download
                    if col2.button("Download Dform Here", use_container_width=True, type='primary'):
                        pdf = self.generate_pdf(dataframe, invigDict, retrievedDocuments['date'], retrievedDocuments['time'], retrievedDocuments['session'])
                        # Provide the path to the generated PDF file for download
                        col2.download_button(label="Download the Exam Schedule PDF", data=pdf, file_name="exam_schedule.pdf", mime="application/pdf")
                else:
                    col2.error("No documents found for the selected subject.")


