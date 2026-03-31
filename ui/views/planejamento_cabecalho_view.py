from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSplitter, QTableWidget, QMessageBox
from ui.widgets.common import configure_table, status_labels_layout, apply_int_validator
from ui.widgets.table_items import IntegerItem, TextItem, DateItem
from ui.views.base_mixins import FilterMixin
from ui.widgets.advanced_widgets import SearchableComboBox, DateFieldWidget
from ui.widgets.input_widgets import DateLineEdit

class PlanejamentoCabecalhoView(QWidget, FilterMixin):
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
        left_layout.addWidget(QLabel("Planejamento"))
        self.ed_filtro = QLineEdit()
        self.ed_filtro.setPlaceholderText("Pesquisar...")
        self.ed_filtro.textChanged.connect(self.after_filter)
        left_layout.addWidget(self.ed_filtro)
        self.cb_contrato_filtro = SearchableComboBox()
        self.cb_contrato_filtro.currentIndexChanged.connect(self.reload_data)
        left_layout.addWidget(self.cb_contrato_filtro)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Contrato", "Versão", "Data Base", "Status", "Descrição"])
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
        self.cb_contrato = SearchableComboBox()
        self.ed_versao = QLineEdit()
        apply_int_validator(self.ed_versao)
        self.ed_desc = QLineEdit()
        self.ed_data = DateLineEdit()
        self.cb_status = SearchableComboBox()
        self.cb_status.addItems(["rascunho", "aprovado", "cancelado"])
        self.ed_motivo = QTextEdit()
        self.ed_obs = QTextEdit()
        form.addRow("Contrato:", self.cb_contrato)
        form.addRow("Versão:", self.ed_versao)
        form.addRow("Descrição da versão:", self.ed_desc)
        form.addRow("Data base:", DateFieldWidget(self.ed_data))
        form.addRow("Status:", self.cb_status)
        form.addRow("Motivo da revisão:", self.ed_motivo)
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
        splitter.setSizes([980, 520])

    def reload_data(self):
        contracts = self.service.contratos()
        cur = self.cb_contrato_filtro.currentData()
        self.cb_contrato_filtro.blockSignals(True)
        self.cb_contrato_filtro.clear()
        self.cb_contrato_filtro.addItem("Todos", None)
        for c in contracts:
            self.cb_contrato_filtro.addItem(f"{c['codigo']} - {c['nome']}", c["id"])
        idx = self.cb_contrato_filtro.findData(cur)
        self.cb_contrato_filtro.setCurrentIndex(idx if idx >= 0 else 0)
        self.cb_contrato_filtro.blockSignals(False)

        sel = self.cb_contrato.currentData()
        self.cb_contrato.clear()
        for c in contracts:
            self.cb_contrato.addItem(f"{c['codigo']} - {c['nome']}", c["id"])
        idx2 = self.cb_contrato.findData(sel)
        self.cb_contrato.setCurrentIndex(idx2 if idx2 >= 0 and self.cb_contrato.count() > 0 else 0)

        rows = self.service.list_all()
        if self.cb_contrato_filtro.currentData():
            rows = [r for r in rows if r["contrato_id"] == self.cb_contrato_filtro.currentData()]
        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, IntegerItem(row["id"]))
            self.table.setItem(r, 1, TextItem(f"{row['contrato_codigo']} - {row['contrato_nome']}"))
            self.table.setItem(r, 2, IntegerItem(row["versao"]))
            self.table.setItem(r, 3, DateItem(row["data_base"] or ""))
            self.table.setItem(r, 4, TextItem(row["status"] or ""))
            self.table.setItem(r, 5, TextItem(row["descricao_versao"] or ""))
        self.lbl_1.setText(f"Total: {len(rows)}")
        self.lbl_2.setText(f"Filtro contrato: {self.cb_contrato_filtro.currentText()}")
        self.after_filter()

    def after_filter(self):
        self.apply_text_filter(self.table, self.ed_filtro.text())
        visible = sum(1 for r in range(self.table.rowCount()) if not self.table.isRowHidden(r))
        self.lbl_reg.setText(f"Registros: {visible} / {self.table.rowCount()}")
        self.lbl_f.setText("Filtro: sim" if self.ed_filtro.text().strip() else "Filtro: não")

    def on_select(self):
        items = self.table.selectedItems()
        if not items:
            return
        self.current_id = int(self.table.item(items[0].row(), 0).text())
        obj = self.service.get_by_id(self.current_id)
        idx = self.cb_contrato.findData(obj["contrato_id"])
        self.cb_contrato.setCurrentIndex(idx if idx >= 0 else 0)
        self.ed_versao.setText(str(obj["versao"] or ""))
        self.ed_desc.setText(obj["descricao_versao"] or "")
        self.ed_data.setText(obj["data_base"] or "")
        idxs = self.cb_status.findText(obj["status"] or "")
        self.cb_status.setCurrentIndex(idxs if idxs >= 0 else 0)
        self.ed_motivo.setPlainText(obj["motivo_revisao"] or "")
        self.ed_obs.setPlainText(obj["observacoes"] or "")

    def get_data(self):
        return {
            "contrato_id": self.cb_contrato.currentData() or 0,
            "versao": self.ed_versao.text(),
            "descricao_versao": self.ed_desc.text(),
            "data_base": self.ed_data.text(),
            "status": self.cb_status.currentText(),
            "motivo_revisao": self.ed_motivo.toPlainText(),
            "observacoes": self.ed_obs.toPlainText(),
        }

    def novo(self):
        self.current_id = None
        self.limpar()

    def limpar(self):
        self.table.clearSelection()
        self.ed_versao.clear()
        self.ed_desc.clear()
        self.ed_data.clear()
        self.ed_motivo.clear()
        self.ed_obs.clear()
        if self.cb_contrato.count() > 0:
            self.cb_contrato.setCurrentIndex(0)
        self.cb_status.setCurrentIndex(0)

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
            QMessageBox.information(self, "Excluir", "Selecione um registro para excluir.")
            return
        if QMessageBox.question(self, "Confirmar exclusão", "Deseja realmente excluir este registro?") != QMessageBox.Yes:
            return
        try:
            self.service.delete(self.current_id)
            QMessageBox.information(self, "Sucesso", "Registro excluído com sucesso.")
            self.current_id = None
            self.limpar()
            self.reload_data()
            self.data_changed.emit()
        except Exception as exc:
            QMessageBox.warning(self, "Atenção", str(exc))
