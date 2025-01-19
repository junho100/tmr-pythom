from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, 
                           QLabel, QMessageBox)
from breathing_window import BreathingVisualizer
from api.user_api import verify_user

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('사용자 인증')
        self.setGeometry(300, 300, 300, 150)
        
        layout = QVBoxLayout()
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText('ID를 입력하세요')
        layout.addWidget(self.id_input)
        
        self.login_btn = QPushButton('로그인')
        self.login_btn.clicked.connect(self.verify_user)
        layout.addWidget(self.login_btn)
        
        self.status_label = QLabel('')
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def verify_user(self):
        user_id = self.id_input.text()
        if not user_id:
            QMessageBox.warning(self, '경고', 'ID를 입력해주세요')
            return
            
        success, message = verify_user(user_id)
        if success:
            self.breathing_window = BreathingVisualizer(user_id)
            self.breathing_window.show()
            self.close()
        else:
            QMessageBox.warning(self, '로그인 실패', message)
            self.status_label.setText(message)