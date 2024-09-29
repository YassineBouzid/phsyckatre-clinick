import sys
import bcrypt
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QMessageBox, QTableWidget, QTableWidgetItem, QTextEdit, QFileDialog, QWidget
)
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtGui import QIcon

# SQLAlchemy setup
Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname_familyname = Column(String)
    age = Column(Integer)
    sex = Column(String)
    education_level = Column(String)
    address = Column(String)
    information = Column(Text)
    character = Column(Text)
    reason_visit = Column(String)
    from_whom = Column(String)
    history_illness = Column(Text)
    psychiatric_history = Column(Text)
    clinic_follow = Column(Text)
    diagnosis_history = Column(Text)
    propositions_directing = Column(Text)
    diagnosis = Column(Text)
    curing_program = Column(Text)
    evaluation = Column(Text)
    reporting = Column(Text)
    photo = Column(String)  # path to the patient's photo

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

# SQLite database setup
engine = create_engine('sqlite:///patients.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Home Page
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox

# Home Page
class HomePage(QMainWindow):
    def __init__(self):
        super(HomePage, self).__init__()
        self.setWindowTitle("الصفحة الرئيسية")
        self.setGeometry(100, 300, 1000, 900)
        self.setWindowIcon(QIcon('static/logo.ico'))  # Set your application icon

        center(self)

        self.layout = QVBoxLayout()

        # Simplify the table to show only the main information
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "الرقم", "الاسم واللقب", "السن", "العنوان", "سبب الزيارة"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)  # Adjusts column to fit the width
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #f5f5f5;
                font-size: 14px;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #3a86ff;
                color: white;
                font-weight: bold;
                height: 30px;
            }
        """)

        # Enable double-click on the table to open patient profile
        self.table.cellDoubleClicked.connect(self.open_profile_on_double_click)

        self.layout.addWidget(self.table)

        self.load_patients()

        # Add buttons with modern styles
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("إضافة")
        self.add_button.setStyleSheet(self.get_button_style())
        self.add_button.clicked.connect(self.add_patient)
        button_layout.addWidget(self.add_button)

        self.modify_button = QPushButton("تعديل")
        self.modify_button.setStyleSheet(self.get_button_style())
        self.modify_button.clicked.connect(self.modify_patient)
        button_layout.addWidget(self.modify_button)

        self.delete_button = QPushButton("حذف")
        self.delete_button.setStyleSheet(self.get_button_style())
        self.delete_button.clicked.connect(self.delete_patient)
        button_layout.addWidget(self.delete_button)

        self.profile_button = QPushButton("ملف المريض")
        self.profile_button.setStyleSheet(self.get_button_style())
        self.profile_button.clicked.connect(self.open_profile)
        button_layout.addWidget(self.profile_button)

        self.layout.addLayout(button_layout)

        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #3a86ff;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

    def load_patients(self):
        self.table.setRowCount(0)  # Clear table
        patients = session.query(Patient).all()
        for patient in patients:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(patient.id)))
            self.table.setItem(row_position, 1, QTableWidgetItem(patient.firstname_familyname))
            self.table.setItem(row_position, 2, QTableWidgetItem(str(patient.age)))
            self.table.setItem(row_position, 3, QTableWidgetItem(patient.address))
            self.table.setItem(row_position, 4, QTableWidgetItem(patient.reason_visit))

    def open_profile_on_double_click(self, row, column):
        """Opens the profile page when the user double-clicks a row."""
        selected_patient = self.get_selected_patient()
        if selected_patient:
            self.open_profile(selected_patient)

    def add_patient(self):
        self.modify_page = AddPage()
        self.modify_page.show()
        self.close()

    def modify_patient(self):
        selected_patient = self.get_selected_patient()
        if selected_patient:
            self.modify_page = ModifyPage(selected_patient)
            self.modify_page.show()
            self.close()

    def delete_patient(self):
        selected_patient = self.get_selected_patient()
        if selected_patient:
            confirm = QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد أنك تريد حذف هذا المريض؟", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                session.delete(selected_patient)
                session.commit()
                self.load_patients()
                #QMessageBox.information(self, "تم الحذف", "تم حذف المريض بنجاح")

    def open_profile(self, patient=None):
        """Open the profile of the selected patient."""
        if not patient:
            patient = self.get_selected_patient()
        
        if patient:
            self.profile_page = ProfilePage(patient)
            self.profile_page.show()

    def get_selected_patient(self):
        """Get the currently selected patient in the table."""
        selected_row = self.table.currentRow()
        if selected_row != -1:
            patient_id = self.table.item(selected_row, 0).text()
            return session.query(Patient).filter_by(id=patient_id).first()
        else:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار مريض")
            return None

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QMainWindow, QLabel, QLineEdit, QTextEdit, QPushButton, QScrollArea, QWidget, QFileDialog, QMessageBox

class AddPage(QMainWindow):
    def __init__(self):
        super(AddPage, self).__init__()
        self.setWindowTitle("متابعة المرضى")
        self.setGeometry(100, 300, 400, 1000)
        center(self)

        # Create a scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.layout = QVBoxLayout()

        # Create form fields in Arabic and apply styles
        self.firstname_familyname = self.create_styled_lineedit("الاسم واللقب", "form-control")
        self.age = self.create_styled_lineedit("السن", "form-control")
        self.sex = self.create_styled_lineedit("الجنس", "form-control")
        self.education_level = self.create_styled_lineedit("المستوى الدراسي", "form-control")
        self.address = self.create_styled_lineedit("العنوان", "form-control")

        self.information = self.create_styled_textedit("معلومات", "text-area")
        self.character = self.create_styled_textedit("الرمز", "text-area")
        self.reason_visit = self.create_styled_lineedit("سبب الزيارة", "form-control")
        self.from_whom = self.create_styled_lineedit("جهة الإحالة", "form-control")

        self.history_illness = self.create_styled_textedit("التاريخ المرضي", "text-area")
        self.psychiatric_history = self.create_styled_textedit("التاريخ النفسي والعقلي والعصبي", "text-area")
        self.clinic_follow = self.create_styled_textedit("المتابعات الإكلينيكية", "text-area")
        self.diagnosis_history = self.create_styled_textedit("مجريات الفحص + التاريخ", "text-area")

        self.propositions_directing = self.create_styled_textedit("التوجيهات والإحالات", "text-area")
        self.diagnosis = self.create_styled_textedit("التشخيص", "text-area")
        self.curing_program = self.create_styled_textedit("البرنامج العلاجي", "text-area")
        self.evaluation = self.create_styled_textedit("التقييم", "text-area")
        self.reporting = self.create_styled_textedit("التقرير", "text-area")

        # File dialog to upload a photo
        self.photo_button = QPushButton("تحميل صورة")
        self.photo_button.setStyleSheet(self.get_button_style())
        self.photo_button.clicked.connect(self.upload_photo)
        self.layout.addWidget(self.photo_button)

        # Submit button
        self.submit_button = QPushButton("إضافة")
        self.submit_button.setStyleSheet(self.get_button_style())
        self.submit_button.clicked.connect(self.submit_data)
        self.layout.addWidget(self.submit_button)

        # Back to Home button
        self.back_button = QPushButton("العودة إلى الصفحة الرئيسية")
        self.back_button.setStyleSheet(self.get_button_style())
        self.back_button.clicked.connect(self.go_back_home)
        self.layout.addWidget(self.back_button)

        # Widget to hold layout and scroll area
        content_widget = QWidget()
        content_widget.setLayout(self.layout)
        self.scroll_area.setWidget(content_widget)
        self.setCentralWidget(self.scroll_area)

        # Apply global styles
        self.set_global_styles()

    def create_styled_lineedit(self, placeholder, class_name):
        """Helper function to create and style QLineEdit."""
        lineedit = QLineEdit(self)
        lineedit.setPlaceholderText(placeholder)
        lineedit.setObjectName(class_name)
        self.layout.addWidget(QLabel(placeholder))
        self.layout.addWidget(lineedit)
        return lineedit

    def create_styled_textedit(self, label_text, class_name):
        """Helper function to create and style QTextEdit."""
        textedit = QTextEdit(self)
        textedit.setObjectName(class_name)
        self.layout.addWidget(QLabel(label_text))
        self.layout.addWidget(textedit)
        return textedit

    def set_global_styles(self):
        """Set global stylesheet for the entire form."""
        self.setStyleSheet("""
            .form-control {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
                margin-bottom: 10px;
            }
            QLabel {
               
                font-size: 18px;
                font-weight: bold;
                color: #2E7D32;
                margin-bottom: 5px;
            
            }
            .text-area {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 16px;
                height: 80px;
                margin-bottom: 10px;
            }
            QPushButton {
                background-color: #3a86ff;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                width:50px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

    def get_button_style(self):
        """Button style consistent with the home page."""
        return """
            QPushButton {
                background-color: #3a86ff;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

    def go_back_home(self):
        # Navigate back to the home page
        self.home_page = HomePage()
        self.home_page.show()
        self.close()
    
    def upload_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "اختر الصورة", "", "Image Files (*.png *.jpg *.bmp)")
        #print('----------------filename = ------------------------', file_name)
        if file_name:
            self.photo_path = file_name
            save_picture(file_name)

    def submit_data(self):
        # Save patient data to the database

        
        patient_data = {
            "firstname_familyname": self.firstname_familyname.text(),
            "age": self.age.text(),
            "sex": self.sex.text(),
            "education_level": self.education_level.text(),
            "address": self.address.text(),
            "information": self.information.toPlainText(),
            "character": self.character.toPlainText(),
            "reason_visit": self.reason_visit.text(),
            "from_whom": self.from_whom.text(),
            "history_illness": self.history_illness.toPlainText(),
            "psychiatric_history": self.psychiatric_history.toPlainText(),
            "clinic_follow": self.clinic_follow.toPlainText(),
            "diagnosis_history": self.diagnosis_history.toPlainText(),
            "propositions_directing": self.propositions_directing.toPlainText(),
            "diagnosis": self.diagnosis.toPlainText(),
            "curing_program": self.curing_program.toPlainText(),
            "evaluation": self.evaluation.toPlainText(),
            "reporting": self.reporting.toPlainText(),
            "photo": self.photo_path if hasattr(self, 'photo_path') else None,
        }

        # Save patient data to the database
        add_patient(patient_data)
        QMessageBox.information(self, "تم الحفظ", "تم حفظ بيانات المريض بنجاح")
        self.home_page = HomePage()
        self.home_page.show()
        self.close()

# The add_patient function remains unchanged.self.sex = Column(String)
def add_patient(patient_data):
    new_patient = Patient(
        firstname_familyname=patient_data["firstname_familyname"],
        age=patient_data["age"],
        sex=patient_data["sex"],
        education_level=patient_data["education_level"],
        address=patient_data["address"],
        information=patient_data["information"],
        character=patient_data["character"],
        reason_visit=patient_data["reason_visit"],
        from_whom=patient_data["from_whom"],
        history_illness=patient_data["history_illness"],
        psychiatric_history=patient_data["psychiatric_history"],
        clinic_follow=patient_data["clinic_follow"],
        diagnosis_history=patient_data["diagnosis_history"],
        propositions_directing=patient_data["propositions_directing"],
        diagnosis=patient_data["diagnosis"],
        curing_program=patient_data["curing_program"],
        evaluation=patient_data["evaluation"],
        reporting=patient_data["reporting"],
        photo=patient_data["photo"]
    )
    session.add(new_patient)
    session.commit()

def center(window):
    """Centers the given window on the screen."""
    screen = QDesktopWidget().screenGeometry()
    window_size = window.geometry()
    x = (screen.width() - window_size.width()) // 2
    y = (screen.height() - window_size.height()) // 2
    window.move(x, y)


from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QMainWindow, QLineEdit, QPushButton, QTextEdit, QScrollArea, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
class ModifyPage(QMainWindow):
    def __init__(self, patient):
        super(ModifyPage, self).__init__()
        self.patient = patient
        self.photo_path = patient.photo
        self.setWindowTitle("تعديل المريض")
        self.setGeometry(100, 300, 400, 1000)
        center(self)

        # Create a scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.layout = QVBoxLayout()

        # Helper functions for input and label styling
        def create_styled_input(text=""):
            input_field = QLineEdit(self)
            input_field.setText(text)
            input_field.setStyleSheet("""
                padding: 10px; 
                border: 1px solid #388E3C; 
                border-radius: 5px;
                font-size: 14px;
            """)
            return input_field

        def create_styled_textarea(text=""):
            textarea = QTextEdit(self)
            textarea.setText(text)
            textarea.setStyleSheet("""
                padding: 10px;
                border: 1px solid #388E3C;
                border-radius: 5px;
                font-size: 16px;
            """)
            return textarea

        def create_styled_label(text):
            label = QLabel(text, self)
            label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: #2E7D32;
                margin-bottom: 5px;
            """)
            return label
       
        # Using the helper functions for creating fields and labels
        self.firstname_familyname = create_styled_input(self.patient.firstname_familyname)
        self.layout.addWidget(create_styled_label("الاسم واللقب"))
        self.layout.addWidget(self.firstname_familyname)

        self.age = create_styled_input(str(self.patient.age))
        self.layout.addWidget(create_styled_label("السن"))
        self.layout.addWidget(self.age)

        self.sex = create_styled_input(str(self.patient.sex))
        self.layout.addWidget(create_styled_label("الجنس"))
        self.layout.addWidget(self.sex)

        self.education_level = create_styled_input(self.patient.education_level)
        self.layout.addWidget(create_styled_label("المستوى الدراسي"))
        self.layout.addWidget(self.education_level)

        self.address = create_styled_input(self.patient.address)
        self.layout.addWidget(create_styled_label("العنوان"))
        self.layout.addWidget(self.address)

        self.information = create_styled_textarea(self.patient.information)
        self.layout.addWidget(create_styled_label("معلومات"))
        self.layout.addWidget(self.information)

        self.character = create_styled_textarea(self.patient.character)
        self.layout.addWidget(create_styled_label("الرمز"))
        self.layout.addWidget(self.character)

        self.reason_visit = create_styled_input(self.patient.reason_visit)
        self.layout.addWidget(create_styled_label("سبب الزيارة"))
        self.layout.addWidget(self.reason_visit)

        self.from_whom = create_styled_input(self.patient.from_whom)
        self.layout.addWidget(create_styled_label("جهة الإحالة"))
        self.layout.addWidget(self.from_whom)

        self.history_illness = create_styled_textarea(self.patient.history_illness)
        self.layout.addWidget(create_styled_label("التاريخ المرضي"))
        self.layout.addWidget(self.history_illness)

        self.psychiatric_history = create_styled_textarea(self.patient.psychiatric_history)
        self.layout.addWidget(create_styled_label("التاريخ النفسي والعقلي"))
        self.layout.addWidget(self.psychiatric_history)

        self.clinic_follow = create_styled_textarea(self.patient.clinic_follow)
        self.layout.addWidget(create_styled_label("المتابعات الاكلينيكية"))
        self.layout.addWidget(self.clinic_follow)

        self.diagnosis_history = create_styled_textarea(self.patient.diagnosis_history)
        self.layout.addWidget(create_styled_label("مجريات الفحص"))
        self.layout.addWidget(self.diagnosis_history)

        self.propositions_directing = create_styled_textarea(self.patient.propositions_directing)
        self.layout.addWidget(create_styled_label("التوجيهات والاحالات"))
        self.layout.addWidget(self.propositions_directing)

        self.diagnosis = create_styled_textarea(self.patient.diagnosis)
        self.layout.addWidget(create_styled_label("التشخيص"))
        self.layout.addWidget(self.diagnosis)

        self.curing_program = create_styled_textarea(self.patient.curing_program)
        self.layout.addWidget(create_styled_label("البرنامج العلاجي"))
        self.layout.addWidget(self.curing_program)

        self.evaluation = create_styled_textarea(self.patient.evaluation)
        self.layout.addWidget(create_styled_label("التقييم"))
        self.layout.addWidget(self.evaluation)

        self.reporting = create_styled_textarea(self.patient.reporting)
        self.layout.addWidget(create_styled_label("التقرير"))
        self.layout.addWidget(self.reporting)

        # File dialog to upload a photo
        self.photo_button = QPushButton("تحميل صورة")
        self.photo_button.setStyleSheet(self.get_button_style())
        self.photo_button.clicked.connect(self.upload_photo)
        self.layout.addWidget(self.photo_button)
        

        # Save button
        self.save_button = QPushButton("حفظ")
        self.save_button.setStyleSheet(self.get_button_style())
        self.layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_changes)

        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        # Create a QWidget to hold the layout, and set it as the scroll area's widget
        content_widget = QWidget()
        content_widget.setLayout(self.layout)

         # Back to Home button
        self.back_button = QPushButton("العودة إلى الصفحة الرئيسية")
        
        self.back_button.setStyleSheet(self.get_button_style())
        self.back_button.clicked.connect(self.go_back_home)
        self.layout.addWidget(self.back_button)

        # Set the content widget to the scroll area
        self.scroll_area.setWidget(content_widget)

        # Set the scroll area as the central widget of the window
        self.setCentralWidget(self.scroll_area)

    def upload_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "اختر الصورة", "", "Image Files (*.png *.jpg *.bmp)")
        #print("-----------filename=---------------",file_name)
        if file_name:
            self.photo_path = file_name
            save_picture(file_name)
            

    def go_back_home(self):
            # Navigate back to the home page
            self.home_page = HomePage()
            self.home_page.show()
            self.close()

    def get_button_style(self):
            """Button style consistent with the home page."""
            return """
                QPushButton {
                    background-color: #3a86ff;
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """
    def save_changes(self):
        self.patient.firstname_familyname = self.firstname_familyname.text()
        self.patient.age = self.age.text()
        self.patient.sex = self.sex.text()
        self.patient.education_level = self.education_level.text()
        self.patient.address = self.address.text()
        self.patient.information = self.information.toPlainText()
        self.patient.character = self.character.toPlainText()
        self.patient.reason_visit = self.reason_visit.text()
        self.patient.from_whom = self.from_whom.text()
        self.patient.history_illness = self.history_illness.toPlainText()
        self.patient.psychiatric_history = self.psychiatric_history.toPlainText()
        self.patient.clinic_follow = self.clinic_follow.toPlainText()
        self.patient.diagnosis_history = self.diagnosis_history.toPlainText()
        self.patient.propositions_directing = self.propositions_directing.toPlainText()
        self.patient.diagnosis = self.diagnosis.toPlainText()
        self.patient.curing_program = self.curing_program.toPlainText()
        self.patient.evaluation = self.evaluation.toPlainText()
        self.patient.reporting = self.reporting.toPlainText()
        self.patient.photo = self.photo_path
        
        session.commit()
        QMessageBox.information(self, "تم الحفظ", "تم حفظ التعديلات بنجاح")
        self.home_page = HomePage()
        self.home_page.show()
        self.close()


