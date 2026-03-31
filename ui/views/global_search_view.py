from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget
from ui.widgets.common import configure_table
from ui.widgets.table_items import TextItem

class GlobalSearchView(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        self.lbl = QLabel('Busca global')
        self.lbl.setStyleSheet('font-size:18px; font-weight:700;')
        root.addWidget(self.lbl)
        self.table = QTableWidget(0,4)
        self.table.setHorizontalHeaderLabels(['Tipo','Referência','Detalhe','Extra'])
        configure_table(self.table)
        root.addWidget(self.table)

    def perform_search(self, q):
        self.lbl.setText(f"Busca global: {q}")
        rows = self.service.global_search(q) if str(q).strip() else []
        self.table.setRowCount(0)
        for row in rows:
            r=self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r,0,TextItem(row['tipo']))
            self.table.setItem(r,1,TextItem(row['referencia']))
            self.table.setItem(r,2,TextItem(row['detalhe']))
            self.table.setItem(r,3,TextItem(row['extra']))
