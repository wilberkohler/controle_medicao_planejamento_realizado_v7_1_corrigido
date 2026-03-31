from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QTableWidget, QComboBox, QMessageBox
from ui.widgets.common import configure_table
from ui.widgets.table_items import IntegerItem, TextItem
from ui.widgets.advanced_widgets import DateFieldWidget
from ui.widgets.input_widgets import DateLineEdit

class WorkflowView(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        root = QHBoxLayout(self)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Workflow de aprovação"))

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["ID", "Módulo", "Registro", "Status", "Solicitante", "Aprovador", "Data Solic.", "Data Aprov."])
        configure_table(self.table)
        left_layout.addWidget(self.table)
        root.addWidget(left, 2)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("Criar fluxo"))

        form = QFormLayout()
        self.ed_modulo = QLineEdit()
        self.ed_registro = QLineEdit()
        self.cb_status = QComboBox()
        self.cb_status.addItems(["rascunho", "em_aprovacao", "aprovado", "rejeitado"])
        self.cb_solicitante = QComboBox()
        self.cb_aprovador = QComboBox()
        self.ed_data_solic = DateLineEdit()
        self.ed_data_aprov = DateLineEdit()
        self.ed_coment = QTextEdit()

        form.addRow("Módulo:", self.ed_modulo)
        form.addRow("Registro ID:", self.ed_registro)
        form.addRow("Status:", self.cb_status)
        form.addRow("Solicitante:", self.cb_solicitante)
        form.addRow("Aprovador:", self.cb_aprovador)
        form.addRow("Data solicitação:", DateFieldWidget(self.ed_data_solic))
        form.addRow("Data aprovação:", DateFieldWidget(self.ed_data_aprov))
        form.addRow("Comentário:", self.ed_coment)
        right_layout.addLayout(form)

        self.btn_salvar = QPushButton("Salvar workflow")
        self.btn_salvar.clicked.connect(self.salvar)
        right_layout.addWidget(self.btn_salvar)
        right_layout.addStretch()
        root.addWidget(right, 1)

    def reload_data(self):
        usuarios = self.service.usuarios()
        for cb in [self.cb_solicitante, self.cb_aprovador]:
            current = cb.currentData()
            cb.clear()
            cb.addItem("Nenhum", None)
            for u in usuarios:
                cb.addItem(f"{u['id']} - {u['nome']} - {u['perfil']}", u["id"])
            idx = cb.findData(current)
            cb.setCurrentIndex(idx if idx >= 0 else 0)

        rows = self.service.list_all()
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, IntegerItem(row["id"]))
            self.table.setItem(r, 1, TextItem(row["modulo"]))
            self.table.setItem(r, 2, IntegerItem(row["registro_id"]))
            self.table.setItem(r, 3, TextItem(row["status"]))
            self.table.setItem(r, 4, TextItem(row["solicitante_nome"] or ""))
            self.table.setItem(r, 5, TextItem(row["aprovador_nome"] or ""))
            self.table.setItem(r, 6, TextItem(row["data_solicitacao"] or ""))
            self.table.setItem(r, 7, TextItem(row["data_aprovacao"] or ""))
        self.table.setSortingEnabled(True)

    def salvar(self):
        try:
            self.service.create({
                "modulo": self.ed_modulo.text(),
                "registro_id": self.ed_registro.text(),
                "status": self.cb_status.currentText(),
                "usuario_solicitante_id": self.cb_solicitante.currentData(),
                "usuario_aprovador_id": self.cb_aprovador.currentData(),
                "data_solicitacao": self.ed_data_solic.text(),
                "data_aprovacao": self.ed_data_aprov.text(),
                "comentario": self.ed_coment.toPlainText(),
            })
            QMessageBox.information(self, "Sucesso", "Workflow salvo com sucesso.")
            self.ed_modulo.clear()
            self.ed_registro.clear()
            self.ed_data_solic.clear()
            self.ed_data_aprov.clear()
            self.ed_coment.clear()
            self.reload_data()
        except Exception as exc:
            QMessageBox.warning(self, "Atenção", str(exc))
