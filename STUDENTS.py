import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from pymongo import MongoClient
import pandas as pd
from bson.binary import Binary
from PIL import Image
from bson import Binary
from io import BytesIO
class Students:
    def __init__(self):
        self.client = MongoClient(st.secrets['database']['clientLink'])
        self.studentsDB = self.client["StudentsDB"]
        self.studentsCollection = self.studentsDB["StudentsCollection"]
        self.client1 = MongoClient("mongodb+srv://kr587925:Palyam25.in@cluster7.gxpko.mongodb.net/?retryWrites=true&w=majority&appName=CLUSTER7")
        self.internetDB = self.client1["StudentsDB"]
        self.internetCollection = self.internetDB["StudentsCollection"]
    def __del__(self):
        self.client.close()
        self.client1.close()
    def display(self):
        tab1, tab2, tab3 = st.tabs(["Register", "Edit", "Display"])
        # tab1 details are here
        with tab1:
            col1, col2 = st.columns([1, 2],border=True)          
            with col1:
                selectedOption = st.radio("Select the operation to perform",["Register Students", "Upload the photos", "Take photos and upload","upload finger prints", "Register Backlog Students","Upload Data To Internet","Upload ThumbPrints"])
                if selectedOption == "Register Students":
                    self.register(col1,col2)
                if selectedOption == "Upload the photos":
                    self.uploadPhoto(col1,col2)
                if selectedOption == "Take photos and upload":
                    self.takePhotos(col1, col2)
                if selectedOption == "upload finger prints":
                    self.uploadFingerPrint(col1,col2)
                if selectedOption == "Upload Data To Internet":
                    self.uploadDataToInternet(col1, col2)
                if selectedOption == "Upload ThumbPrints":
                    self.uploadThumbPrint(col1, col2)
                total_students = self.studentsCollection.count_documents({})
                style_metric_cards()
                col1.metric("Total Students", value=total_students)
        # Tab3 details are here
        with tab3:
            self.viewDetails(col1,col2)
        # Tab2 details are here   
        with tab2:
            st.header("You can perform edit operations here", divider='blue')
            col1, col2 = st.columns([1.5, 2], border=True)
            with col1:
                st.subheader("Select the mode",divider='blue')
                selectedOption = st.radio("How do you want to edit ?", ["Edits on group of students", "Edits On specific Students"])
                if selectedOption == "Edits On specific Students":
                    self.edits("Edits On specific Students",col1, col2)
                if selectedOption == "Edits on group of students":
                    self.edits("Edits on group of students", col1, col2)
                    
    def edits(self, editMode, col1, col2):
        self.batch = col1.selectbox("select the batch that you want to retrieve", self.studentsCollection.distinct("batch"))
        self.branch = col1.selectbox("select the branch that you want to retrieve", self.studentsCollection.distinct("branch"))
        self.semester = col1.selectbox("select the semester that you want to retrieve", self.studentsCollection.distinct("semester"))
        if self.batch and self.branch and self.semester:
            if editMode == "Edits On specific Students":
                roll_numbers = self.studentsCollection.find({"branch": self.branch, "batch": self.batch, "semester": self.semester}, {"roll_number": 1}).distinct("roll_number")
                if len(roll_numbers):
                    self.rollNumbers = col1.selectbox(f"Select the roll number to  the deatails", roll_numbers)
                    self.details = self.studentsCollection.find_one({"batch": self.batch, "branch": self.branch, "semester": self.semester, "roll_number": self.rollNumbers})
                    col2.subheader("Select Operation Here",divider='blue')
                    editOption = col2.radio("Select the type of edit that you want to perform", ["Add A Field", "Remove A Field", "Update A Field Value", "Remove the current value for a field", "Delete student","Edit student photo"])
                    with col2:
                        with st.expander(f"First document shown here"):
                            st.json(self.details)
                    if editOption == "Add A Field":
                        self.addField(col1, col2,"Edits On specific Students")
                    if editOption == "Remove A Field":
                        self.removeField(col1, col2,"Edits On specific Students")
                    if editOption == "Update A Field Value":
                        self.updateField(col1, col2,"Edits On specific Students")
                    if editOption == "Remove the current value for a field":
                        self.removeCurrentValue(col1, col2,"Edits On specific Students")
                    if editOption == "Delete student":
                        self.deleteStudent(col1, col2, "Edits On specific Students")
                    if editOption == "Edit student photo":
                        self.editOption(col1,col2)
                else:
                    st.warning("No documents are found please upload the data first")
            if editMode == "Edits on group of students":
                documents=self.studentsCollection.find({"batch": self.batch, "branch": self.branch, "semester": self.semester}).to_list()
                if len(documents):
                    style_metric_cards()
                    col1.metric("Total documnets found",value=len(documents))
                    col2.subheader("Select Operation here",divider='blue')
                    editOption = col2.radio("Select the optio to edit",["Add A Field", "Remove A Field", "Update A Field Value", "Remove the current value for fields", "Delete group"])
                    with col2:
                        with st.expander(f"First document shown here"):
                            st.json(documents[0])
                    if editOption == "Add A Field":
                        self.addField(col1, col2, "Edits on group of students")
                    if editOption == "Remove A Field":
                        self.removeField(col1, col2, "Edits on group of students")
                    if editOption == "Update A Field Value":
                        self.updateField(col1, col2, "Edits on group of students")
                    if editOption == "Remove the current value for fields":
                        self.removeCurrentValue(col1, col2, "Edits on group of students")
                    if editOption == "Delete group":
                        self.deleteStudent(col1, col2, "Edits on group of students")
                else:
                    st.warning("No documents are found upload the data first")
    def editOption(self, col1, col2):
        typeOfPhoto = col1.radio("Select the type of photo to edit", ["front_photo", "left_photo", "right_photo"])
        takePhoto = col2.camera_input("Take Photo")
        with col1:
            document=self.studentsCollection.find_one({"batch":self.batch,"branch":self.branch,"semester":self.semester,"roll_number":self.rollNumbers})
            st.subheader("Front Photo",divider='green')
            if "front_photo" in document:
                st.image(document["front_photo"])
            else:
                st.info(f"{document['roll_number']} does'nt contain front photo.\nPlease Upload it first.")
            st.subheader("Left Photo",divider='green')
            if "left_photo" in document:
                st.image(document["left_photo"])
            else:
                st.info(f"{document['roll_number']} does'nt contain left photo.\nPlease Upload it first.")
            st.subheader("Right Photo",divider='green')
            if "right_photo" in document:
                st.image(document["right_photo"])
            else:
                st.info(f"{document['roll_number']} does'nt contain right photo.\nPlease Upload it first.")

        if takePhoto:
            col2.image(takePhoto, use_container_width=True)
            if col2.button("Fix this photo", use_container_width=True, type="primary"):
                try:
                    # Perform the update operation in the collection
                    edited = self.studentsCollection.update_one(
                        {
                            "branch": self.branch,
                            "batch": self.batch,
                            "semester": self.semester,
                            "roll_number": self.rollNumbers
                        },
                        {"$set": {typeOfPhoto: Binary(takePhoto.getvalue())}}
                    )
                    
                    if edited.acknowledged:
                        col2.success("Photo replaced successfully")
                        col2.image(takePhoto)
                    else:
                        st.error("Operation failed")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            col2.warning("Please take a photo before proceeding.")
    def register(self, col1, col2):
        with col2:
            file_uploader = st.file_uploader("Upload the CSV file", type=["csv"])
            if file_uploader:
                try:
                    # Read the uploaded CSV file
                    df = pd.read_csv(file_uploader)
                    if not df.empty:
                        # Insert data into MongoDB
                        inserted_ids = self.studentsCollection.insert_many(df.to_dict(orient="records"))
                        total_documents = len(inserted_ids.inserted_ids)
                        
                        # Display success message with metric cards
                        if total_documents:
                            st.success(f"{total_documents} students registered successfully!")
                            with st.container():
                                style_metric_cards()
                                st.metric(label="Total Students Registered", value=total_documents)
                    else:
                        st.error("The uploaded CSV file is empty.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
    def uploadPhoto(self, col1, col2):
        with col2:
            # Fetch distinct options for batch, branch, and semester
            self.batch = st.selectbox("Select the batch:", self.studentsCollection.distinct("batch"))
            self.branch = st.selectbox("Select the branch:", self.studentsCollection.distinct("branch"))
            self.semester = st.selectbox("Select the semester:", self.studentsCollection.distinct("semester"))
            
            if self.batch and self.branch and self.semester:
                # Fetch roll numbers based on selected filters
                roll_numbers = self.studentsCollection.find(
                    {"branch": self.branch, "batch": self.batch, "semester": self.semester},
                    {"roll_number": 1}
                ).distinct("roll_number")
                
                if roll_numbers:
                    self.rollNumbers = st.selectbox("Select the roll number to upload the photo:", roll_numbers)
                    select_type = st.selectbox(
                        "Select the type of photo to upload:",
                        ["Front Photo", "Left Photo", "Right Photo"]
                    )

                    # File uploader for photo
                    uploaded_photo = st.file_uploader(f"Upload the {select_type.lower()} (JPG, JPEG, PNG):", type=["jpg", "jpeg", "png"])
                    
                    if uploaded_photo:
                        st.image(uploaded_photo, use_container_width=True)
                        
                        if st.button(f"Confirm to upload {select_type.lower()} photo", use_container_width=True, type="primary"):
                            try:
                                # Convert photo to binary format
                                photo_binary = Binary(uploaded_photo.read())
                                
                                # Map photo type to field name in MongoDB
                                photo_field_map = {
                                    "Front Photo": "front_photo",
                                    "Left Photo": "left_photo",
                                    "Right Photo": "right_photo"
                                }
                                update_field = photo_field_map.get(select_type)
                                
                                # Update the photo in the database
                                edited = self.studentsCollection.update_one(
                                    {
                                        "branch": self.branch,
                                        "batch": self.batch,
                                        "semester": self.semester,
                                        "roll_number": self.rollNumbers
                                    },
                                    {"$set": {update_field: photo_binary}}
                                )
                                
                                if edited.acknowledged:
                                    st.success(f"{select_type} uploaded successfully!")
                                else:
                                    st.error("Failed to upload photo. Please try again.")
                            except Exception as e:
                                st.error(f"An error occurred: {e}")
                    else:
                        st.info("Please upload a photo before confirming.")
                else:
                    st.warning(f"No roll numbers found for Batch: {self.batch}, Branch: {self.branch}, Semester: {self.semester}.")
    def takePhotos(self, col1, col2):
        with col2:
            self.batch = st.selectbox("Select the batch: ", self.studentsCollection.distinct("batch"))
            self.branch = st.selectbox("Select the branch: ", self.studentsCollection.distinct("branch"))
            self.semester = st.selectbox("Select the semester: ", self.studentsCollection.distinct("semester"))
            
            if self.batch and self.branch and self.semester:
                roll_numbers = self.studentsCollection.find(
                    {"branch": self.branch, "batch": self.batch, "semester": self.semester},
                    {"roll_number": 1}
                ).distinct("roll_number")
                
                if len(roll_numbers):
                    self.rollNumbers = st.selectbox("Select the roll number to upload the photo", roll_numbers)
                    select_type = st.selectbox(
                        "Select the type of photo that you want to upload",
                        ["Front Photo", "Left Photo", "Right Photo"]
                    )
                    
                    photo = st.camera_input(f"Upload the {select_type.lower()}")
                    if photo:
                        st.image(photo, use_container_width=True)
                        
                        if st.button(f"Confirm to upload photo as {select_type.lower()}", use_container_width=True, type="primary"):
                            # Convert the photo to binary format
                            binary_photo = Binary(photo.getvalue())
                            
                            # Map photo type to the corresponding MongoDB field
                            photo_field_map = {
                                "Front Photo": "front_photo",
                                "Left Photo": "left_photo",
                                "Right Photo": "right_photo"
                            }
                            
                            update_field = photo_field_map.get(select_type)
                            
                            # Update the document in MongoDB
                            edited = self.studentsCollection.update_one(
                                {
                                    "branch": self.branch,
                                    "batch": self.batch,
                                    "semester": self.semester,
                                    "roll_number": self.rollNumbers
                                },
                                {"$set": {update_field: binary_photo}}
                            )
                            
                            if edited.acknowledged:
                                st.success("Photo uploaded successfully")
                                col2.image(photo)
                            else:
                                st.error("Operation failed")
    def viewDetails(self, col1, col2):
        st.header("View The Details Of A Student", divider='green')
        self.batch = st.selectbox("Select the Batch : ", self.studentsCollection.distinct("batch"))
        self.branch = st.selectbox("Select the Barnch : ", self.studentsCollection.distinct("branch"))
        self.semester = st.selectbox("select the Semister : ", self.studentsCollection.distinct("semester"))
        if self.batch and self.branch and self.semester:
            roll_numbers = self.studentsCollection.find({"branch": self.branch, "batch": self.batch, "semester": self.semester}, {"roll_number": 1}).distinct("roll_number")
            if len(roll_numbers):
                self.rollNumbers = st.selectbox("Select the roll number to see deatails", roll_numbers)
                if self.batch and self.branch and self.semester and self.rollNumbers:
                    col1, col2 = st.columns([1, 2], border=True)
                    document = self.studentsCollection.find_one({"batch": self.batch, "branch": self.branch, "semester": self.semester, "roll_number": self.rollNumbers})
                    with col2:
                        st.subheader(document["fullname"], divider='blue')
                        detailsDict = {
                            "batch": document["batch"],
                            "branch": document["branch"],
                            "semester": document["semester"],
                            "roll_number": document["roll_number"],
                            "fullname": document["fullname"],
                            "email": document["email_id"],
                            "phone": document["phone_number"]
                        }
                        st.json(detailsDict)
                    with col1:
                        
                        st.subheader("Front Photo",divider='green')
                        if "front_photo" in document:
                            st.image(document["front_photo"])
                        else:
                            st.info(f"{document['roll_number']} does'nt contain front photo.\nPlease Upload it first.")
                        st.subheader("Left Photo",divider='green')
                        if "left_photo" in document:
                            st.image(document["left_photo"])
                        else:
                            st.info(f"{document['roll_number']} does'nt contain left photo.\nPlease Upload it first.")
                        st.subheader("Right Photo",divider='green')
                        if "right_photo" in document:
                            st.image(document["right_photo"])
                        else:
                            st.info(f"{document['roll_number']} does'nt contain right photo.\nPlease Upload it first.")

                        
            else:
                st.warning("No documents are found\nUploadthe data first")
    #Methods That Performs CRUD Operations
    def addField(self, col1, col2, mode):
        try:
            self.fieldName = col2.text_input("Enter the field name")
            self.fieldValue = eval(col2.text_input("Enter the field value"))
            if self.fieldName and self.fieldValue:
                if col2.button("Confirm to add the above field and value", type="primary", use_container_width=True):
                    if mode == "Edits On specific Students":
                        result = self.studentsCollection.update_one(
                            {"batch": self.batch, "branch": self.branch, "semester": self.semester,"roll_number":self.rollNumbers},
                            {"$set": {self.fieldName: self.fieldValue}}
                        )
                        if result.matched_count:
                            col2.success("Field Added Successfully")
                            col2.subheader("Here is the brief info about the operation", divider='blue')
                            style_metric_cards()
                            col2.metric("Modified Documents Count", value=result.modified_count)
                            style_metric_cards()
                            col2.metric("Matched Documents Count", value=result.matched_count)
                        else:
                            col2.error("No matching documents found for the specific student.")

                    # For a group of students
                    if mode == "Edits on group of students":
                        result = self.studentsCollection.update_many(
                            {"batch": self.batch, "branch": self.branch, "semester": self.semester},
                            {"$set": {self.fieldName: self.fieldValue}}
                        )
                        if result.matched_count:
                            col2.success("Field Added Successfully")
                            col2.subheader("Here is the brief info about the operation", divider='blue')
                            style_metric_cards()
                            col2.metric("Modified Documents Count", value=result.modified_count)
                            style_metric_cards()
                            col2.metric("Matched Documents Count", value=result.matched_count)
                        else:
                            col2.error("No matching documents found for the group.")
        except Exception as e:
            col2.error(f"An error occurred: {e}")


    def removeField(self, col1, col2, mode):
        try:
            if mode == "Edits On specific Students":
                document = self.studentsCollection.find({"batch": self.batch, "branch": self.branch, "semester": self.semester, "roll_number": self.rollNumbers})
                if document:
                    document=document.to_list()
                    self.fieldName = col2.selectbox("select the columns", document[0].keys())
                    if col2.button(f"{self.fieldName} - Conffirm To Remove This",type="primary",use_container_width=True):
                        result = self.studentsCollection.update_one(
                            {"batch": self.batch, "branch": self.branch, "semester": self.semester,"roll_number":self.rollNumbers},
                            {"$unset": {self.fieldName: ""}}
                        )
                        if result.matched_count:
                            col2.success("Field Added Successfully")
                            col2.subheader("Here is the brief info about the operation", divider='blue')
                            style_metric_cards()
                            col2.metric("Modified Documents Count", value=result.modified_count)
                            style_metric_cards()
                            col2.metric("Matched Documents Count", value=result.matched_count)
                        else:
                            col2.error("No matching documents found for the specific student.")

                # For a group of students
            if mode == "Edits on group of students":
                document = self.studentsCollection.find({"batch": self.batch, "branch": self.branch, "semester": self.semester})
                if document:
                    document = document.to_list()
                    doc = [len(x.keys()) for x in document]
                    document=document[doc.index(max(doc))]
                    self.fieldName = col2.selectbox("select the columns", document.keys())
                    if col2.button(f"{self.fieldName} - Conffirm To Remove This",type="primary",use_container_width=True):
                        result = self.studentsCollection.update_many(
                            {"batch": self.batch, "branch": self.branch, "semester": self.semester},
                            {"$unset": {self.fieldName: ""}}
                        )
                        if result.matched_count:
                            col2.success("Field Added Successfully")
                            col2.subheader("Here is the brief info about the operation", divider='blue')
                            style_metric_cards()
                            col2.metric("Modified Documents Count", value=result.modified_count)
                            style_metric_cards()
                            col2.metric("Matched Documents Count", value=result.matched_count)
                        else:
                            col2.error("No matching documents found for the group.")
        except Exception as e:
            col2.error(f"An error occurred: {e}")
    def updateField(self, col1, col2, mode):
        try:
            self.fieldName = col2.text_input("Enter the field name to update")
            self.fieldValue = eval(col2.text_input("Enter the new value for the field"))
            if self.fieldName and self.fieldValue:
                if col2.button(f"Confirm to modify {self.fieldName} to {self.fieldValue}"):
                    if mode == "Edits On specific Students":
                        updated_count = self.studentsCollection.update_one(
                            {"batch": self.batch, "branch": self.branch, "semester": self.semester, "roll_number": self.rollNumbers},
                            {"$set": {self.fieldName: self.fieldValue}}
                        )
                        if updated_count.matched_count:
                            col2.success("Field Updated Successfully")
                            col2.subheader("Operation Summary", divider='blue')
                            style_metric_cards()
                            col2.metric("Modified documents count", value=updated_count.modified_count)
                    elif mode == "Edits on group of students":
                        updated_count = self.studentsCollection.update_many(
                            {"batch": self.batch, "branch": self.branch, "semester": self.semester},
                            {"$set": {self.fieldName: self.fieldValue}}
                        )
                        if updated_count.matched_count:
                            col2.success("Field Updated Successfully")
                            col2.subheader("Operation Summary", divider='blue')
                            style_metric_cards()
                            col2.metric("Modified documents count", value=updated_count.modified_count)
        except Exception as e:
            col2.error(f"An error occurred: {e}")
    def removeCurrentValue(self, col1, col2, mode):
        try:
            self.fieldName = col2.text_input("Enter the field name to remove the value from")
            if self.fieldName:
                if col2.button(f"Confirm to remove {self.fieldName} from the current value"):
                    if mode == "Edits On specific Students":
                        updated_count = self.studentsCollection.update_one(
                            {"batch": self.batch, "branch": self.branch, "semester": self.semester, "roll_number": self.rollNumbers},
                            {"$set": {self.fieldName: None}}
                        )
                        if updated_count.matched_count:
                            col2.success("Field Value Removed Successfully")
                            col2.subheader("Operation Summary", divider='blue')
                            style_metric_cards()
                            col2.metric("Modified documents count", value=updated_count.modified_count)
                    elif mode == "Edits on group of students":
                        updated_count = self.studentsCollection.update_many(
                            {"batch": self.batch, "branch": self.branch, "semester": self.semester},
                            {"$set": {self.fieldName: None}}
                        )
                        if updated_count.matched_count:
                            col2.success("Field Value Removed Successfully")
                            col2.subheader("Operation Summary", divider='blue')
                            style_metric_cards()
                            col2.metric("Modified documents count", value=updated_count.modified_count)
        except Exception as e:
            col2.error("An Error Occured {e}")
    def deleteStudent(self, col1, col2, mode):
        try:
            if mode == "Edits On specific Students":
                confirm_delete = col2.checkbox("Confirm Deletion of the Selected Student")
                if confirm_delete:
                    deleted_count = self.studentsCollection.delete_one(
                        {"batch": self.batch, "branch": self.branch, "semester": self.semester, "roll_number": self.rollNumbers}
                    )
                    if deleted_count.deleted_count:
                        col2.success("Student Deleted Successfully")
            elif mode == "Edits on group of students":
                confirm_delete = col2.checkbox("Confirm Deletion of the Selected Group of Students")
                if confirm_delete:
                    deleted_count = self.studentsCollection.delete_many(
                        {"batch": self.batch, "branch": self.branch, "semester": self.semester}
                    )
                    if deleted_count.deleted_count:
                        col2.success("Group of Students Deleted Successfully")
                        col2.metric("Deleted Documents Count", value=deleted_count.deleted_count)
        except Exception as e:
            col2.error("An Error Occured {e}")
    def uploadFingerPrint(self, col1, col2):
        # Select Batch, Branch, and Semester
        self.Batch = col1.selectbox("Select the Batch that you want to retrieve", self.studentsCollection.distinct("batch"))
        self.Branch = col1.selectbox("Select the Branch that you want to retrieve", self.studentsCollection.distinct("branch"))
        self.Semester = col1.selectbox("Select the Semester that you want to retrieve", self.studentsCollection.distinct("semester"))
        
        if self.Batch and self.Branch and self.Semester:
            # Retrieve roll numbers based on the selected Batch, Branch, and Semester
            roll_numbers = self.studentsCollection.find(
                {"branch": self.Branch, "batch": self.Batch, "semester": self.Semester},
                {"roll_number": 1}
            ).distinct("roll_number")
            
            self.selectedRollNumber = col1.selectbox("Please select the roll number", roll_numbers)
            
            if self.selectedRollNumber:
                # File uploader for the thumbprint image
                fileUploader = col2.file_uploader("Upload the thumbprint image", type=['png', 'jpeg', 'jpg'])
                
                if fileUploader:
                    image = Image.open(fileUploader)
                    
                    # Convert the image to black and white
                    bw_image = image.convert('L')
                    
                    # Display the black-and-white image
                    col2.image(bw_image)
                    
                    # Confirmation button to upload the fingerprint
                    if col2.button("Confirm to upload the fingerprint", use_container_width=True, type='primary'):
                        # Save the black-and-white image as binary
                        buffer = BytesIO()
                        bw_image.save(buffer, format="JPEG")
                        binary_data = Binary(buffer.getvalue())
                        
                        # Update the database with the black-and-white thumbprint
                        uploadedThumbPrint = self.studentsCollection.update_one(
                            {"roll_number": self.selectedRollNumber}, 
                            {"$set": {"thumbPhoto": binary_data}}
                        )
                        
                        # Provide feedback to the user
                        if uploadedThumbPrint.acknowledged:
                            col2.success("Thumb Print uploaded successfully")
    def uploadDataToInternet(self, col1, col2):
        self.batch = col2.selectbox("Select the batch that you want to retrieve", self.studentsCollection.distinct("batch"))
        self.branch = col2.selectbox("Select the branch that you want to retrieve", self.studentsCollection.distinct("branch"))
        self.semester = col2.selectbox("Select the semester that you want to retrieve", self.studentsCollection.distinct("semester"))
        if self.batch and self.branch and self.semester:
            options = col2.radio("Upload data to internet", ["Photos", "Thumb Prints"])
            retrievedDocs = self.studentsCollection.find(
                {"batch": self.batch, "branch": self.branch, "semester": self.semester},
                {"_id": 0, "roll_number": 1, "front_photo": 1, "left_photo": 1, "right_photo": 1,"left_thumb":1}
            )
            count = 0
            if col2.button("Confirm to upload, required internet connection",use_container_width=True,type='primary'):
                for currentDoc in retrievedDocs:
                    # Correcting the key name check
                    roll_number = currentDoc["roll_number"]
                    front_photo = currentDoc["front_photo"] if "front_photo" in currentDoc else None
                    left_photo = currentDoc["left_photo"] if "left_photo" in currentDoc else None
                    right_photo = currentDoc["right_photo"] if "right_photo" in currentDoc else None
                    left_thumb = currentDoc["left_thumb"] if "left_thumb" in currentDoc else None
                    if options == "Photos":
                        self.internetCollection.update_one(
                            {
                                "batch": self.batch,
                                "branch": self.branch,
                                "semester": self.semester,
                                "roll_number": roll_number
                            },
                            {
                                "$set": {
                                    "front_photo": front_photo if "front_photo" in currentDoc else None,
                                    "left_photo": left_photo if "left_photo" in currentDoc else None,
                                    "right_photo": right_photo if "right_photo" in currentDoc else None
                                }
                            },
                            upsert=True  # Ensures that a document is created if it doesn't exist
                        )
                        count=count+1
                    if options == "Thumb Prints":
                        self.internetCollection.update_one(
                            {
                                "batch": self.batch,
                                "branch": self.branch,
                                "semester": self.semester,
                                "roll_number": roll_number
                            },
                            {
                                "$set": {
                                    "left_thumb": left_thumb
                                }
                            },
                            upsert=True  # Ensures that a document is created if it doesn't exist
                        )
                        count = count + 1
                col2.success(f"Successfully Uploaded {count} documents")

    def uploadThumbPrint(self, col1, col2):
        self.batch = col2.selectbox("Select The batch that you want to retrieve", self.studentsCollection.distinct("batch"))
        self.branch = col2.selectbox("Select The branch that you want to retrieve", self.studentsCollection.distinct("branch"))
        self.semester = col2.selectbox("Select The semester that you want to retrieve", self.studentsCollection.distinct("semester"))
        self.roll_numbers = col2.selectbox("Select the roll number to upload the thumb print", self.studentsCollection.distinct("roll_number"))

        if self.batch and self.branch and self.semester and self.roll_numbers:
            leftThumbPrint = col2.file_uploader("Please Upload the left thumb Print Image", type=["jpeg", "jpg", "bmp", "BMP", "png"])

            if leftThumbPrint:
                col2.image(leftThumbPrint)

                if col2.button("Upload the thumb prints", use_container_width=True, type='primary'):
                    # Read the uploaded file as binary data
                    left_thumb_binary = Binary(leftThumbPrint.read())

                    # Update MongoDB with binary data
                    self.internetCollection.update_one(
                        {
                            "batch": self.batch,
                            "branch": self.branch,
                            "semester": self.semester,
                            "roll_number": self.roll_numbers
                        },
                        {
                            "$set": {"left_thumb": left_thumb_binary}
                        }
                    )
                    col2.success("Uploaded To Internet is successful")

                    self.studentsCollection.update_one(
                        {
                            "batch": self.batch,
                            "branch": self.branch,
                            "semester": self.semester,
                            "roll_number": self.roll_numbers
                        },
                        {
                            "$set": {"left_thumb": left_thumb_binary}
                        }
                    )
                    col2.success("Uploaded to local host")
