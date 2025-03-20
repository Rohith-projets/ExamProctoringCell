import streamlit as st
import pandas as pd
from pymongo import MongoClient
from streamlit_option_menu import option_menu

# Session state initialization
if 'invigilatorID' not in st.session_state:
    st.session_state.invigilatorID = None
if 'invigilator' not in st.session_state:
    st.session_state.invigilator = None

class Login:
    def __init__(self):
        # MongoDB connection
        self.client = MongoClient(st.secrets['database']['clientLink'])
        self.scheduledDB = self.client["ScheduledExams"]
        self.studentsCollection = self.client["StudentsDB"]["StudentsCollection"]
        self.teachersCollection = self.client["TeachersDB"]["TeachersCollection"]
        self.departmentsCollection = self.client["DepartmentsDB"]["Departments"]
        self.roomsCollection = self.client["RoomsDB"]["RoomsCollection"]
        self.validationDB = self.client["validationDB"]
        self.invigilatorDB = self.client["InvigilatorDB"]

    def display(self):
        # Sidebar navigation
        with st.sidebar:
            selected_option = option_menu(
                "Select Stage",
                ["Login", "Schedule", "Validate", "See Validations"],
                menu_icon='list',
                icons=['person', 'calendar', 'check-circle', 'eye'],
                default_index=0
            )

        # Display corresponding section
        if selected_option == "Login":
            self.login()
        elif selected_option == "Schedule":
            self.schedule()
        elif selected_option == "Validate":
            self.validate()
        elif selected_option == "See Validations":
            self.see_validations()

    def login(self):
        col1, col2 = st.columns([1.5, 2], gap="medium",border=True)
        col2.subheader("Login", divider='green')
        emp_id = col2.text_input("Enter Your Employee ID")

        if col2.button("Login", use_container_width=True, type='primary'):
            result = self.validate_login(emp_id, col1)
            if result:
                col2.success("Your credentials are valid. Check details on the left.")
            else:
                col2.warning("Invalid credentials. Please try again.")

    def validate_login(self, emp_id, col1):
        teacher = self.teachersCollection.find_one({"empID": emp_id}, {"_id": 0})
        if teacher:
            col1.subheader("Your Details", divider="blue")
            for key, value in teacher.items():
                col1.text(f"{key}: {value}")
            st.session_state['invigilatorID'] = emp_id
            st.session_state['invigilator'] = f"{teacher['fullname']} (ID: {emp_id})"
            return True
        return False

    def schedule(self):
        if st.session_state['invigilatorID']:
            col1, col2 = st.columns([1, 2], gap="medium",border=True)
            collection_names = self.invigilatorDB.list_collection_names()

            if collection_names:
                collection = col1.selectbox("Select the Exam to Check Your Schedule", collection_names)
                collectionList=collection.split('_')
                if collection:
                    invig_collection = self.invigilatorDB[collection]
                    docs = invig_collection.find({
                        "invigilatorID": st.session_state['invigilatorID'],
                        "invigilator": st.session_state['invigilator']
                    }, {"_id": 0, 'invigilator': 0, 'invigilatorID': 0, 'semester': 0, 'branch': 0, 'batch': 0})
                    col2.subheader('Primary Details',divider='blue')
                    col2.text(f"Exam Name : {collectionList[0]}")
                    col2.text(f"Exam Type : {collectionList[1]}")
                    col2.text(f"Batch : {collectionList[2]}")
                    col2.text(f"Branch : {collectionList[3]}")
                    data = list(docs)
                    if data:
                        df = pd.DataFrame(data)
                        col2.header("Invigilation Details", divider='blue')
                        col2.dataframe(df)
                    else:
                        col2.warning("No schedule found for the selected exam.")
            else:
                col1.warning("No exam schedules available.")
        else:
            st.warning("Please login to view your schedule.")

    def validate(self):
        col1, col2 = st.columns([1,2], border=True)
        collection = col1.selectbox("Select the validation type", self.scheduledDB.list_collection_names())
        
        if collection:
            collection_data = self.scheduledDB[collection]
            
            date = col1.selectbox("Select date", collection_data.distinct("date"))
            subject = col1.selectbox("Select subject", collection_data.distinct("subject"))
            session = col1.selectbox("Select session", collection_data.distinct("session"))
            
            if date and subject and session:
                # Corrected field name: 'subject' instead of 'ssubject'
                exam_data = collection_data.find_one(
                    {'date': date, 'subject': subject, 'session': session},
                    {'rooms': 1, 'roomDetails': 1, '_id': 0}
                )
                
                if exam_data and 'rooms' in exam_data:
                    selected_room = col1.selectbox("Select room", exam_data['rooms'])
                    
                    # Fetch hall ticket numbers for the selected room
                    room_details = next(
                        (room for room in exam_data.get('roomDetails', []) if room['roomNumber'] == selected_room), 
                        None
                    )
                    
                    if room_details:
                        roll_number = col1.selectbox("Select roll number", room_details.get('hallTicketNumbers', []))
                        
                        if roll_number:
                            # Corrected variable names
                            verification_type = col2.selectbox("Select verification type", ['QR Status', 'Face Status', 'Thumb Status'])
                            
                            if verification_type == 'QR Status':
                                col2.success(f"QR verification for {roll_number} is pending.")
                            elif verification_type == 'Face Status':
                                col2.success(f"Face verification for {roll_number} is pending.")
                            elif verification_type == 'Thumb Status':
                                col2.success(f"Thumb verification for {roll_number} is pending.")
                    else:
                        col1.warning("No hall ticket numbers found for the selected room.")
                else:
                    col1.warning("No rooms found for the selected date, subject, and session.")

    def see_validations(self):
        st.title("See Validations")
        st.write("This section will display validation reports.")

if __name__ == "__main__":
    Login().display()
