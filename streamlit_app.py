import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.metric_cards import *  # Ensure you have installed this package
from STUDENTS import Students
from TEACHERS import Teachers
from DEPARTMENTS import Departments
from SCHEDULE import Schedule
from DFORMS import DForms
from VALIDATION import Validation
from GENERATEHALLTICKETS import GenerateHallTickets
# Sidebar option menu for navigation
with st.sidebar:
  selectedOption = option_menu(
    "Select the operation to perform",  # Title of the sidebar
    ["students", "teachers", "departments & rooms", "schedule", "generate hall tickets", "dform's", "validation sheets"],  # List of options
    icons=["person", "person-fill", "building", "calendar","ticket", "file-earmark-text", "check-circle"],  # Add icons to each option
    default_index=0,  # Default option, can be adjusted
    orientation="vertical",  # Sidebar style
)

# Use a conditional block to display content based on selected option
if selectedOption == "students":
    students=Students().display()

elif selectedOption == "teachers":
    teachers=Teachers().display()

elif selectedOption == "departments & rooms":
    departments=Departments().display()

elif selectedOption == "schedule":
    schedule=Schedule().display()

elif selectedOption == "generate hall tickets":
    GenerateHallTickets().display()

elif selectedOption == "dform's":
    DForms().display()

elif selectedOption == "validation sheets":
    Validation().display()
