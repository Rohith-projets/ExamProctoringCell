from pymongo import MongoClient
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os

class Validation:
    def __init__(self):
        try:
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
        except Exception as e:
            st.error(f"Database connection error: {e}")

    def __del__(self):
        self.client.close()

    def display(self):
        tab1, tab2 = st.tabs(["View Validation", "Edit Validation"])
        
        with tab1:
            st.subheader("View Validation")
            self.view()
        with tab2:
            st.subheader("Edit Validations", divider='blue')
            self.edit() 

    def view(self):
        try:
            col1, col2 = st.columns([1, 2], border=True)
            self.ExamName = col1.selectbox("Select the Exam", ["Mid 1", "Mid 2", "End Semester"], key="view_exam")
            self.ExamType = col1.selectbox("Select the Exam Type", ["Regular", "Supplementary"], key="view_exam_type")
            self.Batch = col1.selectbox("Select the Batch Year", self.studentsCollection.distinct("batch"), key="view_batch")
            self.Branch = col1.selectbox("Select the Department", self.studentsCollection.distinct("branch"), key="view_branch")
            
            semesters = ["semister 1", "semister 2", "semister 3", "semister 4", "semister 5", "semister 6", "semister 7", "semister 8"]
            self.Semester = col1.selectbox("Select the Semester", semesters, key="view_semester")
            
            if self.ExamName and self.ExamType and self.Batch and self.Branch and self.Semester:
                collection = f"{self.ExamName}-{self.ExamType}-{self.Batch}-{self.Branch}-{self.Semester}-Validations"
                scheduledCollection = f"{self.ExamName}-{self.ExamType}-{self.Batch}-{self.Branch}-{self.Semester}-Schedule"
                self.scheduledCollection = self.scheduledDB[scheduledCollection]
                self.collection = self.validationDB[collection]
                subjects = self.collection.distinct("subject")
                selectedSubject = col2.selectbox("Select Subject", subjects, key="view_subject")
                
                document = self.scheduledCollection.find_one({"subject_name": selectedSubject})
                if document:
                    selectedRoom = col2.selectbox("Select Room", document.get('room_numbers', []), key="view_room")
                    
                    if selectedRoom and selectedSubject:
                        retrievedDocuments = list(self.collection.find({"subject": selectedSubject, "room_number": selectedRoom}))
                        if retrievedDocuments:
                            validationDataFrame = pd.DataFrame(retrievedDocuments)[[
                                "hall_ticket_number", "studentName","studentBooketNumber", 'studentFaceRecognitionStatus', 'studentQRCodeStatus', 'studentThumbStatus', 'StudentsFinalStatus'
                            ]]
                            col2.dataframe(validationDataFrame)
                            # add button to download the pdf
                            if col2.button("Download Validation Sheet", use_container_width=True, type='primary'):
                                file_path = self.generate_exam_pdf(selectedSubject, selectedRoom, validationDataFrame,document)
                                with open(file_path, "rb") as file:
                                    st.download_button(label="Download PDF", data=file, file_name=os.path.basename(file_path), mime="application/pdf")

                        else:
                            col2.error("No documents found for the selected subject.")
                else:
                    col2.error("No schedule found for the selected subject.")
        except Exception as e:
            st.error(f"Error while fetching validation data: {e}")
    
    # create a method that will create the pdf for selected input
    def fetch_schedule_details(self,subject,document):
        if document:
            return document.get("date", "N/A"), document.get("time", "N/A")
        return "N/A", "N/A"
    def generate_exam_pdf(self,subject, room, data,document):
        file_path = f"exam_attendance_{subject}_{room}.pdf"
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Fetch date and time from Schedule DB
        exam_date, exam_time = self.fetch_schedule_details(subject,document)
        
        # Title
        title = Paragraph(f"<b>Exam Attendance Sheet</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Exam Details
        details = [
            ["Date & Time:", f"{document['date']}, {document['time']}"],
            ["Examination:", f"{self.ExamName} - {self.ExamType}"],
            ["Batch:", self.Batch],
            ["Branch:", self.Branch],
            ["Semester:", self.Semester],
            ["Room No:", room],
            ["Subjects:", subject]
        ]
        table_details = Table(details, colWidths=[100, 300])
        table_details.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ]))
        elements.append(table_details)
        elements.append(Spacer(1, 12))
        
        # Table Header
        table_data = [["S. No", "H.T. No", "Name of Candidate", "Booklet No", "Signature"]]
        
        # Adding student data
        for idx, row in enumerate(data.itertuples(), start=1):
            table_data.append([idx, row.hall_ticket_number, row.studentName, row.studentBooketNumber, ""])
        
        table = Table(table_data, colWidths=[40, 100, 180, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 12))
        
        # Footer
        footer_details = [
            ["Number of Candidates Registered:", len(data)],
            ["Number of Candidates Present:", ""],
            ["Number of Candidates Absent:", ""],
        ]
        footer_table = Table(footer_details, colWidths=[200, 200])
        elements.append(footer_table)
        elements.append(Spacer(1, 20))
        
        # Signature Fields
        signatures = [["Signature of Invigilator", "Signature of Chief Superintendent"]]
        sig_table = Table(signatures, colWidths=[200, 200])
        sig_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black)
        ]))
        elements.append(sig_table)
        
        doc.build(elements)
        return file_path


    def edit(self):
        try:
            col1, col2 = st.columns([1, 2], border=True)
            self.ExamName = col1.selectbox("Select the Exam", ["Mid 1", "Mid 2", "End Semester", "Lab Exams"], key="edit_exam")
            self.ExamType = col1.selectbox("Select the Exam Type", ["Regular", "Supplementary"], key="edit_exam_type")
            self.Batch = col1.selectbox("Select the Batch Year", self.departmentsCollection.distinct("batch"), key="edit_batch")
            self.Branch = col1.selectbox("Select the Department", self.departmentsCollection.distinct("branch"), key="edit_branch")
            
            semesters = ["semister 1", "semister 2", "semister 3", "semister 4", "semister 5", "semister 6", "semister 7", "semister 8"]
            self.Semester = col1.selectbox("Select the Semester", semesters, key="edit_semester")
            
            if self.ExamName and self.ExamType and self.Batch and self.Branch and self.Semester:
                collection_name = f"{self.ExamName}-{self.ExamType}-{self.Batch}-{self.Branch}-{self.Semester}-Validations"
                self.collection = self.validationDB[collection_name]
                subjects = self.collection.distinct("subject")
                selected_subject = col1.selectbox("Select Subject", subjects, key="edit_subject")
                
                if selected_subject:
                    hall_ticket_numbers = [doc.get("hall_ticket_number") for doc in self.collection.find({"subject": selected_subject}, {"hall_ticket_number": 1})]
                    
                    if hall_ticket_numbers:
                        hall_ticket_number = col1.selectbox("Select Hall Ticket Number", hall_ticket_numbers, key="edit_hall_ticket")
                        options = col2.radio("Select the field to validate", ["QR Code Status", "Face Status", "Thumb Status", "Final Status"], key="edit_validation_field")
                        status_option = col2.selectbox("Select Status", [True, False], key="edit_status")
                        
                        if col2.button("Confirm Update", use_container_width=True, type='primary', key="edit_confirm"):
                            field_map = {
                                "QR Code Status": "studentQRCodeStatus",
                                "Face Status": "studentFaceRecognitionStatus",
                                "Thumb Status": "studentThumbStatus",
                                "Final Status": "StudentsFinalStatus"
                            }
                            field_to_update = field_map.get(options)
                            
                            if field_to_update:
                                result = self.collection.update_one({"hall_ticket_number": hall_ticket_number, "subject": selected_subject}, {"$set": {field_to_update: status_option}})
                                
                                if result.modified_count == 1:
                                    col2.success(f"{options} updated successfully!")
                                else:
                                    col2.error("Update failed. Please try again.")
                    else:
                        col1.error("No hall ticket numbers found for the selected subject.")
        except Exception as e:
            st.error(f"Error while updating validation data: {e}")