from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QMainWindow, QLineEdit, QPushButton, QMessageBox, QDesktopWidget
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

class LoginPage(QMainWindow):
    def __init__(self):
        super(LoginPage, self).__init__()
        self.setWindowTitle("تسجيل الدخول")
        self.setGeometry(300, 300, 400, 200)

        # Set background color
        self.setStyleSheet("background-color: #E0F7FA;")  # Light relaxing cyan color

        # Center the window on the screen
        center(self)


        # Create the layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignLeft)  # Align items to the right

        # Username input
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("اسم المستخدم")
        self.username_input.setStyleSheet("padding: 10px; border: 1px solid #00897B; border-radius: 5px;")
        self.layout.addWidget(QLabel("اسم المستخدم", alignment=Qt.AlignLeft))  # Align label to the right
        self.layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 10px; border: 1px solid #00897B; border-radius: 5px;")
        self.layout.addWidget(QLabel("كلمة المرور", alignment=Qt.AlignLeft))  # Align label to the right
        self.layout.addWidget(self.password_input)

        # Login button
        self.login_button = QPushButton("تسجيل الدخول")
        self.login_button.setStyleSheet("""
            background-color: #00897B; 
            color: white; 
            padding: 10px; 
            border: none; 
            border-radius: 5px; 
            font-size: 16px; 
            font-weight: bold;
        """) 
        # Styled button

        # Connect the returnPressed signal for both fields to trigger login when Enter is pressed
        self.username_input.returnPressed.connect(self.login)
        self.password_input.returnPressed.connect(self.login)

        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        # Create a central widget and set the layout
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول")
            return

        # Check if the username exists
        user = session.query(User).filter_by(username=username).first()

        if user is None:
            QMessageBox.warning(self, "خطأ", "اسم المستخدم غير موجود")
        else:
            # Verify the password
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                #QMessageBox.information(self, "نجاح", "تم تسجيل الدخول بنجاح")
                self.home_page = HomePage()
                self.home_page.show()
                self.close()  # Close the login page
            else:
                QMessageBox.warning(self, "خطأ", "كلمة المرور غير صحيحة")


