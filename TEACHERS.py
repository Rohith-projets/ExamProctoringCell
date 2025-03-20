import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from bson.binary import Binary
class Teachers:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.TeachersDB = self.client["TeachersDB"]
        self.teachersCollection = self.TeachersDB["TeachersCollection"]
    def __del__(self):
        self.client.close()

    def display(self):
        tab1, tab2, tab3 = st.tabs(["Register", "Edit", "Display"])

        # Tab 1: Registration
        with tab1:
            col1, col2 = st.columns([1, 2], border=True)
            with col1:
                selected_option = st.radio("Select the operation to perform", 
                                           ["Register Teachers", "Upload the Photos", "Take Photos and Upload"])
                if selected_option == "Register Teachers":
                    self.register(col1, col2)
                elif selected_option == "Upload the Photos":
                    self.uploadPhoto(col1, col2)
                elif selected_option == "Take Photos and Upload":
                    self.takePhotos(col1, col2)
                total_teachers = self.teachersCollection.count_documents({})
                style_metric_cards()
                col1.metric("Total Teachers", value=total_teachers)

        # Tab 2: Edit
        with tab2:
            st.header("Edit Teacher Details", divider='blue')
            col1, col2 = st.columns([1.5, 2], border=True)
            with col1:
                edit_mode = st.radio("Select Edit Mode", ["Edit Specific Teacher", "Edit Group of Teachers"])
                self.handleEdits(edit_mode, col1, col2)

        # Tab 3: Display Details
        with tab3:
            self.viewDetails()

    def handleEdits(self, edit_mode, col1, col2):
        # Retrieving department and designation
        department = col1.selectbox("Select the Department", self.teachersCollection.distinct("department"))
        designation = col1.selectbox("Select the Designation", self.teachersCollection.distinct("designation"))
        if department and designation:
            # Fetching documents based on department and designation
            documents = list(self.teachersCollection.find({"department": department, "designation": designation}))
            if documents:
                if edit_mode == "Edit Specific Teacher":
                    # Add a checkbox to view all documents
                    view_all = col2.checkbox("View All Teachers in this Department and Designation")
                    if view_all:
                        with col2.expander("All Teachers", expanded=True):
                            for doc in documents:
                                st.json(doc)

                    # Dropdown for employee IDs
                    employee_ids = [doc.get("empID") for doc in documents if "empID" in doc]
                    if not employee_ids:
                        st.warning("No empID found in the fetched documents.")
                        return
                    selected_employee_id = col1.selectbox("Select Employee ID to Edit", employee_ids)
                    if selected_employee_id:
                        selected_employee = next((doc for doc in documents if doc.get("empID") == selected_employee_id), None)
                        if selected_employee:
                            col2.subheader("Employee Details", divider='blue')
                            st.json(selected_employee)
                            edit_option = col2.radio("Select the type of edit", 
                                                    ["Add A Field", "Remove A Field", "Update A Field Value", 
                                                    "Clear Field Value", "Delete Teacher", "Edit Photo"])
                            self.executeEditOption(edit_option, col1, col2, selected_employee, is_group=False)
                if edit_mode == "Edit Group of Teachers":
                    view_all = col2.checkbox("View All Teachers in this Department and Designation")
                    if view_all:
                        with col2.expander("All Teachers", expanded=True):
                            for doc in documents:
                                st.json(doc)
                    edit_option = col2.radio("Select the type of edit", 
                                                    ["Add A Field", "Remove A Field", "Update A Field Value", 
                                                    "Clear Field Value", "Delete Teacher"])
                    self.executeEditOption(edit_option, col1, col2, {"department":department,"designation":designation}, is_group=True)

            else:
                st.warning("No teachers found for the selected department and designation.")
        else:
            st.warning("Please select both Department and Designation.")

    def executeEditOption(self, option, col1, col2, data, is_group):
        if option == "Add A Field":
            self.addField(col1, col2, data, is_group)
        elif option == "Remove A Field":
            self.removeField(col1, col2, data, is_group)
        elif option == "Update A Field Value":
            self.updateField(col1, col2, data, is_group)
        elif option == "Clear Field Value":
            self.clearFieldValue(col1, col2, data, is_group)
        elif option == "Delete Teacher" and not is_group:
            self.deleteTeacher(col1, col2, data)
        elif option == "Delete Teacher" and is_group:
            self.deleteGroup(col1, col2, data)
        elif option == "Edit Photo":
            self.editPhoto(col1, col2, data)

    def addField(self, col1, col2, data, is_group):
        field_name = col2.text_input("Enter the field name to add")
        field_value = col2.text_input("Enter the field value")

        if col2.button("Add Field", type="primary", use_container_width=True):
            if not field_name or not field_value:
                col2.error("Field name and value cannot be empty.")
                return

            update_query = {"$set": {field_name: field_value}}

            if is_group:
                result = self.teachersCollection.update_many({"department": data["department"], "designation": data["designation"]}, update_query)
            else:
                result = self.teachersCollection.update_one({"empID": data["empID"]}, update_query)

            if result.modified_count > 0:
                col2.success(f"Field '{field_name}' added successfully!")
                col2.metric("Modified Documents", value=result.modified_count, border=True)
            else:
                col2.warning("No matching documents found. No changes made.")

    def removeField(self, col1, col2, data, is_group):
        field_name = col2.text_input("Enter the field name to remove")

        if col2.button("Remove Field", type="primary", use_container_width=True):
            if not field_name:
                col2.error("Field name cannot be empty.")
                return

            update_query = {"$unset": {field_name: ""}}

            if is_group:
                result = self.teachersCollection.update_many({"department": data["department"], "designation": data["designation"]}, update_query)
            else:
                result = self.teachersCollection.update_one({"empID": data["empID"]}, update_query)

            if result.modified_count > 0:
                col2.success(f"Field '{field_name}' removed successfully!")
                col2.metric("Modified Documents", value=result.modified_count, border=True)
            else:
                col2.warning("No matching documents found. No changes made.")

    def updateField(self, col1, col2, data, is_group):
        field_name = col2.text_input("Enter the field name to update")
        new_value = col2.text_input("Enter the new value")

        if col2.button("Update Field", type="primary", use_container_width=True):
            if not field_name or not new_value:
                col2.error("Field name and value cannot be empty.")
                return

            update_query = {"$set": {field_name: new_value}}

            if is_group:
                result = self.teachersCollection.update_many({"department": data["department"], "designation": data["designation"]}, update_query)
            else:
                result = self.teachersCollection.update_one({"empID": data["empID"]}, update_query)

            if result.modified_count > 0:
                col2.success(f"Field '{field_name}' updated successfully!")
                col2.metric("Modified Documents", value=result.modified_count, border=True)
            else:
                col2.warning("No matching documents found. No changes made.")
    def clearFieldValue(self, col1, col2, data, is_group):
        field_name = col2.text_input("Enter the field name to update")
        if col2.button("Update Field", type="primary", use_container_width=True):
            if not field_name:
                col2.error("Field name and value cannot be empty.")
                return

            update_query = {"$set": {field_name: None}}

            if is_group:
                result = self.teachersCollection.update_many({"department": data["department"], "designation": data["designation"]}, update_query)
            else:
                result = self.teachersCollection.update_one({"empID": data["empID"]}, update_query)

            if result.modified_count > 0:
                col2.success(f"Field '{field_name}' updated successfully!")
                col2.metric("Modified Documents", value=result.modified_count, border=True)
            else:
                col2.warning("No matching documents found. No changes made.")


    def deleteTeacher(self, col1, col2, data):
        # Display confirmation checkbox
        confirm = col2.checkbox("Are you sure you want to delete this teacher?", key="confirm_teacher_deletion")
        if confirm and col2.button(f"Delete Teacher: {data.get('empID')}", type="primary", use_container_width=True):
            result = self.teachersCollection.delete_one({"empID": data["empID"]})
            if result.deleted_count > 0:
                col2.success("Teacher deleted successfully!")
                col2.metric("Deleted Documents", value=result.deleted_count)
            else:
                col2.warning("No matching teacher found. Deletion failed.")

    def deleteGroup(self, col1, col2, data):
        department = data.get("department")
        designation = data.get("designation")

        # Display confirmation checkbox
        confirm = col2.checkbox(f"Are you sure you want to delete all teachers in {department} - {designation}?", key="confirm_group_deletion")
        if confirm and col2.button("Delete Group", type="primary", use_container_width=True):
            result = self.teachersCollection.delete_many({"department": department, "designation": designation})
            if result.deleted_count > 0:
                col2.success(f"Group deleted successfully! ({result.deleted_count} documents removed)")
                col2.metric("Deleted Documents", value=result.deleted_count)
            else:
                col2.warning("No matching group found. Deletion failed.")

    def editPhoto(self, col1, col2, data):
        photo_type = col2.selectbox("Select the type of photo to upload", ["Front Photo", "Left Photo", "Right Photo"])
        uploaded_photo = col2.camera_input("Take a Photo")

        if uploaded_photo and col2.button("Upload Photo", type="primary", use_container_width=True):
            try:
                binary_photo = Binary(uploaded_photo.read())  # Convert to binary

                update_field = {
                    "Front Photo": "front_photo",
                    "Left Photo": "left_photo",
                    "Right Photo": "right_photo"
                }[photo_type]

                result = self.teachersCollection.update_one({"empID": data["empID"]}, {"$set": {update_field: binary_photo}})

                if result.modified_count > 0:
                    col2.success(f"{photo_type} uploaded successfully!")
                else:
                    col2.warning("No matching record found. Photo upload failed.")

            except Exception as e:
                col2.error(f"Error uploading photo: {str(e)}")

    def viewDetails(self):
        st.header("View The Details Of A Teacher", divider='green')
        departments = list(self.teachersCollection.distinct("department"))
        designations = list(self.teachersCollection.distinct("designation"))

        col1, col2 = st.columns([1, 2], border=True)

        # Dropdowns in col2 to select Department and Designation
        self.department = col2.selectbox("Select Department", departments)
        self.designation = col2.selectbox("Select Designation", designations)

        # Dropdown to select empID
        if self.department and self.designation:
            empIDs = list(self.teachersCollection.find({"department": self.department, "designation": self.designation}, {"empID": 1}).distinct("empID"))
            if len(empIDs):
                self.empID = col2.selectbox("Select empID to see details", empIDs)
                if self.empID:
                    document = self.teachersCollection.find_one({"empID": self.empID})
                    if document:
                        with col2:
                            st.subheader("Teacher Details", divider='blue')
                            detailsDict = {
                                "empID": document["empID"],
                                "fullname": document['fullname'],
                                "department": document["department"],
                                "designation": document["designation"],
                                "email": document["email"],
                                "phone": document["phone"]
                            }
                            st.json(detailsDict)
                        with col1:
                            st.subheader("Front Photo", divider='green')
                            if "front_photo" in document:
                                st.image(document["front_photo"])
                            else:
                                st.info(f"{document['empID']} doesn't contain front photo.\nPlease upload it first.")
                            st.subheader("Left Photo", divider='green')
                            if "left_photo" in document:
                                st.image(document["left_photo"])
                            else:
                                st.info(f"{document['empID']} doesn't contain left photo.\nPlease upload it first.")
                            st.subheader("Right Photo", divider='green')
                            if "right_photo" in document:
                                st.image(document["right_photo"])
                            else:
                                st.info(f"{document['empID']} doesn't contain right photo.\nPlease upload it first.")
            else:
                st.warning("No documents found for the selected department and designation.")

    def register(self, col1, col2):
        with col2:
            file_uploader = st.file_uploader("Upload the CSV file", type=["csv"])
            if file_uploader:
                try:
                    # Read the uploaded CSV file
                    df = pd.read_csv(file_uploader)
                    if not df.empty:
                        # Insert data into MongoDB
                        inserted_ids = self.teachersCollection.insert_many(df.to_dict(orient="records"))
                        total_documents = len(inserted_ids.inserted_ids)
                        
                        # Display success message with metric cards
                        if total_documents:
                            st.success(f"{total_documents} teachers registered successfully!")
                            with st.container():
                                style_metric_cards()
                                st.metric(label="Total Teachers Registered", value=total_documents)
                    else:
                        st.error("The uploaded CSV file is empty.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    def uploadPhoto(self, col1, col2):
        departments = list(self.teachersCollection.distinct("department"))
        designations = list(self.teachersCollection.distinct("designation"))
        self.department = col2.selectbox("Select department", departments)
        self.designation = col2.selectbox("Select designation", designations)

        # Dropdown to select empID
        if self.department and self.designation:
            empIDs = list(self.teachersCollection.find({"department": self.department, "designation": self.designation}, {"empID": 1}).distinct("empID"))
            if len(empIDs):
                self.empID = col2.selectbox("Select empID", empIDs)
                if self.empID:
                    select_type = col2.selectbox(
                        "Select the type of photo to upload:",
                        ["Front Photo", "Left Photo", "Right Photo"]
                    )

                    # File uploader for photo
                    uploaded_photo = col2.file_uploader(f"Upload the {select_type.lower()} (JPG, JPEG, PNG):", type=["jpg", "jpeg", "png"])
                    
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
                                edited = self.teachersCollection.update_one(
                                    {
                                        "designation": self.designation,
                                        "department": self.department,
                                        "empID": self.empID
                                    },
                                    {"$set": {update_field: photo_binary}}
                                )
                                
                                if edited.acknowledged:
                                    col2.success(f"{select_type} uploaded successfully!")
                                else:
                                    col2.error("Failed to upload photo. Please try again.")
                            except Exception as e:
                                col2.error(f"An error occurred: {e}")
                    else:
                        col2.info("Please upload a photo before confirming.")
                else:
                    col2.warning(f"No empIDs found for Batch: {self.batch}, Branch: {self.branch}, Semester: {self.semester}.")

    def takePhotos(self, col1, col2):
        departments = list(self.teachersCollection.distinct("department"))
        designations = list(self.teachersCollection.distinct("designation"))
        self.department = col2.selectbox("Select Departments", departments)
        self.designation = col2.selectbox("Select Designations", designations)

        # Dropdown to select empID
        if self.department and self.designation:
            empIDs = list(self.teachersCollection.find({"department": self.department, "designation": self.designation}, {"empID": 1}).distinct("empID"))
            if len(empIDs):
                self.empID = col2.selectbox("Select employee ID", empIDs)
                if self.empID:
                    select_type = col2.selectbox(
                        "Select the type of photo to upload:",
                        ["Front Photo", "Left Photo", "Right Photo"]
                    )
                    
                    photo = col2.camera_input(f"Upload the {select_type.lower()}")
                    if photo:
                        st.image(photo, use_container_width=True)
                        
                        if st.button(f"confirm to upload photo as {select_type.lower()}", use_container_width=True, type="primary"):
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
                            edited = self.teachersCollection.update_one(
                                {
                                    "department": self.department,
                                    "designation": self.designation,
                                    "empID": self.empID
                                },
                                {"$set": {update_field: binary_photo}}
                            )
                            
                            if edited.acknowledged:
                                col2.success("Photo uploaded successfully")
                                col2.image(photo)
                            else:
                                col2.error("Operation failed")
