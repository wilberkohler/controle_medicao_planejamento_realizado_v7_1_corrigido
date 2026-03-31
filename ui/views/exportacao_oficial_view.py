from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QTableWidget
import csv
from ui.widgets.common import configure_table
from ui.widgets.table_items import TextItem

class ExportacaoOficialView(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.payload = {}
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        title = QLabel("Exportação Financeira Oficial")
        title.setStyleSheet("font-size:18px;font-weight:700;")
        root.addWidget(title)
        info = QLabel("Exportações baseadas na camada oficial importada: ano vigente, próximos 12 meses e forecast anual.")
        info.setWordWrap(True)
        root.addWidget(info)

        bar = QHBoxLayout()
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self.reload_data)
        self.btn_exportar_csv = QPushButton("Exportar CSVs oficiais")
        self.btn_exportar_csv.clicked.connect(self.exportar_csvs)
        bar.addWidget(self.btn_atualizar)
        bar.addWidget(self.btn_exportar_csv)
        bar.addStretch()
        root.addLayout(bar)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Arquivo lógico", "Quantidade de linhas"])
        configure_table(self.table)
        root.addWidget(self.table)

    def reload_data(self):
        self.payload = self.service.pacote_oficial_dict()
        self.table.setRowCount(0)
        for name, rows in self.payload.items():
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, TextItem(name))
            self.table.setItem(r, 1, TextItem(str(len(rows))))

    def exportar_csvs(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar pasta de exportação")
        if not folder:
            return
        try:
            for name, rows in self.payload.items():
                path = f"{folder}/{name}.csv"
                with open(path, "w", newline="", encoding="utf-8-sig") as f:
                    if rows:
                        headers = list(rows[0].keys())
                        w = csv.writer(f, delimiter=";")
                        w.writerow(headers)
                        for row in rows:
                            w.writerow([row.get(h, "") for h in headers])
                    else:
                        f.write("Sem dados\n")
            QMessageBox.information(self, "Sucesso", "Arquivos oficiais exportados.")
        except Exception as exc:
            QMessageBox.warning(self, "Erro", str(exc))
