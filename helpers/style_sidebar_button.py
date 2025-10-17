from PySide6.QtWidgets import QPushButton

def style_toolbar_button(btn: QPushButton):
    btn.setCheckable(True)
    btn.setStyleSheet("""
        QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 6px 12px;
    }

    QPushButton:hover {
        background-color: #3a3a3a;
        border-color: #5a5a5a;
    }

    QPushButton:pressed {
        background-color: #505050;
        border-color: #6c6c6c;
        color: #ffffff;
    }

    QPushButton:checked {
        background-color: #1e88e5;
        border-color: #1976d2;
        color: white;
    }

    QPushButton:disabled {
        background-color: #1c1c1c;
        color: #666666;
        border-color: #2a2a2a;
    }
    """)