from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QMainWindow, QGridLayout, QFrame, QPushButton, QScrollArea
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor
from PyQt5.QtCore import Qt

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from bidi.algorithm import get_display
import arabic_reshaper

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportImage

# Add the Arabic TTF font
pdfmetrics.registerFont(TTFont('Arabic', 'static/Amiri-Regular.ttf'))  # Replace with the actual path to your Arabic font

def reshape_text(text):
    # Reshape and apply Bidi algorithm to make Arabic readable
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

class ProfilePage(QMainWindow):
    def __init__(self, patient):
        super(ProfilePage, self).__init__()
        self.setWindowTitle("ملف المريض")
        self.setGeometry(100, 300, 1000, 900)
        center(self)
        #print("-------------------------------",)

        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Container for scroll area content
        content_widget = QWidget()
        self.layout = QGridLayout(content_widget)
        
        # Set relaxing background color
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor("#E6F7F5"))  # Light pastel color for relaxation
        content_widget.setAutoFillBackground(True)
        content_widget.setPalette(palette)
        
        # Apply modern font styles
        header_font = QFont("Arial", 12, QFont.Bold)
        info_font = QFont("Arial", 10)
        
        # Add patient photo with rounded corners and shadow on the left side
        if patient.photo:
            photo_label = QLabel()
            pixmap = QPixmap(patient.photo).scaled(250, 150, Qt.KeepAspectRatio)
            photo_label.setPixmap(pixmap)
            photo_label.setAlignment(Qt.AlignCenter)
            photo_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            photo_label.setStyleSheet("border-radius: 10px; padding: 10px; background-color: #f0f0f0;")
            self.layout.addWidget(photo_label, 0, 0, 4, 1)  # Span across 4 rows for the photo
        
        # Add all patient information with labels aligned right-to-left
        self.add_grid_item("الاسم واللقب:", patient.firstname_familyname, 0, 1, header_font, info_font)
        self.add_grid_item("السن:", patient.age, 1, 1, header_font, info_font,align_value=True)
        
        self.add_grid_item("الجنس:", patient.sex, 1, 1, header_font, info_font,align_value=True)

        self.add_grid_item("المستوى الدراسي:", patient.education_level, 2, 1, header_font, info_font)
        self.add_grid_item("العنوان:", patient.address, 3, 1, header_font, info_font)
        self.add_grid_item_with_show_more("معلومات:", patient.information, 4, 1, header_font, info_font)
        self.add_grid_item("الطبع:", patient.character, 6, 1, header_font, info_font)
        self.add_grid_item("سبب الزيارة:", patient.reason_visit, 8, 1, header_font, info_font)
        self.add_grid_item("من طرف:", patient.from_whom, 10, 1, header_font, info_font)
        self.add_grid_item_with_show_more("التاريخ المرضي:", patient.history_illness, 12, 1, header_font, info_font)
        self.add_grid_item_with_show_more("التاريخ النفسي:", patient.psychiatric_history, 14, 1, header_font, info_font)
        self.add_grid_item_with_show_more("المتابعة السريرية:", patient.clinic_follow, 16, 1, header_font, info_font)
        self.add_grid_item_with_show_more("التشخيص:", patient.diagnosis, 18, 1, header_font, info_font)
        self.add_grid_item_with_show_more("تاريخ التشخيص:", patient.diagnosis_history, 20, 1, header_font, info_font)
        self.add_grid_item("التوجيهات والاقتراحات:", patient.propositions_directing, 22, 1, header_font, info_font)
        self.add_grid_item_with_show_more("الخطة العلاجية:", patient.curing_program, 24, 1, header_font, info_font)
        self.add_grid_item("التقييم:", patient.evaluation, 26, 1, header_font, info_font)
        self.add_grid_item_with_show_more("التقرير:", patient.reporting, 28, 1, header_font, info_font)

       
        # Add border to the layout (optional padding for inner content)
        content_widget.setStyleSheet("""
            background-color: #f0f0f0; /* Light background for the content */
            border: 2px solid #2E7D32; /* Green border color for photo and middle column */
            border-radius: 10px; /* Rounded corners */
            padding: 15px; /* Padding for inner content */
        """)

        # Add the content widget to the scroll area
        scroll_area.setWidget(content_widget)

         # Set column stretch factors
        self.layout.setColumnStretch(3, 0)  # First column (labels) will take 1 part
        self.layout.setColumnStretch(2, 1)  # Second column (values) will take 2 parts
        #self.layout.setColumnStretch(2, 1)  # Third column (if any, otherwise this can be omitted)


        # Main layout of the central widget
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(scroll_area)
    

    
        # Add buttons for generating report and returning to home
        button_layout = QVBoxLayout()

        generate_report_btn = QPushButton("PDF التقرير")
        generate_report_btn.setStyleSheet(self.get_button_style())
        generate_report_btn.clicked.connect(lambda: self.create_patient_report(patient))
        button_layout.addWidget(generate_report_btn)

        return_home_btn = QPushButton("العودة إلى الصفحة الرئيسية")
        
        return_home_btn.setStyleSheet(self.get_button_style())
        return_home_btn.clicked.connect(self.return_to_home)
        button_layout.addWidget(return_home_btn)

        main_layout.addLayout(button_layout)

    # Utility function to add grid items with styled headers and values (RTL alignment)
    def get_button_style(self):
            """Button style consistent with the home page."""
            return """
                QPushButton {
                    background-color: #3a86ff;
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """
    def add_grid_item(self, label_text, value, row, col, header_font, info_font, align_value=False):
        label = QLabel(label_text)
        label.setFont(header_font)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        value_label = QLabel(str(value))
        value_label.setFont(info_font)
        value_label.setWordWrap(True)
        
        # Set alignment for the value label if specified
        if align_value:
            value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        else:
            value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Default alignment

        self.layout.addWidget(label, row, col * 2 + 1)
        self.layout.addWidget(value_label, row, col * 2)

    # Utility function to add grid items with "Show more" functionality (RTL alignment)
    def add_grid_item_with_show_more(self, label_text, value, row, col, header_font, info_font):
        label = QLabel(label_text)
        label.setFont(header_font)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Short version of the text (displayed initially)
        short_text = QLabel(value[:100] + '...' if len(value) > 100 else value)
        short_text.setFont(info_font)
        short_text.setWordWrap(True)
        short_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Full version of the text (hidden initially)
        full_text = QLabel(value)
        full_text.setFont(info_font)
        full_text.setWordWrap(True)
        full_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        full_text.setVisible(False)  # Initially hidden

        # Button to show more text
        show_more_btn = QPushButton("المزيد")
        show_more_btn.setStyleSheet("color: blue; text-decoration: underline; border: none; background: none;")
        show_more_btn.clicked.connect(lambda: self.toggle_text_visibility(full_text, show_more_btn, short_text))

        self.layout.addWidget(label, row, col * 2 + 1)
        self.layout.addWidget(short_text, row, col * 2)
        self.layout.addWidget(full_text, row, col * 2)  # Hidden initially
        self.layout.addWidget(show_more_btn, row + 1, col * 2)

    # Function to toggle between showing the short and full text
    def toggle_text_visibility(self, full_text, btn, short_text):
        if full_text.isVisible():
            full_text.setVisible(False)
            short_text.setVisible(True)
            btn.setText("المزيد")
        else:
            full_text.setVisible(True)
            short_text.setVisible(False)
            btn.setText("إخفاء")


    # Generate a PDF report
    def create_patient_report(self, patient):
        file_path = f"{patient.firstname_familyname}_report.pdf"

        # Create the PDF document
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()

        # Custom style for Arabic text
        arabic_style = ParagraphStyle(name='Arabic', fontName='Arabic', fontSize=12, alignment=2)  # Right align

        arabic_style_header = ParagraphStyle(name='Arabic', fontName='Arabic', fontSize=14, alignment=2)  # Right align


        arabic_style_header_top = ParagraphStyle(
                name='ArabicHeader',
                fontName='Arabic',             # Arabic font
                fontSize=22,                   # Larger font size for headers
                alignment=1,           # Center align the text
                textColor=colors.HexColor("#006699"),  # Custom color (dark blue)
                spaceAfter=24,                 # Add space after the header
                spaceBefore=12,                # Add space before the header
                leading=22,                    # Increase line height/leading for better readability
                borderPadding=(10, 5, 10, 5),  # Padding (top, left, bottom, right)
                borderColor=colors.HexColor("#006699"),  # Border color matching the text
                borderWidth=1,                 # Border width
                borderRadius=5,                # Rounded corners for the border
                backColor=colors.HexColor("#E6F7F5"),  # Light background color to make the header stand out
                bold=True                      # Make the text bold
            )

        # Report content
        report_content = []


        # Clinic Name and Date
        pdfmetrics.registerFont(TTFont('Arabic', 'static/Amiri-Bold.ttf'))
        report_content.append(Paragraph(reshape_text("عيادة بارود"), arabic_style_header_top))
        report_content.append(Spacer(1, 24))
        pdfmetrics.registerFont(TTFont('Arabic', 'static/Amiri-Regular.ttf'))
        report_content.append(Paragraph(reshape_text(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d')}"), arabic_style))
        report_content.append(Spacer(1, 24))

        
         # Add patient's photo at the top-left corner
        if patient.photo and os.path.exists(patient.photo):
            patient_image = ReportImage(patient.photo, 1.5 * inch, 1.5 * inch)  # Adjust size as needed
            patient_image.hAlign = 'LEFT'
            report_content.append(patient_image)

        # Patient Details
        report_content.append(Paragraph(reshape_text(f"الاسم واللقب: {patient.firstname_familyname}"), arabic_style_header))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"السن: {patient.age}"), arabic_style_header))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"الجنس: {patient.sex}"), arabic_style_header))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"المستوى الدراسي: {patient.education_level}"), arabic_style_header))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"العنوان: {patient.address}"), arabic_style_header))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"  معلومات : "), arabic_style_header))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"{patient.information}"), arabic_style))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"  التشخيص : "), arabic_style_header))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"{patient.diagnosis}"), arabic_style))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"  التوجيهات وااقتراحات : "), arabic_style_header))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"{patient.propositions_directing}"), arabic_style))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"  الخطةالعلاجية : "), arabic_style_header))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"{patient.curing_program}"), arabic_style))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"  التقييم :"), arabic_style_header))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"{patient.evaluation}"), arabic_style))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"  التقرير :"), arabic_style_header))
        report_content.append(Spacer(1, 12))
        report_content.append(Paragraph(reshape_text(f"{patient.reporting}"), arabic_style))

        

        

        # Doctor's Signaturereport_content.append(Spacer(1, 24))
        report_content.append(Spacer(1, 24))
        report_content.append(Spacer(1, 24))
        report_content.append(Paragraph(reshape_text("_____________________________________________________________________________"), arabic_style))
        report_content.append(Spacer(1, 24))
        report_content.append(Paragraph(reshape_text("<u> توقيع الطبيب </u>"), arabic_style_header))
        report_content.append(Spacer(1, 24))
      
        # Add doctor's signature image at the bottom
        if  os.path.exists(r'static/path_to_doctor_signature.png'):
            signature_image = ReportImage(r'static/path_to_doctor_signature.png', 0.75 * inch, 0.75 * inch)  # Adjust size as needed
            signature_image.hAlign = 'RIGHT'
            report_content.append(signature_image)

        # Build the PDF
        doc.build(report_content)
        
        QMessageBox.information(self, "تم الحفظ", "تم اخراج التقرير للمريض بنجاح")
        
        self.close()

    def return_to_home(self):
        self.close()








import secrets
import os 
from PIL import Image


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext= os.path.splitext(form_picture)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join('.', 'static',picture_fn)
    outpu_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(outpu_size)
    i.save(picture_path)

    #form_picture.save(picture_path)
    return picture_fn

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Set application icon globally (optional)
    app.setWindowIcon(QIcon('static/logo.ico'))
    
    # Uncomment to create a new user (only needs to be done once for initial setup)

    hashed_password = bcrypt.hashpw("xxxxxxxxxxxxxxxx".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin = User(id=1,username= "xxxxxxxxxxxxx", password_hash=hashed_password)
    admin_in_database = session.query(User).filter_by(id=admin.id).first()
    if admin_in_database == None:
        new_user = User(username="admin", password_hash=hashed_password)
        session.add(new_user)
        session.commit()

    login_page = LoginPage()
    #login_page = HomePage()
    login_page.show()

    sys.exit(app.exec_())
