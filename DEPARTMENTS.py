import streamlit as st
import pandas as pd
from streamlit_extras.metric_cards import *
from bson.binary import Binary
from pymongo import MongoClient

class Departments:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.DepartmentsDB = self.client["DepartmentsDB"]
        self.DepartmentsCollection = self.DepartmentsDB["Departments"]
        self.roomsDB = self.client["RoomsDB"]
        self.roomsCollection=self.roomsDB["RoomsCollection"]
    def __del__(self):
        self.client.close()
    def display(self):
        tab1, tab2, tab3 = st.tabs(["Register Departments", "Edit Departments", "Display Departments"])
        with tab1:
            data = self.DepartmentsCollection.count_documents({})
            col1, col2 = st.columns([1, 2], border=True)
            with col1:
                style_metric_cards()
                st.metric(label="Number of Departments", value=data)
                st.divider()
                options = st.radio("select the mode of registration", ["Csv File", "Manual Entry"])
                if options == "Csv File":
                    self.register_csv(col1, col2)
                if options == "Manual Entry":
                    self.register_manual_entry(col1, col2)
        with tab2:
            col1, col2 = st.columns([1, 2], border=True)
            self.edit(col1, col2)
        with tab3:
            col1, col2 = st.columns([1, 2], border=True)
            self.display_departments(col1, col2)
        tab4, tab5, tab6 = st.tabs(["Register Rooms", "Edit Rooms", "Display Rooms"])
        with tab4:
            col1, col2 = st.columns([1, 2], border=True)
            self.register_rooms(col1, col2)
        with tab5:
            col1, col2 = st.columns([1, 2], border=True)
            self.editRooms(col1, col2)
        with tab6:
            col1, col2 = st.columns([1, 2], border=True)
            self.displayRooms(col1,col2)
    def register_csv(self,col1,col2):
        file_uploader = col2.file_uploader("Upload Any CSV File")
        if file_uploader is not None:
            dataframe = pd.read_csv(file_uploader)
            col2.subheader("Your data looks like this\nVerify is it correct or not", divider='blue')
            list_ = self.parsed_csv(col1, col2, dataframe)
            with col2.expander("Your data in db looks like"):
                for i in list_:
                    st.json(i)
            if col2.button("My Data is correct.\nContinue with the regestring data.",use_container_width=True,type='primary',icon='➡️'):
                self.DepartmentsCollection.insert_many(list_)
                col2.success("Data inserted successfully")
                style_metric_cards()
                col2.metric("Number of documents Inserted", value=dataframe.shape[0])
            

    def register_manual_entry(self, col1, col2):
        if "childDict" not in st.session_state:
            st.session_state.childDict = {}
        st.divider()
        col1.subheader("Your Data Look Like This In DB", divider='blue')
        with col1:
            st.json(st.session_state.childDict)
        col2.subheader("Enter Primary Details Here", divider='blue')
        batch = col2.text_input("Enter batch year")
        branch = col2.text_input("Enter department here")
        branch_code = col2.text_input("Enter branch code")
        hod_name = col2.text_input("Enter hod name")
        number_of_faculties = col2.number_input("Enter number of faculties")
        regulation = col2.text_input("Enter regulation here")
        if col2.button("Fix the above details", use_container_width=True, type="primary"):
            col1.subheader("Your Data Looks Like This In DB")
            st.session_state.childDict = {
                "batch": batch,
                "branch": branch,
                "branch_code": branch_code,
                "hod_name": hod_name,
                "number_of_faculties": number_of_faculties,
                "regulation": regulation
            }
        col2.subheader("Enter Semister 1 Details", divider='blue')
        semister_1_subjects = col2.text_input("1 : Enter comma separeted subjects.Example : subject1,subject2")
        semister_1_subjects_codes = col2.text_input("1 : Enter the comma separated sunject codes")
        semister_1_subjects_credits = col2.text_input("1: Enter the comma separated subject credits.\nExample:20CAI105,20CAI205")
        semister_1_total_credits = col2.text_input("1 : Enter the total credits for semister 1")
        semister_1_subjects_types = col2.text_input("1 : Enter all the subjects types comma seperated.Example : theory,practical")
        if col2.button("Semister 1 : Fix the above details", use_container_width=True, type="primary"):
            semester1 = {
                "semister_1_subjects": semister_1_subjects.split(','),
                "semister_1_subjects_codes": semister_1_subjects_codes.split(','),
                "semister_1_subjects_credits": semister_1_subjects_credits.split(','),
                "semister_1_total_credits": semister_1_total_credits.split(','),
                "semister_1_subjects_types": semister_1_subjects_types.split(',')
            }
            st.session_state.childDict["semister 1"] = semester1
        col2.subheader("Enter Semister 2 Details", divider='blue')
        semister_2_subjects = col2.text_input("Enter comma separeted subjects for semester 2.Example : subject1,subject2")
        semister_2_subjects_codes = col2.text_input("Enter the comma separated sunject codes for semster 2")
        semister_2_subjects_credits = col2.text_input("Enter the comma separated subject credits for semster 2.\nExample:20CAI105,20CAI205")
        semister_2_total_credits = col2.text_input("Enter the total credits for semister 2")
        semister_2_subjects_types = col2.text_input("Enter all the subjects types comma seperated for semster 2.Example : theory,practical")
        if col2.button("fix the above details", use_container_width=True, type="primary"):
            semester2 = {
                "semister_2_subjects": semister_2_subjects.split(','),
                "semister_2_subjects_codes": semister_2_subjects_codes.split(','),
                "semister_2_subjects_credits": semister_2_subjects_credits.split(','),
                "semister_2_total_credits": semister_2_total_credits.split(','),
                "semister_2_subjects_types": semister_2_subjects_types.split(',')
            }
            st.session_state.childDict["semister 2"] = semester2
        col2.subheader("Enter Semister 3 Details", divider='blue')
        semister_3_subjects = col2.text_input("Semster 3 : Enter comma separeted subjects.Example : subject1,subject2")
        semister_3_subjects_codes = col2.text_input("Semster 3 : Enter the comma separated sunject codes")
        semister_3_subjects_credits = col2.text_input("Semster 3 : Enter the comma separated subject credits.\nExample:20CAI105,20CAI205")
        semister_3_total_credits = col2.text_input("Semster 3 : Enter the total credits for semister 1")
        semister_3_subjects_types = col2.text_input("Semster 3 : Enter all the subjects types comma seperated.Example : theory,practical")
        if col2.button("Semster 3 : Fix the above details", use_container_width=True, type="primary"):
            semester3 = {
                "semister_3_subjects": semister_3_subjects.split(','),
                "semister_3_subjects_codes": semister_3_subjects_codes.split(','),
                "semister_3_subjects_credits": semister_3_subjects_credits.split(','),
                "semister_3_total_credits": semister_3_total_credits.split(','),
                "semister_3_subjects_types": semister_3_subjects_types.split(',')
            }
            st.session_state.childDict["semister 3"] = semester3
        col2.subheader("Enter Semister 4 Details", divider='blue')
        semister_4_subjects = col2.text_input("Semster 4 : Enter comma separeted subjects.Example : subject1,subject2")
        semister_4_subjects_codes = col2.text_input("Semster 4 : Enter the comma separated sunject codes")
        semister_4_subjects_credits = col2.text_input("Semster 4 : Enter the comma separated subject credits.\nExample:20CAI105,20CAI205")
        semister_4_total_credits = col2.text_input("Semster 4 : Enter the total credits for semister 1")
        semister_4_subjects_types = col2.text_input("Semster 4 : Enter all the subjects types comma seperated.Example : theory,practical")
        if col2.button("Semster 4 : Fix the above details", use_container_width=True, type="primary"):
            semester4 = {
                "semister_4_subjects": semister_4_subjects.split(','),
                "semister_4_subjects_codes": semister_4_subjects_codes.split(','),
                "semister_4_subjects_credits": semister_4_subjects_credits.split(','),
                "semister_4_total_credits": semister_4_total_credits.split(','),
                "semister_4_subjects_types": semister_4_subjects_types.split(',')
            }
            st.session_state.childDict["semister 4"] = semester4
        col2.subheader("Enter Semister 5 Details", divider='blue')
        semister_5_subjects = col2.text_input("Semster 5 : Enter comma separeted subjects.Example : subject1,subject2")
        semister_5_subjects_codes = col2.text_input("Semster 5 : Enter the comma separated sunject codes")
        semister_5_subjects_credits = col2.text_input("Semster 5 : Enter the comma separated subject credits.\nExample:20CAI105,20CAI205")
        semister_5_total_credits = col2.text_input("Semster 5 : Enter the total credits for semister 1")
        semister_5_subjects_types = col2.text_input("Semster 5 : Enter all the subjects types comma seperated.Example : theory,practical")
        if col2.button("Semster 5 : Fix the above details", use_container_width=True, type="primary"):
            semester5 = {
                "semister_5_subjects": semister_5_subjects.split(','),
                "semister_5_subjects_codes": semister_5_subjects_codes.split(','),
                "semister_5_subjects_credits": semister_5_subjects_credits.split(','),
                "semister_5_total_credits": semister_5_total_credits.split(','),
                "semister_5_subjects_types": semister_5_subjects_types.split(',')
            }
            st.session_state.childDict["semister 5"] = semester5
        col2.subheader("Enter Semister 6 Details", divider='blue')
        semister_6_subjects = col2.text_input("Semster 6 : Enter comma separeted subjects.Example : subject1,subject2")
        semister_6_subjects_codes = col2.text_input("Semster 6 : Enter the comma separated sunject codes")
        semister_6_subjects_credits = col2.text_input("Semster 6 : Enter the comma separated subject credits.\nExample:20CAI105,20CAI205")
        semister_6_total_credits = col2.text_input("Semster 6 : Enter the total credits for semister 1")
        semister_6_subjects_types = col2.text_input("Semster 6 : Enter all the subjects types comma seperated.Example : theory,practical")
        if col2.button("Semster 6 : Fix the above details", use_container_width=True, type="primary"):
            semester6 = {
                "semister_6_subjects": semister_6_subjects.split(','),
                "semister_6_subjects_codes": semister_6_subjects_codes.split(','),
                "semister_6_subjects_credits": semister_6_subjects_credits.split(','),
                "semister_6_total_credits": semister_6_total_credits.split(','),
                "semister_6_subjects_types": semister_6_subjects_types.split(',')
            }
            st.session_state.childDict["semister 6"] = semester6
        col2.subheader("Enter Semister 7 Details", divider='blue')
        semister_7_subjects = col2.text_input("Semster 7 : Enter comma separeted subjects.Example : subject1,subject2")
        semister_7_subjects_codes = col2.text_input("Semster 7 : Enter the comma separated sunject codes")
        semister_7_subjects_credits = col2.text_input("Semster 7 : Enter the comma separated subject credits.\nExample:20CAI105,20CAI205")
        semister_7_total_credits = col2.text_input("Semster 7 : Enter the total credits for semister 1")
        semister_7_subjects_types = col2.text_input("Semster 7 : Enter all the subjects types comma seperated.Example : theory,practical")
        if col2.button("Semster 7 : Fix the above details", use_container_width=True, type="primary"):
            semester7 = {
                "semister_7_subjects": semister_7_subjects.split(','),
                "semister_7_subjects_codes": semister_7_subjects_codes.split(','),
                "semister_7_subjects_credits": semister_7_subjects_credits.split(','),
                "semister_7_total_credits": semister_7_total_credits.split(','),
                "semister_7_subjects_types": semister_7_subjects_types.split(',')
            }
            st.session_state.childDict["semister 7"] = semester7
        col2.subheader("Enter Semister 8 Details", divider='blue')
        semister_8_subjects = col2.text_input("Semster 8 : Enter comma separeted subjects.Example : subject1,subject2")
        semister_8_subjects_codes = col2.text_input("Semster 8 : Enter the comma separated sunject codes")
        semister_8_subjects_credits = col2.text_input("Semster 8 : Enter the comma separated subject credits.\nExample:20CAI105,20CAI205")
        semister_8_total_credits = col2.text_input("Semster 8 : Enter the total credits for semister 1")
        semister_8_subjects_types = col2.text_input("Semster 8 : Enter all the subjects types comma seperated.Example : theory,practical")
        if col2.button("Semster 8 : Fix the above details", use_container_width=True, type="primary"):
            semester8 = {
                "semister_8_subjects": semister_8_subjects.split(','),
                "semister_8_subjects_codes": semister_8_subjects_codes.split(','),
                "semister_8_subjects_credits": semister_8_subjects_credits.split(','),
                "semister_8_total_credits": semister_8_total_credits.split(','),
                "semister_8_subjects_types": semister_8_subjects_types.split(',')
            }
            st.session_state.childDict["semister 8"] = semester8
        
        if col2.button("I Entered all the data.\nUpload to database", type="primary", use_container_width=True):
            inserted_data = self.DepartmentsCollection.insert_one(st.session_state.childDict)
            if inserted_data.acknowledged:
                col2.success("You data is uploaded in db")
                col2.subheader("Data Uploaded", divider='blue')
                col2.json(st.session_state.childDict)

    def edit(self, col1, col2):
        selectOptions = col1.radio("Select the option to edit", [
            "Add Department Photo", 
            "Edit departments primary details", 
            "semister 1", "semister 2", "semister 3", "semister 4",
            "semister 5", "semister 6", "semister 7", "semister 8","Delete Department"
        ])

        batch = col2.selectbox("Select the Batch", self.DepartmentsCollection.distinct("batch"))
        branch = col2.selectbox("Select the Branch", self.DepartmentsCollection.distinct("branch"))
        regulation = col2.selectbox("Select the Regulation", self.DepartmentsCollection.distinct("regulation"))

        if batch and branch and regulation:
            document = self.DepartmentsCollection.find_one({"batch": batch, "branch": branch, "regulation": regulation})
            
            if not document:
                col2.warning("No Departments found. Upload the data first.")
                return
            
            col1.json(document)  # Display current document

            if selectOptions == "Add Department Photo":
                col2.subheader("Add Department Photo", divider='blue')
                photo = col2.file_uploader("Upload the photo", type=["jpg", "png"])
                
                if photo and col2.button("Upload Photo", type="primary", use_container_width=True):
                    result = self.DepartmentsCollection.update_one(
                        {"batch": batch, "branch": branch, "regulation": regulation}, 
                        {"$set": {"department_photo": Binary(photo.getvalue())}}
                    )
                    if result.modified_count:
                        col2.success("Photo uploaded successfully!")

            elif selectOptions == "Edit departments primary details":
                batch_new = col2.text_input("Write the new batch", value=batch)
                if col2.button("Update batch", type="primary", use_container_width=True):
                    result = self.DepartmentsCollection.update_one(
                        {"branch": branch, "regulation": regulation}, {"$set": {"batch": batch_new}}
                    )
                    if result.modified_count:
                        col2.success("Batch updated")

                branch_new = col2.text_input("Write the new branch", value=branch)
                if col2.button("Update branch", type="primary", use_container_width=True):
                    result = self.DepartmentsCollection.update_one(
                        {"batch": batch, "regulation": regulation}, {"$set": {"branch": branch_new}}
                    )
                    if result.modified_count:
                        col2.success("Branch updated")

                regulation_new = col2.text_input("Write the new regulation", value=regulation)
                if col2.button("Update regulation", type="primary", use_container_width=True):
                    result = self.DepartmentsCollection.update_one(
                        {"batch": batch, "branch": branch}, {"$set": {"regulation": regulation_new}}
                    )
                    if result.modified_count:
                        col2.success("Regulation updated")

                hod_name = col2.text_input("Modify the HOD name", value=document.get("hod_name", ""))
                if col2.button("Update HOD Name", type="primary", use_container_width=True):
                    result = self.DepartmentsCollection.update_one(
                        {"batch": batch, "branch": branch, "regulation": regulation}, 
                        {"$set": {"hod_name": hod_name}}
                    )
                    if result.modified_count:
                        col2.success("HOD Name updated")

                number_of_faculties = col2.number_input("Modify Number of faculties", value=document.get("number_of_faculties", 0))
                if col2.button("Update Number of Faculties", type="primary", use_container_width=True):
                    result = self.DepartmentsCollection.update_one(
                        {"batch": batch, "branch": branch, "regulation": regulation}, 
                        {"$set": {"number_of_faculties": number_of_faculties}}
                    )
                    if result.modified_count:
                        col2.success("Number of Faculties updated")
            elif selectOptions=="Delete Department":
                if col2.button("Delete Department", type="primary", use_container_width=True):
                    result = self.DepartmentsCollection.delete_one({"batch": batch, "branch": branch,"regulation":regulation})
                    if result.deleted_count:
                        col2.success("Department deleted successfully")
            else:
                sem_key = f"semister {selectOptions[-1]}"
                new_sem_key="_".join(sem_key.split(" "))
                if sem_key in document:
                    update_option = col2.selectbox("Select option", ["Update Details", "Delete", "Add"])
                    
                    if update_option == "Update Details":
                        select_areas = col2.selectbox("On Which Areas Do You Want To Update Fields", [
                            f"{new_sem_key}_subjects", f"{new_sem_key}_subjects_credits",
                            f"{new_sem_key}_subjects_codes", f"{new_sem_key}_total_credits",
                            f"{new_sem_key}_subjects_types"
                        ])
                        
                        if select_areas:
                            retrieved_docs = document[sem_key].get(select_areas, [])
                            old_values = col2.multiselect(f"Select {select_areas} to modify", retrieved_docs)
                            new_values = col2.text_input("Give comma separated values").split(',')
                            
                            if old_values and new_values:
                                if col2.button("Confirm To Update", type='primary'):
                                    updated_list = retrieved_docs[:]  # Make a copy to avoid modifying the original list
                                    
                                    for old_val, new_val in zip(old_values, new_values):
                                        if old_val in updated_list:  # Ensure old value exists before replacing
                                            index = updated_list.index(old_val)
                                            updated_list[index] = new_val  # Replace only at the correct index

                                    result = self.DepartmentsCollection.update_one(
                                        {"batch": batch, "branch": branch, "regulation": regulation},
                                        {"$set": {f"{sem_key}.{select_areas}": updated_list}}
                                    )
                                    
                                    if result.modified_count:
                                        col2.success(f"{select_areas} updated successfully!")


                    elif update_option == "Delete":
                        select_areas = col2.selectbox("Select field to delete", [
                            f"{new_sem_key}_subjects", f"{new_sem_key}_subjects_credits",
                            f"{new_sem_key}_subjects_codes", f"{new_sem_key}_total_credits",
                            f"{new_sem_key}_subjects_types"
                        ])
                        
                        if select_areas:
                            retrieved_docs = document[sem_key].get(select_areas, [])
                            to_delete = col2.multiselect("Select items to delete", retrieved_docs)
                            
                            if to_delete and col2.button("Delete Selected", type="primary", use_container_width=True):
                                updated_list = [val for val in retrieved_docs if val not in to_delete]
                                result = self.DepartmentsCollection.update_one(
                                    {"batch": batch, "branch": branch, "regulation": regulation},
                                    {"$set": {f"{sem_key}.{select_areas}": updated_list}}
                                )
                                if result.modified_count:
                                    col2.success(f"Selected {select_areas} deleted successfully!")

                    elif update_option == "Add":
                        select_areas = col2.selectbox("Select field to add", [
                            f"{new_sem_key}_subjects", f"{new_sem_key}_subjects_credits",
                            f"{new_sem_key}_subjects_codes", f"{new_sem_key}_total_credits",
                            f"{new_sem_key}_subjects_types"
                        ])
                        
                        new_values = col2.text_input("Enter comma-separated values").split(',')
                        
                        if new_values and col2.button("Add Values", type="primary", use_container_width=True):
                            updated_list = document[sem_key].get(select_areas, []) + new_values
                            result = self.DepartmentsCollection.update_one(
                                {"batch": batch, "branch": branch, "regulation": regulation},
                                {"$set": {f"{sem_key}.{select_areas}": updated_list}}
                            )
                            if result.modified_count:
                                col2.success(f"New values added to {select_areas}!")
    def display_departments(self, col1, col2):
        col2.subheader("Fill the details", divider='blue')
        batch = col2.selectbox("Select the batch", self.DepartmentsCollection.distinct("batch"))
        branch = col2.selectbox("select the branch", self.DepartmentsCollection.distinct("branch"))
        regulation = col2.selectbox("Select the regulation", self.DepartmentsCollection.distinct("regulation"))
        if batch and branch and regulation:
            document = self.DepartmentsCollection.find_one({"batch": batch, "branch": branch, "regulation": regulation},{"_id":0,"branch":0,"batch":0,"regulation":0,"hod_name":0,"number_of_faculties":0,"branch_code":0})
            if not document:
                col2.warning("No Departments are found.\nUpoad the data first")
            col2.dataframe(document)
            if document:
                with col1:
                    col1.subheader("Department Logo",divider='blue')
                    if "department_photo" in document:
                        st.image(document["department_photo"])
                    else:
                        st.warning("Photo not yet uploaded.\nUpload Photo")
    def parsed_csv(self, col1, col2, dataframe):
        # General lists
        batch, branch, branch_codes, hod_names, number_of_faculties, regulations = [], [], [], [], [], []

        # Semester-specific lists
        semister_1_subjects, semister_1_subjects_codes, semister_1_subjects_credits, semister_1_total_credits, semister_1_subjects_types = [], [], [], [], []
        semister_2_subjects, semister_2_subjects_codes, semister_2_subjects_credits, semister_2_total_credits, semister_2_subjects_types = [], [], [], [], []
        semister_3_subjects, semister_3_subjects_codes, semister_3_subjects_credits, semister_3_total_credits, semister_3_subjects_types = [], [], [], [], []
        semister_4_subjects, semister_4_subjects_codes, semister_4_subjects_credits, semister_4_total_credits, semister_4_subjects_types = [], [], [], [], []
        semister_5_subjects, semister_5_subjects_codes, semister_5_subjects_credits, semister_5_total_credits, semister_5_subjects_types = [], [], [], [], []
        semister_6_subjects, semister_6_subjects_codes, semister_6_subjects_credits, semister_6_total_credits, semister_6_subjects_types = [], [], [], [], []
        semister_7_subjects, semister_7_subjects_codes, semister_7_subjects_credits, semister_7_total_credits, semister_7_subjects_types = [], [], [], [], []
        semister_8_subjects, semister_8_subjects_codes, semister_8_subjects_credits, semister_8_total_credits, semister_8_subjects_types = [], [], [], [], []

        # Dictionary to store the parsed data
        parentDict = {}

        for i in range(dataframe.shape[0]):
            # General information
            batch.append(dataframe.iat[i, 0])
            branch.append(dataframe.iat[i, 1])
            branch_codes.append(dataframe.iat[i, 2])
            hod_names.append(dataframe.iat[i, 3])
            number_of_faculties.append(dataframe.iat[i, 4])
            regulations.append(dataframe.iat[i, 5])

            # Semester-wise parsing
            semister_1_subjects.append(dataframe.iat[i, 6].split(','))
            semister_1_subjects_codes.append(dataframe.iat[i, 7].split(','))
            semister_1_subjects_credits.append(dataframe.iat[i, 8].split(','))
            semister_1_total_credits.append(dataframe.iat[i, 9])
            semister_1_subjects_types.append(dataframe.iat[i, 10].split(','))

            semister_2_subjects.append(dataframe.iat[i, 11].split(','))
            semister_2_subjects_codes.append(dataframe.iat[i, 12].split(','))
            semister_2_subjects_credits.append(dataframe.iat[i, 13].split(','))
            semister_2_total_credits.append(dataframe.iat[i, 14])
            semister_2_subjects_types.append(dataframe.iat[i, 15].split(','))

            semister_3_subjects.append(dataframe.iat[i, 16].split(','))
            semister_3_subjects_codes.append(dataframe.iat[i, 17].split(','))
            semister_3_subjects_credits.append(dataframe.iat[i, 18].split(','))
            semister_3_total_credits.append(dataframe.iat[i, 19])
            semister_3_subjects_types.append(dataframe.iat[i, 20].split(','))

            semister_4_subjects.append(dataframe.iat[i, 21].split(','))
            semister_4_subjects_codes.append(dataframe.iat[i, 22].split(','))
            semister_4_subjects_credits.append(dataframe.iat[i, 23].split(','))
            semister_4_total_credits.append(dataframe.iat[i, 24])
            semister_4_subjects_types.append(dataframe.iat[i, 25].split(','))

            semister_5_subjects.append(dataframe.iat[i, 26].split(','))
            semister_5_subjects_codes.append(dataframe.iat[i, 27].split(','))
            semister_5_subjects_credits.append(dataframe.iat[i, 28].split(','))
            semister_5_total_credits.append(dataframe.iat[i, 29])
            semister_5_subjects_types.append(dataframe.iat[i, 30].split(','))

            semister_6_subjects.append(dataframe.iat[i, 31].split(','))
            semister_6_subjects_codes.append(dataframe.iat[i, 32].split(','))
            semister_6_subjects_credits.append(dataframe.iat[i, 33].split(','))
            semister_6_total_credits.append(dataframe.iat[i, 34])
            semister_6_subjects_types.append(dataframe.iat[i, 35].split(','))

            semister_7_subjects.append(dataframe.iat[i, 36].split(','))
            semister_7_subjects_codes.append(dataframe.iat[i, 37].split(','))
            semister_7_subjects_credits.append(dataframe.iat[i, 38].split(','))
            semister_7_total_credits.append(dataframe.iat[i, 39])
            semister_7_subjects_types.append(dataframe.iat[i, 40].split(','))

            semister_8_subjects.append(dataframe.iat[i, 41].split(','))
            semister_8_subjects_codes.append(dataframe.iat[i, 42].split(','))
            semister_8_subjects_credits.append(dataframe.iat[i, 43].split(','))
            semister_8_total_credits.append(dataframe.iat[i, 44])
            semister_8_subjects_types.append(dataframe.iat[i, 45].split(','))

            # Constructing the child dictionary
            childDict = {
                "branch": branch[i],
                "batch": batch[i],
                "branch_code": branch_codes[i],
                "hod_name": hod_names[i],
                "number_of_faculties": number_of_faculties[i],
                "regulation": regulations[i],
                "semister1": {
                    "subjects": semister_1_subjects[i],
                    "subject_codes": semister_1_subjects_codes[i],
                    "subject_credits": semister_1_subjects_credits[i],
                    "total_credits": semister_1_total_credits[i],
                    "subject types": semister_1_subjects_types[i]
                },
                "semister2": {
                    "subjects": semister_2_subjects[i],
                    "subject_codes": semister_2_subjects_codes[i],
                    "subject_credits": semister_2_subjects_credits[i],
                    "total_credits": semister_2_total_credits[i],
                    "subject types": semister_2_subjects_types[i]
                },
                "semister3": {
                    "subjects": semister_3_subjects[i],
                    "subject_codes": semister_3_subjects_codes[i],
                    "subject_credits": semister_3_subjects_credits[i],
                    "total_credits": semister_3_total_credits[i],
                    "subject types": semister_3_subjects_types[i]
                },
                "semister4": {
                    "subjects": semister_4_subjects[i],
                    "subject_codes": semister_4_subjects_codes[i],
                    "subject_credits": semister_4_subjects_credits[i],
                    "total_credits": semister_4_total_credits[i],
                    "subject types": semister_4_subjects_types[i]
                },
                "semister5": {
                    "subjects": semister_5_subjects[i],
                    "subject_codes": semister_5_subjects_codes[i],
                    "subject_credits": semister_5_subjects_credits[i],
                    "total_credits": semister_5_total_credits[i],
                    "subject types": semister_5_subjects_types[i]
                },
                "semister6": {
                    "subjects": semister_6_subjects[i],
                    "subject_codes": semister_6_subjects_codes[i],
                    "subject_credits": semister_6_subjects_credits[i],
                    "total_credits": semister_6_total_credits[i],
                    "subject types": semister_6_subjects_types[i]
                },
                "semister7": {
                    "subjects": semister_7_subjects[i],
                    "subject_codes": semister_7_subjects_codes[i],
                    "subject_credits": semister_7_subjects_credits[i],
                    "total_credits": semister_7_total_credits[i],
                    "subject types": semister_7_subjects_types[i]
                },
                "semister8": {
                    "subjects": semister_8_subjects[i],
                    "subject_codes": semister_8_subjects_codes[i],
                    "subject_credits": semister_8_subjects_credits[i],
                    "total_credits": semister_8_total_credits[i],
                    "subject types": semister_8_subjects_types[i]
                }
            }

            parentDict[i] = childDict

        # Creating a list of all parsed records
        finalList = [parentDict[i] for i in parentDict.keys()]
        return finalList
    def register_rooms(self, col1, col2):
        style_metric_cards()
        col1.metric("Total Rooms Available In DB",self.roomsCollection.count_documents({}))
        col1.divider()
        selectedOption = col1.radio("Select the option", ["Manual Entry","set department photo"])
        if selectedOption=="set department photo":
            block=col2.selectbox("Please select the block",self.roomsCollection.distinct("block"))
            image=col2.file_uploader("Upload the department photo")
            if image:
                col2.image(image)
                if col2.button("conforim to set this image as an department logo",use_container_width=True,type='primary'):
                    if block:
                        result=self.roomsCollection.update_one({"block":block},{"$set":{"block_photo":Binary(image.getvalue())}})
                        if result.modified_count:
                            col2.success(f"Department photo is set for {block}")
                            style_metric_cards()
                            col2.metric("Number of documents Modified In DB",result.modified_count)
                    else:
                        col2.warning("Please Enetr the block first")
                else:
                    col2.info("Select block --> Upload block photo --> Click button to set the photo as department photo")

        if selectedOption == "Manual Entry":
            block = col2.text_input("Register block name")
            col2.subheader("Enter details for floor 1", divider='blue')
            floor1 = col2.text_input("Floor 1 Rooms ',' separated.\nWB-101,WB-102", help="If no rooms, write None")
            col2.subheader("Enter details for floor 2", divider='blue')
            floor2 = col2.text_input("Floor 2 Rooms ',' separated.\nWB-201,WB-202", help="If no rooms, write None")
            col2.subheader("Enter details for floor 3", divider='blue')
            floor3 = col2.text_input("Floor 3 Rooms ',' separated.\nWB-301,WB-302", help="If no rooms, write None")

            floors = {"floor1": floor1, "floor2": floor2, "floor3": floor3}
            for floor in floors:
                if floors[floor]:
                    if floors[floor].lower() == "none":
                        floors[floor] = None
                    else:
                        floors[floor] = floors[floor].split(',')

            if col2.button("Register", use_container_width=True, type='primary'):
                if not block:
                    block = None
                result = self.roomsCollection.insert_one(
                    {
                        "block": block,
                        "floor1": floors["floor1"],
                        "floor2": floors["floor2"],
                        "floor3": floors["floor3"]
                    }
                )
                if result.inserted_id:
                    col2.success(f"Block '{block}' registered successfully!")

    def editRooms(self, col1, col2):
        col1.subheader("Select the editing mode", divider='blue')
        selectedOptions = col1.radio("Options Available", ["edit block name", "edit room names", "delete rooms", "delete block"])

        if selectedOptions == "edit block name":
            block = col2.selectbox("Select the block to Edit block name", self.roomsCollection.distinct("block"))
            newBlockName = col2.text_input("Enter New Block Name")
            if col2.button("Confirm Edit", use_container_width=True, type='primary'):
                result = self.roomsCollection.update_one({"block": block}, {"$set": {"block": newBlockName}})
                if result.matched_count:
                    col2.success("Block name updated successfully!")
                    style_metric_cards()
                    col2.metric("Total Modified Count In DB", value=result.modified_count)
                else:
                    col2.error("Failed to update the block name. Please try again.")

        elif selectedOptions == "edit room names":
            block = col2.selectbox("Select the Block", self.roomsCollection.distinct("block"))
            selectFloor = col2.selectbox("Select the floor", [1, 2, 3, 4])
            block_data = self.roomsCollection.find_one({"block": block})
            if block_data and f"floor{selectFloor}" in block_data:
                availableRooms = block_data[f"floor{selectFloor}"]
                selectRoom = col2.selectbox('Select room to edit', availableRooms if availableRooms else ["None"])
                newRoomName = col2.text_input("Enter New Room Name")
                if col2.button("Confirm Edit", use_container_width=True, type='primary'):
                    updatedRooms = [newRoomName if room == selectRoom else room for room in availableRooms]
                    result = self.roomsCollection.update_one(
                        {"block": block},
                        {"$set": {f"floor{selectFloor}": updatedRooms}}
                    )
                    if result.matched_count:
                        col2.success(f"Room '{selectRoom}' updated to '{newRoomName}' successfully!")
                        style_metric_cards()
                        col2.metric("Total Modified Documents", value=result.modified_count)
                    else:
                        col2.error("Failed to update the room. Please try again.")

        elif selectedOptions == "delete rooms":
            block = col2.selectbox("Select the Block", self.roomsCollection.distinct("block"))
            selectFloor = col2.selectbox("Select the floor", [1, 2, 3, 4])
            block_data = self.roomsCollection.find_one({"block": block})
            if block_data and f"floor{selectFloor}" in block_data:
                availableRooms = block_data[f"floor{selectFloor}"]
                selectRoom = col2.selectbox('Select room to edit', availableRooms if availableRooms else ["None"])
                if col2.button("Confirm To Delete", use_container_width=True, type='primary'):
                    block_data[f"floor{selectFloor}"].remove(selectRoom)
                    result = self.roomsCollection.update_one(
                        {"block": block},
                        {"$set": {f"floor{selectFloor}": block_data[f"floor{selectFloor}"]}}
                    )
                    if result.matched_count:
                        col2.success(f"Room 'Deleted' successfully!")
                        style_metric_cards()
                        col2.metric("Total Modified Documents", value=result.modified_count)
                    else:
                        col2.error("Failed to update the room. Please try again.")

        elif selectedOptions == "delete block":
            block = col2.selectbox("Select the block to delete", self.roomsCollection.distinct("block"))
            if col2.button("Delete Block", use_container_width=True, type='primary'):
                result = self.roomsCollection.delete_one({"block": block})
                if result.deleted_count:
                    col2.success(f"The block '{block}' has been deleted successfully!")
                    style_metric_cards()
                    col2.metric("Total Deleted Documents", value=result.deleted_count)
                else:
                    col2.error("Failed to delete the block. Please try again.")
    def displayRooms(self, col1, col2):
        col2.subheader("Enter details here", divider='blue')
        block = col2.selectbox("Select the block", self.roomsCollection.distinct("block"))
        if col2.button("Search Block", use_container_width=True, type='primary'):
            block_data = self.roomsCollection.find_one({"block": block})
            if block_data:
                if "block_photo" in block_data:
                    col1.subheader("Department Photo",divider='blue')
                    col1.image(block_data["block_photo"])
                else:
                    col1.warning("No Department Photo is set")
                col1.json(block_data)
                
                    
                        
                    
                        
                        
                    
                