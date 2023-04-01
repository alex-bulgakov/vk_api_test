from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout


class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create username label and input field
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()

        # Create password label and input field
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        # Create login button
        self.login_button = QPushButton("Login")

        # Add widgets to layout
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)
