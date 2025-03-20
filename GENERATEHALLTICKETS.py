import streamlit as st
import pymongo
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, gray, blue, white
from PIL import Image
import qrcode

class GenerateHallTickets:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.scheduledDB = self.client["ScheduledExams"]
        self.studentsDB = self.client["StudentsDB"]
        self.studentsCollection = self.studentsDB["StudentsCollection"]
        self.hallTicketsDB = self.client["HallTicketsDB"]
        self.selected_roll_number = None

    def __del__(self):
        self.client.close()

    def generate_qr_code(self, data):
        qr = qrcode.QRCode()
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="blue", back_color="white")
        qr_buffer = BytesIO()
        img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        return qr_buffer

    def create_pdf(self, student, exam_details, instructions):
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        page_width, page_height = letter
        border_padding = 10

        # Draw Border
        c.setStrokeColor(black)
        c.setLineWidth(3)
        c.rect(border_padding, border_padding, page_width - 2 * border_padding, page_height - 2 * border_padding)

        # Header
        c.setFillColor(blue)
        c.rect(0, page_height - 40, page_width, 40, fill=1)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(page_width / 2, page_height - 30, f"Hall Ticket for {student['roll_number']}")

        # Image & QR code sizes
        img_width = page_width * 0.15
        img_height = page_height * 0.15
        qr_width = page_width * 0.15
        qr_height = page_height * 0.15
        x_position = border_padding + 10
        qr_x_position = page_width - qr_width - border_padding - 10
        y_position = page_height - img_height - 60

        # Draw Student Photo
        if student.get("front_photo"):
            image_data = BytesIO(student["front_photo"])
            image = Image.open(image_data)
            temp_image = BytesIO()
            image.save(temp_image, format="PNG")
            temp_image.seek(0)
            c.drawInlineImage(Image.open(BytesIO(temp_image.getvalue())), x_position, y_position, width=img_width, height=img_height)
        c.rect(x_position - 2, y_position - 2, img_width + 4, img_height + 4)

        # Draw QR Code
        qr_code = self.generate_qr_code(student["roll_number"])
        c.drawInlineImage(Image.open(qr_code), qr_x_position, y_position, width=qr_width, height=qr_height)
        c.rect(qr_x_position - 2, y_position - 2, qr_width + 4, qr_height + 4)

        # Draw Student Information Box
        text_x_position = x_position + img_width + 10
        info_box_width = page_width * 0.50
        info_box_height = img_height + 10
        c.setStrokeColor(black)
        c.rect(text_x_position, y_position, info_box_width, info_box_height)

        # Draw Student Information
        c.setFont("Helvetica", 10)
        info_lines = [
            f"College Name: Madanapalle Institute of Technology and Science",
            f"College Code: M-90",
            f"College Location: Madanapalle",
            f"Student Name: {student['fullname']}",
            f"Batch: {student['batch']}",
            f"Branch: {student['branch']}",
            f"Semester: {student['semester']}"
        ]
        text_y_position = y_position + img_height - 5
        for line in info_lines:
            c.drawString(text_x_position + 10, text_y_position, line)  # Adjusting for margin
            text_y_position -= 12  # Reduce spacing

        # Exam Instructions
        instruction_y_position = y_position - 50
        c.setFont("Helvetica-Bold", 12)
        c.drawString(border_padding, instruction_y_position, "Instructions:")
        instruction_y_position -= 20
        c.setFont("Helvetica", 10)
        for instruction in instructions:
            c.drawString(border_padding, instruction_y_position, f"• {instruction}")
            instruction_y_position -= 15

        c.showPage()
        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    def display(self):
        st.title("Hall Ticket Management System")
        tab1, tab2 = st.tabs(["Generate Hall Tickets", "View Hall Tickets"])

        with tab1:
            collections = self.scheduledDB.list_collection_names()
            selected_collection = st.selectbox("Select an Exam Collection", collections)
            if selected_collection and st.button("Confirm to Generate Hall Tickets"):
                exam_details = " ".join(selected_collection.split("_"))
                students = self.studentsCollection.find()
                
                for student in students:
                    pdf_data = self.create_pdf(
                        student,
                        exam_details,
                        [
                            "BRING YOUR HALL TICKET",
                            "DON’T BRING MOBILES",
                            "PLEASE BE SEATED IN YOUR ALLOTTED BENCH ONLY",
                            "FOLLOW THE INSTRUCTIONS CAREFULLY"
                        ]
                    )
                    self.hallTicketsDB[f"{selected_collection}_hallTickets"].insert_one({
                        "roll_number": student["roll_number"],
                        "hall_ticket": base64.b64encode(pdf_data).decode('utf-8')
                    })
                st.success("Hall tickets generated successfully!")

        with tab2:
            col1, col2 = st.columns([1, 2])
            with col1:
                hall_ticket_collections = self.hallTicketsDB.list_collection_names()
                selected_hall_ticket_collection = st.selectbox("Select a Hall Ticket Collection", hall_ticket_collections)
                if selected_hall_ticket_collection:
                    roll_numbers = [
                        doc["roll_number"]
                        for doc in self.hallTicketsDB[selected_hall_ticket_collection].find({}, {"roll_number": 1, "_id": 0})
                    ]
                    self.selected_roll_number = st.selectbox("Select a Roll Number", roll_numbers)
            
            with col2:
                if self.selected_roll_number:
                    hall_ticket = self.hallTicketsDB[selected_hall_ticket_collection].find_one(
                        {"roll_number": self.selected_roll_number}, {"hall_ticket": 1, "_id": 0}
                    )
                    if hall_ticket:
                        pdf_binary = base64.b64decode(hall_ticket["hall_ticket"])
                        st.download_button(
                            label="Download Hall Ticket",
                            data=pdf_binary,
                            file_name=f"{self.selected_roll_number}_hall_ticket.pdf",
                            mime="application/pdf"
                        )
