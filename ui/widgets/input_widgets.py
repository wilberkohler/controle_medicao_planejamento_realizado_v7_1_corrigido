from PySide6.QtWidgets import QLineEdit, QDialog, QVBoxLayout, QCalendarWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import QDate
from utils.number_utils import br_number

class DateLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("DD-MM-AAAA")

class CalendarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selecionar data")
        self.resize(320, 300)
        layout = QVBoxLayout(self)
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        layout.addWidget(self.calendar)
        btns = QHBoxLayout()
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        btns.addWidget(self.btn_ok)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

    def set_date_text(self, text):
        parts = str(text or "").split("-")
        if len(parts) == 3:
            try:
                d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
                self.calendar.setSelectedDate(QDate(y, m, d))
            except Exception:
                pass

    def selected_text(self):
        d = self.calendar.selectedDate()
        return d.toString("dd-MM-yyyy")

class CurrencyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("0,00")
        self.editingFinished.connect(self._format_text)

    def _format_text(self):
        txt = self.text().strip()
        if txt == "":
            return
        try:
            val = float(txt.replace(".", "").replace(",", "."))
            self.setText(br_number(val, 2))
        except Exception:
            pass

class PercentLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("0,0000")
        self.editingFinished.connect(self._format_text)

    def _format_text(self):
        txt = self.text().strip()
        if txt == "":
            return
        try:
            val = float(txt.replace(".", "").replace(",", "."))
            if val < 0:
                val = 0
            if val > 100:
                val = 100
            self.setText(br_number(val, 4))
        except Exception:
            pass
