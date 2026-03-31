from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSplitter, QTableWidget, QComboBox, QMessageBox
from ui.widgets.common import configure_table, status_labels_layout
from ui.widgets.table_items import IntegerItem, TextItem
from ui.views.base_mixins import FilterMixin

class UsuariosView(QWidget, FilterMixin):
    data_changed = Signal()

    def __init__(self, service):
        super().__init__()
        self.service = service
        self.current_id = None
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        root = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        root.addWidget(splitter)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Usuários"))

        self.ed_filtro = QLineEdit()
        self.ed_filtro.setPlaceholderText("Pesquisar nome, email ou perfil...")
        self.ed_filtro.textChanged.connect(self.after_filter)
        left_layout.addWidget(self.ed_filtro)

        self.cb_ativo_filtro = QComboBox()
        self.cb_ativo_filtro.addItems(["Todos", "Ativos", "Inativos"])
        self.cb_ativo_filtro.currentIndexChanged.connect(self.reload_data)
        left_layout.addWidget(self.cb_ativo_filtro)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Email", "Perfil", "Ativo"])
        configure_table(self.table)
        self.table.itemSelectionChanged.connect(self.on_select)
        left_layout.addWidget(self.table)

        status_layout, labels = status_labels_layout()
        self.lbl_reg, self.lbl_1, self.lbl_2, self.lbl_f = labels
        left_layout.addLayout(status_layout)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("Cadastro / edição"))

        form = QFormLayout()
        self.ed_nome = QLineEdit()
        self.ed_email = QLineEdit()
        self.cb_perfil = QComboBox()
        self.cb_perfil.addItems(["administrador", "gestor", "aprovador", "lancador", "consulta"])
        self.cb_ativo = QComboBox()
        self.cb_ativo.addItems(["Sim", "Não"])
        self.ed_obs = QTextEdit()

        form.addRow("Nome:", self.ed_nome)
        form.addRow("Email:", self.ed_email)
        form.addRow("Perfil:", self.cb_perfil)
        form.addRow("Ativo:", self.cb_ativo)
        form.addRow("Observações:", self.ed_obs)
        right_layout.addLayout(form)

        buttons = QHBoxLayout()
        self.btn_novo = QPushButton("Novo")
        self.btn_salvar = QPushButton("Salvar")
        self.btn_excluir = QPushButton("Excluir")
        self.btn_limpar = QPushButton("Limpar")
        self.btn_novo.clicked.connect(self.novo)
        self.btn_salvar.clicked.connect(self.salvar)
        self.btn_excluir.clicked.connect(self.excluir)
        self.btn_limpar.clicked.connect(self.limpar)
        for b in [self.btn_novo, self.btn_salvar, self.btn_excluir, self.btn_limpar]:
            buttons.addWidget(b)
        right_layout.addLayout(buttons)
        right_layout.addStretch()

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([850, 500])

    def reload_data(self):
        rows = self.service.list_all()
        filtro = self.cb_ativo_filtro.currentText()
        if filtro == "Ativos":
            rows = [r for r in rows if int(r["ativo"] or 0) == 1]
        elif filtro == "Inativos":
            rows = [r for r in rows if int(r["ativo"] or 0) == 0]

        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, IntegerItem(row["id"]))
            self.table.setItem(r, 1, TextItem(row["nome"]))
            self.table.setItem(r, 2, TextItem(row["email"]))
            self.table.setItem(r, 3, TextItem(row["perfil"]))
            self.table.setItem(r, 4, TextItem("Sim" if int(row["ativo"] or 0) == 1 else "Não"))
        self.table.setSortingEnabled(True)

        self.lbl_1.setText(f"Usuários: {len(rows)}")
        self.lbl_2.setText(f"Filtro: {filtro}")
        self.after_filter()

    def after_filter(self):
        self.apply_text_filter(self.table, self.ed_filtro.text())
        visible = sum(1 for r in range(self.table.rowCount()) if not self.table.isRowHidden(r))
        self.lbl_reg.setText(f"Registros: {visible} / {self.table.rowCount()}")
        self.lbl_f.setText("Filtro texto: sim" if self.ed_filtro.text().strip() else "Filtro texto: não")

    def on_select(self):
        items = self.table.selectedItems()
        if not items:
            return
        row = items[0].row()
        self.current_id = int(self.table.item(row, 0).text())
        obj = self.service.get_by_id(self.current_id)
        if obj is None:
            return
        self.ed_nome.setText(obj["nome"] or "")
        self.ed_email.setText(obj["email"] or "")
        idx = self.cb_perfil.findText(obj["perfil"] or "")
        self.cb_perfil.setCurrentIndex(idx if idx >= 0 else 0)
        self.cb_ativo.setCurrentIndex(0 if int(obj["ativo"] or 0) == 1 else 1)
        self.ed_obs.setPlainText(obj["observacoes"] or "")

    def get_data(self):
        return {
            "nome": self.ed_nome.text(),
            "email": self.ed_email.text(),
            "perfil": self.cb_perfil.currentText(),
            "ativo": self.cb_ativo.currentText(),
            "observacoes": self.ed_obs.toPlainText(),
        }

    def novo(self):
        self.current_id = None
        self.limpar()

    def limpar(self):
        self.ed_nome.clear()
        self.ed_email.clear()
        self.cb_perfil.setCurrentIndex(0)
        self.cb_ativo.setCurrentIndex(0)
        self.ed_obs.clear()
        self.table.clearSelection()

    def salvar(self):
        try:
            data = self.get_data()
            if self.current_id is None:
                self.service.create(data)
            else:
                self.service.update(self.current_id, data)
            QMessageBox.information(self, "Sucesso", "Operação realizada com sucesso.")
            self.current_id = None
            self.limpar()
            self.reload_data()
            self.data_changed.emit()
        except Exception as exc:
            QMessageBox.warning(self, "Atenção", str(exc))

    def excluir(self):
        if self.current_id is None:
            QMessageBox.information(self, "Excluir", "Selecione um usuário para excluir.")
            return
        ok = QMessageBox.question(self, "Confirmar exclusão", "Deseja realmente excluir este usuário?")
        if ok != QMessageBox.Yes:
            return
        try:
            self.service.delete(self.current_id)
            QMessageBox.information(self, "Sucesso", "Usuário excluído com sucesso.")
            self.current_id = None
            self.limpar()
            self.reload_data()
            self.data_changed.emit()
        except Exception as exc:
            QMessageBox.warning(self, "Atenção", str(exc))
