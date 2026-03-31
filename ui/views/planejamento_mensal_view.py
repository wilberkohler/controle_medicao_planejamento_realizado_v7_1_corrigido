from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSplitter, QTableWidget, QMessageBox
from ui.widgets.common import configure_table, status_labels_layout
from ui.widgets.table_items import IntegerItem, TextItem, CurrencyItem, FloatItem
from ui.views.base_mixins import FilterMixin
from ui.widgets.advanced_widgets import SearchableComboBox
from ui.widgets.input_widgets import CurrencyLineEdit, PercentLineEdit

class PlanejamentoMensalView(QWidget, FilterMixin):
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
        left_layout.addWidget(QLabel("Planejamento Mensal"))
        self.ed_filtro = QLineEdit()
        self.ed_filtro.setPlaceholderText("Pesquisar...")
        self.ed_filtro.textChanged.connect(self.after_filter)
        left_layout.addWidget(self.ed_filtro)
        self.cb_contrato_filtro = SearchableComboBox()
        self.cb_contrato_filtro.currentIndexChanged.connect(self.reload_data)
        left_layout.addWidget(self.cb_contrato_filtro)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Contrato", "Versão", "Competência", "Entregável", "Valor Prev.", "% Prev."])
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
        self.cb_contrato.currentIndexChanged.connect(self.on_contrato_changed)
        self.cb_plan = SearchableComboBox()
        self.cb_item = SearchableComboBox()
        self.cb_item.currentIndexChanged.connect(self.on_item_changed)
        self.ed_comp = QLineEdit()
        self.ed_valor = CurrencyLineEdit()
        self.ed_percentual = PercentLineEdit()
        self.ed_obs = QTextEdit()
        form.addRow("Contrato:", self.cb_contrato)
        form.addRow("Planejamento:", self.cb_plan)
        form.addRow("Item:", self.cb_item)
        form.addRow("Competência:", self.ed_comp)
        form.addRow("Valor previsto mês:", self.ed_valor)
        form.addRow("% previsto mês:", self.ed_percentual)
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

    def _reload_contratos(self):
        contracts = self.service.contratos()
        curf = self.cb_contrato_filtro.currentData()
        self.cb_contrato_filtro.blockSignals(True)
        self.cb_contrato_filtro.clear()
        self.cb_contrato_filtro.addItem("Todos", None)
        for c in contracts:
            self.cb_contrato_filtro.addItem(f"{c['codigo']} - {c['nome']}", c["id"])
        idx = self.cb_contrato_filtro.findData(curf)
        self.cb_contrato_filtro.setCurrentIndex(idx if idx >= 0 else 0)
        self.cb_contrato_filtro.blockSignals(False)

        cur = self.cb_contrato.currentData()
        self.cb_contrato.blockSignals(True)
        self.cb_contrato.clear()
        for c in contracts:
            self.cb_contrato.addItem(f"{c['codigo']} - {c['nome']}", c["id"])
        idx2 = self.cb_contrato.findData(cur)
        self.cb_contrato.setCurrentIndex(idx2 if idx2 >= 0 and self.cb_contrato.count() > 0 else 0)
        self.cb_contrato.blockSignals(False)

    def on_contrato_changed(self):
        cid = self.cb_contrato.currentData()
        cur_plan = self.cb_plan.currentData()
        self.cb_plan.clear()
        if cid:
            for p in self.service.planejamentos(cid):
                self.cb_plan.addItem(f"v{p['versao']} - {p.get('descricao_versao','')}", p["id"])
        idx = self.cb_plan.findData(cur_plan)
        self.cb_plan.setCurrentIndex(idx if idx >= 0 and self.cb_plan.count() > 0 else 0)
        self._reload_items()

    def _reload_items(self):
        pid = self.cb_plan.currentData()
        cur = self.cb_item.currentData()
        self.cb_item.clear()
        if pid:
            for it in self.service.itens(pid):
                txt = f"ID {it['id']} - Entregável {it['entregavel_id']}"
                self.cb_item.addItem(txt, it["id"])
        idx = self.cb_item.findData(cur)
        self.cb_item.setCurrentIndex(idx if idx >= 0 and self.cb_item.count() > 0 else 0)

    def on_item_changed(self):
        pass

    def reload_data(self):
        self._reload_contratos()
        self.on_contrato_changed()
        rows = self.service.list_all()
        if self.cb_contrato_filtro.currentData():
            rows = [r for r in rows if r["contrato_id"] == self.cb_contrato_filtro.currentData()]
        self.table.setRowCount(0)
        total = 0.0
        for row in rows:
            total += float(row["valor_previsto_mes"] or 0)
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, IntegerItem(row["id"]))
            self.table.setItem(r, 1, TextItem(row["contrato_codigo"]))
            self.table.setItem(r, 2, TextItem(f"v{row['versao']}"))
            self.table.setItem(r, 3, TextItem(row["competencia"]))
            self.table.setItem(r, 4, TextItem(row["entregavel_codigo"]))
            self.table.setItem(r, 5, CurrencyItem(row["valor_previsto_mes"]))
            self.table.setItem(r, 6, FloatItem(row["percentual_previsto_mes"], 2))
        self.lbl_1.setText(f"Valor total: {total:,.2f}")
        self.lbl_2.setText(f"Total: {len(rows)}")
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
        self.on_contrato_changed()
        self._reload_items()
        idx_item = self.cb_item.findData(obj["planejamento_item_id"])
        self.cb_item.setCurrentIndex(idx_item if idx_item >= 0 else 0)
        self.ed_comp.setText(obj["competencia"] or "")
        self.ed_valor.setText(str(obj["valor_previsto_mes"] or ""))
        self.ed_percentual.setText(str(obj["percentual_previsto_mes"] or ""))
        self.ed_obs.setPlainText(obj["observacoes"] or "")

    def get_data(self):
        item_id = self.cb_item.currentData() or 0
        return {
            "planejamento_item_id": item_id,
            "contrato_id": self.cb_contrato.currentData() or 0,
            "etapa_id": 0,
            "grupo_id": 0,
            "entregavel_id": 0,
            "competencia": self.ed_comp.text(),
            "valor_previsto_mes": self.ed_valor.text(),
            "percentual_previsto_mes": self.ed_percentual.text(),
            "observacoes": self.ed_obs.toPlainText(),
        }

    def salvar(self):
        # enrich etapa/grupo/entregavel from selected item
        item_id = self.cb_item.currentData() or 0
        item = None
        if item_id:
            item = self.service.item_repo.get_by_id(item_id) if hasattr(self.service, "item_repo") else None
        data = self.get_data()
        if item:
            data["etapa_id"] = item["etapa_id"]
            data["grupo_id"] = item["grupo_id"]
            data["entregavel_id"] = item["entregavel_id"]
        try:
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

    def novo(self):
        self.current_id = None
        self.limpar()

    def limpar(self):
        self.table.clearSelection()
        if self.cb_contrato.count() > 0:
            self.cb_contrato.setCurrentIndex(0)
        self.on_contrato_changed()
        self.ed_comp.clear()
        self.ed_valor.clear()
        self.ed_percentual.clear()
        self.ed_obs.clear()

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
