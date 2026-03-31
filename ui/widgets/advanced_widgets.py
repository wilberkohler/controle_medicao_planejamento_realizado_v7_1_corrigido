from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QComboBox, QCompleter
)
from PySide6.QtCore import Qt, QStringListModel
from ui.widgets.input_widgets import CalendarDialog

class SearchableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.setMaxVisibleItems(20)
        self.setFocusPolicy(Qt.StrongFocus)
        self.completer_obj = QCompleter(self)
        self.completer_obj.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer_obj.setFilterMode(Qt.MatchContains)
        self.setCompleter(self.completer_obj)

    def refresh_completer(self):
        items = [self.itemText(i) for i in range(self.count())]
        self.completer_obj.setModel(QStringListModel(items, self.completer_obj))

    def addItem(self, text, userData=None):
        super().addItem(text, userData)
        self.refresh_completer()

    def addItems(self, texts):
        super().addItems(texts)
        self.refresh_completer()

    def clear(self):
        super().clear()
        self.refresh_completer()

class DateFieldWidget(QWidget):
    def __init__(self, line_edit, parent=None):
        super().__init__(parent)
        self.line_edit = line_edit
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.line_edit)
        self.btn = QPushButton("📅")
        self.btn.setMaximumWidth(34)
        self.btn.clicked.connect(self.select_date)
        layout.addWidget(self.btn)

    def select_date(self):
        dlg = CalendarDialog(self)
        dlg.set_date_text(self.line_edit.text())
        if dlg.exec():
            self.line_edit.setText(dlg.selected_text())
