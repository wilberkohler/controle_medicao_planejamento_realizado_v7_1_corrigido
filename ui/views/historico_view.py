from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QTableWidget, QComboBox, QMessageBox
from ui.widgets.common import configure_table
from ui.widgets.table_items import IntegerItem, TextItem
from ui.views.base_mixins import FilterMixin

class HistoricoView(QWidget, FilterMixin):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        root = QHBoxLayout(self)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Histórico de alterações"))

        self.ed_filtro = QLineEdit()
        self.ed_filtro.setPlaceholderText("Pesquisar tabela, ação, usuário ou resumo...")
        self.ed_filtro.textChanged.connect(self.after_filter)
        left_layout.addWidget(self.ed_filtro)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["ID", "Tabela", "Registro", "Ação", "Usuário", "Resumo", "Workflow", "Data"])
        configure_table(self.table)
        left_layout.addWidget(self.table)
        root.addWidget(left, 2)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("Lançamento manual de histórico"))

        form = QFormLayout()
        self.ed_tabela = QLineEdit()
        self.ed_registro = QLineEdit()
        self.ed_acao = QLineEdit()
        self.cb_usuario = QComboBox()
        self.ed_resumo = QTextEdit()
        self.ed_workflow = QLineEdit()

        form.addRow("Tabela:", self.ed_tabela)
        form.addRow("Registro ID:", self.ed_registro)
        form.addRow("Ação:", self.ed_acao)
        form.addRow("Usuário:", self.cb_usuario)
        form.addRow("Resumo:", self.ed_resumo)
        form.addRow("Workflow:", self.ed_workflow)
        right_layout.addLayout(form)

        self.btn_salvar = QPushButton("Salvar histórico")
        self.btn_salvar.clicked.connect(self.salvar)
        right_layout.addWidget(self.btn_salvar)
        right_layout.addStretch()
        root.addWidget(right, 1)

    def reload_data(self):
        cur = self.cb_usuario.currentData()
        self.cb_usuario.clear()
        self.cb_usuario.addItem("Nenhum", None)
        for u in self.service.usuarios():
            self.cb_usuario.addItem(f"{u['id']} - {u['nome']}", u["id"])
        idx = self.cb_usuario.findData(cur)
        self.cb_usuario.setCurrentIndex(idx if idx >= 0 else 0)

        rows = self.service.list_all()
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, IntegerItem(row["id"]))
            self.table.setItem(r, 1, TextItem(row["tabela"]))
            self.table.setItem(r, 2, IntegerItem(row["registro_id"]))
            self.table.setItem(r, 3, TextItem(row["acao"]))
            self.table.setItem(r, 4, TextItem(row["usuario_nome"] or ""))
            self.table.setItem(r, 5, TextItem(row["resumo"] or ""))
            self.table.setItem(r, 6, TextItem(row["workflow_status"] or ""))
            self.table.setItem(r, 7, TextItem(row["created_at"] or ""))
        self.table.setSortingEnabled(True)
        self.after_filter()

    def after_filter(self):
        self.apply_text_filter(self.table, self.ed_filtro.text())

    def salvar(self):
        try:
            self.service.create({
                "tabela": self.ed_tabela.text(),
                "registro_id": self.ed_registro.text(),
                "acao": self.ed_acao.text(),
                "usuario_id": self.cb_usuario.currentData(),
                "resumo": self.ed_resumo.toPlainText(),
                "workflow_status": self.ed_workflow.text(),
            })
            QMessageBox.information(self, "Sucesso", "Histórico salvo com sucesso.")
            self.ed_tabela.clear()
            self.ed_registro.clear()
            self.ed_acao.clear()
            self.ed_resumo.clear()
            self.ed_workflow.clear()
            self.reload_data()
        except Exception as exc:
            QMessageBox.warning(self, "Atenção", str(exc))
