from pymongo import MongoClient
import streamlit as st
from datetime import datetime
import pandas as pd
from PIL import *

class Schedule:
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

    def __del__(self):
        self.client.close()

    def display(self):
        try:
            # Tabs in Streamlit
            tab1, tab2, tab3 = st.tabs(["Schedule Exams", "Edit Scheduled Exams", "View Schedules"])

            with tab1:
                col1, col2 = st.columns([1, 2], gap='small',border=True)

                col2.subheader("Schedule Exams")

                # Input fields for scheduling exams
                self.examName = col1.selectbox("Select the exam", ["Mid 1", "Mid 2", "End Semester", "Lab Exams"])
                self.examType = col1.selectbox("Select the exam type", ["Regular", "Supplementary"])
                self.batch = col1.selectbox("Select the batch year", self.studentsCollection.distinct("batch"))
                self.branch = col1.selectbox("Select the department", self.studentsCollection.distinct("branch"))

                # Define semester-related fields
                semesters = ["semister 1", "semister 2", "semister 3", "semister 4", 
                            "semister 5", "semister 6", "semister 7", "semister 8"]
                self.semester = col1.selectbox("Select the semester", semesters)

                if col1.checkbox("Continue Scheduling"):
                    if self.examName and self.examType and self.batch and self.branch and self.semester:
                        # Query to get subjects list based on batch, branch, and semester
                        department_data = self.departmentsCollection.find_one(
                            {"batch": self.batch, "branch": self.branch}
                        )

                        if department_data:
                            parentDict = department_data.get(self.semester, {})
                            finalLetter = self.semester.split(" ")[-1]
                            self.subjects = parentDict[f"semister_{finalLetter}_subjects"]
                            self.subjects_codes = parentDict[f"semister_{finalLetter}_subjects_codes"]
                            self.subjects_credits = parentDict[f"semister_{finalLetter}_subjects_credits"]
                            self.subjects_types = parentDict[f"semister_{finalLetter}_subjects_types"]

                            self.selectedSubject = col2.selectbox("Select the subject to schedule", self.subjects)

                            # Input for date and time
                            self.dateOfConduction = str(col2.date_input("Select the date of conduction"))
                            self.timeOfConductionStart = col2.text_input("Start time of the exam")
                            self.timeOfConductionEnd = col2.text_input("End time of the exam")
                            self.session = col2.selectbox("Select the session", ["Morning", "Afternoon"])

                            if self.selectedSubject and self.dateOfConduction and self.timeOfConductionStart and self.timeOfConductionEnd and self.session:
                                # Fetch and display teachers for invigilation
                                teacher_departments = self.teachersCollection.distinct("department")
                                selectedTeacherDepartments = col2.multiselect("Select teacher departments", teacher_departments)

                                if selectedTeacherDepartments:
                                    invigilators = []
                                    for dept in selectedTeacherDepartments:
                                        invigilators.extend(
                                            self.teachersCollection.find(
                                                {"department": dept}, {"fullname": 1, "empID": 1, "_id": 0}
                                            )
                                        )

                                    # Prepare list for multi-selection
                                    invigilator_options = {
                                        f"{teacher['fullname']} (ID: {teacher['empID']})": teacher['empID']
                                        for teacher in invigilators
                                    }

                                    self.selectedInvigilators = col2.multiselect(
                                        "Select invigilators", list(invigilator_options.keys())
                                    )

                                    if self.selectedInvigilators:
                                        # Map selected invigilators to their corresponding empIDs
                                        self.selectedInvigilatorIDs = [invigilator_options[name] for name in self.selectedInvigilators]

                                # Fetch and display room details
                                blocks = self.roomsCollection.distinct("block")
                                selectedBlocks = col2.multiselect("Select blocks", blocks)

                                if selectedBlocks:
                                    floors = []
                                    for block in selectedBlocks:
                                        block_floors = self.roomsCollection.find_one(
                                            {"block": block}, {"_id": 0}
                                        )
                                        if block_floors:
                                            floors.extend([key for key in block_floors.keys() if key.startswith("floor")])
                                    floors = list(set(floors))  # Remove duplicates
                                    selectedFloors = col2.multiselect("Select floors", floors)

                                    if selectedFloors:
                                        rooms = []
                                        for block in selectedBlocks:
                                            for floor in selectedFloors:
                                                floor_rooms = self.roomsCollection.find_one(
                                                    {"block": block}, {f"{floor}": 1, "_id": 0}
                                                )
                                                if floor_rooms and floor in floor_rooms:
                                                    rooms.extend(floor_rooms[floor])
                                        rooms = list(set(rooms))  # Remove duplicates
                                        self.selectedRooms = col2.multiselect("Select rooms", rooms)

                                if self.selectedInvigilators and self.selectedRooms:
                                    self.bookletNumbers = int(col2.text_input("Enter the starting Booklet Number"))
                                    self.parentDict = {
                                        "subject": self.selectedSubject,
                                        "date": self.dateOfConduction,
                                        "start-time": self.timeOfConductionStart,
                                        "end-time": self.timeOfConductionEnd,
                                        "session": self.session,
                                        "invigilators": self.selectedInvigilators,
                                        "invigilatorsID": self.selectedInvigilatorIDs,
                                        "rooms": self.selectedRooms,
                                        "roomDetails": [{} for _ in self.selectedRooms]  
                                    }
                                    if col2.checkbox("Complete Schedule for exam"):
                                        self.completeInfo(col1, col2)
                                        col2.subheader("Please verify once again")
                                        col2.json(self.parentDict)
                                else:
                                    col2.warning("Please select invigilators and rooms.")
                        else:
                            col2.error("No data found for the selected department and semester.")
                    else:
                        col2.warning("Please fill in all required fields.")
                else:
                    col2.info("Check the box to continue scheduling.")
            with tab3:
                self.view()
        except Exception as e:
            col2.warning(e)

    def completeInfo(self, col1, col2):
        try:
            if len(self.parentDict['rooms']) != len(self.parentDict["invigilators"]):
                col2.warning("The number of rooms and invigilators must be the same.")
                return
            
            # Convert semester to integer
            semester_number = int(self.semester[-1])

            # Fetch student roll numbers from MongoDB using limit and skip for efficiency
            self.roll_numbers = list(self.studentsCollection.find(
                {"batch": self.batch, "branch": self.branch, "semester": semester_number},
                {"roll_number": 1, "_id": 0}
            ).limit(len(self.selectedRooms) * 20))  # Limit to available bench capacity

            self.roll_numbers = [student["roll_number"] for student in self.roll_numbers]
            self.bookletNumbers2 = self.bookletNumbers + len(self.roll_numbers)
            col2.info(f"starting booklet number - {self.bookletNumbers}\nending booklet numbers - {self.bookletNumbers2}")
            self.parentDict["hallTicketNumbers"] = self.roll_numbers
            self.parentDict['bookletNumbers']=[x for x in range(self.bookletNumbers,self.bookletNumbers2+1)]

            # Compute available bench count
            self.mainCount = len(self.selectedRooms) * 20
            self.TotalCount = len(self.roll_numbers)

            # Display room allocation messages
            if self.mainCount >= self.TotalCount:
                col2.success(f"All students got benches for writing exams.\nEmpty benches: {self.mainCount - self.TotalCount}")
            else:
                col2.warning(f"Select more rooms. Additional benches needed: {self.TotalCount - self.mainCount}")

            # Assign students to rooms dynamically
            self.parentDict["roomDetails"] = self.assign_rooms_to_students()

            # Create the exam document
            exam_document = self.create_exam_document()

            # Create lists for invigilators and validation
            self.invigilatorsList = self.create_invigilator_list(exam_document)
            self.validationList = self.create_validation_list(exam_document)
            if col2.button("Fix This Schedule", use_container_width=True, type='primary'):
                invigilation_collection = self.invigilatorDB[f"{self.examName}-{self.examType}-{self.batch}-{self.branch}-{self.semester}-Invigilations"]
                schedule_exams_collection = self.scheduledDB[f"{self.examName}-{self.examType}-{self.batch}-{self.branch}-{self.semester}-Schedule"]
                validation_collection = self.validationDB[f"{self.examName}-{self.examType}-{self.batch}-{self.branch}-{self.semester}-Validations"]
                inserted_doc_schedule = schedule_exams_collection.insert_one(exam_document)
                inserted_doc_invigilation = invigilation_collection.insert_many(self.invigilatorsList)
                inserted_doc_validation = validation_collection.insert_many(self.validationList)
                col2.success("Uploaded")
        except Exception as e:
            col2.warning(e)   

    def assign_rooms_to_students(self):
        try:
            room_details = []
            count = 0
            for index, room in enumerate(self.selectedRooms):
                # Get students for the room, skip the previous ones and limit to 20
                students_cursor = self.studentsCollection.find(
                    {"batch": self.batch, "branch": self.branch, "semester": int(self.semester[-1])},
                    {"roll_number": 1, "_id": 0}
                ).skip(index * 20).limit(20)

                roll_numbers = [student["roll_number"] for student in students_cursor]
                
                # Calculate the available booklet numbers
                remaining_booklets = len(self.parentDict["hallTicketNumbers"]) - count
                if remaining_booklets > 0:
                    # Get a slice of booklet numbers based on the available count
                    booklet_numbers = self.parentDict['bookletNumbers'][count:count + min(remaining_booklets, 20)]
                    count += len(booklet_numbers)  # Update count based on number of booklets assigned

                # Ensure that the booklet_numbers and roll_numbers match the room's bench capacity
                room_details.append({
                    "roomNumber": room,
                    "invigilator": self.parentDict["invigilators"][index],
                    "invigilatorID": self.parentDict["invigilatorsID"][index],
                    "benchNumbers": list(range(1, 21)),
                    "hallTicketNumbers": roll_numbers + [None] * (20 - len(roll_numbers)),  # Fill empty benches with None
                    "bookletNumbers": booklet_numbers + [None] * (20 - len(booklet_numbers))  # Ensure booklet numbers match
                })
                
            return room_details
        except Exception as e:
            st.warning(e)

    def create_exam_document(self):
        try:
            return {
                "subject_name": self.selectedSubject,
                "subject_code": self.subjects_codes[self.subjects.index(self.selectedSubject)],
                "subject_credits": self.subjects_credits[self.subjects.index(self.selectedSubject)],
                "subject_types": self.subjects_types[self.subjects.index(self.selectedSubject)],
                "date": self.dateOfConduction,
                "time": f"{self.timeOfConductionStart} - {self.timeOfConductionEnd}",
                "session": self.session,
                "hall_ticket_numbers": self.roll_numbers,
                "room_numbers": self.selectedRooms,
                "invigilators": self.selectedInvigilators,
                "invigilator_ids": self.selectedInvigilatorIDs,
                "room_details": self.parentDict["roomDetails"],
                "bookletNumbers":self.parentDict["bookletNumbers"]
            }
        except Exception as e:
            st.warning(e)

    def create_invigilator_list(self, exam_document):
        try:
            return [
                {
                    "invigilator": exam_document["invigilators"][i],
                    "invigilatorID": exam_document["invigilator_ids"][i],
                    "roomNumber": exam_document["room_numbers"][i],
                    "roomCapacity": 20,
                    "date": exam_document["date"],
                    "time": exam_document["time"],
                    "subject": exam_document["subject_name"],
                    "subject_code": exam_document["subject_code"],
                    "subject_credits": exam_document["subject_credits"],
                    "subject_types": exam_document["subject_types"],
                    "semester": self.semester,
                    "branch": self.branch,
                    "batch": self.batch
                }
                for i in range(len(self.parentDict["rooms"]))
            ]
        except Exception as e:
            st.warning(e)
    def create_validation_list(self, exam_document):
        try:
            validation_list = []
            for i, roll_number in enumerate(self.roll_numbers):
                student = self.studentsCollection.find_one({"roll_number": roll_number}, {"fullname": 1, "_id": 0})
                validation_list.append({
                    "hall_ticket_number": roll_number,
                    "room_number": self.selectedRooms[i // 20],
                    "room_capacity": 20,
                    "date": exam_document["date"],
                    "time": exam_document["time"],
                    "subject": exam_document["subject_name"],
                    "subject_code": exam_document["subject_code"],
                    "subject_credits": exam_document["subject_credits"],
                    "subject_types": exam_document["subject_types"],
                    "semester": self.semester,
                    "branch": self.branch,
                    "batch": self.batch,
                    "studentName": student.get("fullname") if student else "Unknown",
                    "studentFaceRecognitionStatus": None,
                    "studentQRCodeStatus": None,
                    "studentThumbStatus": None,
                    "StudentsFinalStatus": None,
                    "studentBooketNumber":exam_document['bookletNumbers'][exam_document["hall_ticket_numbers"].index(roll_number)]
                })
            
            return validation_list
        except Exception as e:
            st.warning(e)
    def view(self):
        try:
            col1,col2=st.columns([1,2],border=True)
            self.ExamName = col1.selectbox("Select the Exam", ["Mid 1", "Mid 2", "End Semester", "Lab Exams"])
            self.ExamType = col1.selectbox("Select the Exam Type", ["Regular", "Supplementary"])
            self.Batch = col1.selectbox("Select the Batch Year", self.departmentsCollection.distinct("batch"))
            self.Branch = col1.selectbox("Select the Department", self.departmentsCollection.distinct("branch"))

            # Define semester-related fields
            semesters = ["semister 1", "semister 2", "semister 3", "semister 4", 
                        "semister 5", "semister 6", "semister 7", "semister 8"]
            self.Semester = col1.selectbox("Select the Semester", semesters)
            if self.ExamName and self.ExamType and self.Batch and self.Branch and self.Semester:
                collection=f"{self.ExamName}-{self.ExamType}-{self.Batch}-{self.Branch}-{self.Semester}-Schedule"
                self.collection = self.scheduledDB[collection]
                subject=self.collection.distinct("subject_name")
                selectedSubject=col2.selectbox("Please select the scheduled Subjects To See Room Arrangements",subject)
                if selectedSubject:
                    retrievedDocuments = list(self.collection.find({"subject_name": selectedSubject}))
                    if retrievedDocuments:  # Check if any documents are returned
                        for doc in retrievedDocuments:
                            col2.subheader("Basic Details", divider='blue')
                            col2.text(f"Date Of Conduction: {doc['date']}")
                            col2.text(f"Start Time Of Conduction: {doc['time']}")
                            col2.text(f"Session Of Conduction : {doc['session']}")
                            roomsList = []
                            invigilatorsList = []
                            invigilatorIDList=[]
                            for i in range(len(doc['room_numbers'])):
                                roomsList.append(doc['room_numbers'][i])
                                invigilatorsList.append(doc['invigilators'][i])
                                invigilatorIDList.append(doc['invigilator_ids'][i])
                            invigDict = pd.DataFrame({'Invigilators':invigilatorsList,'InvigilatorsID':invigilatorIDList},index=roomsList)
                            col2.subheader("Invigilation Details",divider='blue')
                            col2.dataframe(invigDict)
                            col2.subheader("Rooming Arrangements Are Like This", divider='blue')
                            roomsDict={}
                            for i in range(len(doc['room_numbers'])):
                                room=doc['room_numbers'][i]
                                roomValues=doc['room_details'][i]['hallTicketNumbers']
                                roomsDict[room] = roomValues
                            dataframe = pd.DataFrame(roomsDict, index=[x for x in range(1, 21)])
                            col2.dataframe(dataframe)
                    else:
                        col2.error("No documents found for the selected subject.")
        except Exception as e:
            st.warning(e)
