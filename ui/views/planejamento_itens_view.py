from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSplitter, QTableWidget, QMessageBox
from ui.widgets.common import configure_table, status_labels_layout
from ui.widgets.table_items import IntegerItem, TextItem, CurrencyItem, FloatItem
from ui.views.base_mixins import FilterMixin
from ui.widgets.advanced_widgets import SearchableComboBox
from ui.widgets.input_widgets import CurrencyLineEdit, PercentLineEdit

class PlanejamentoItensView(QWidget, FilterMixin):
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
        left_layout.addWidget(QLabel("Planejamento - Itens"))
        self.ed_filtro = QLineEdit()
        self.ed_filtro.setPlaceholderText("Pesquisar...")
        self.ed_filtro.textChanged.connect(self.after_filter)
        left_layout.addWidget(self.ed_filtro)
        self.cb_contrato_filtro = SearchableComboBox()
        self.cb_contrato_filtro.currentIndexChanged.connect(self.reload_data)
        left_layout.addWidget(self.cb_contrato_filtro)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Contrato", "Versão", "Entregável", "Valor Prev.", "% Prev.", "Obs."])
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
        self.cb_etapa = SearchableComboBox()
        self.cb_etapa.currentIndexChanged.connect(self.on_etapa_changed)
        self.cb_grupo = SearchableComboBox()
        self.cb_grupo.currentIndexChanged.connect(self.on_grupo_changed)
        self.cb_entregavel = SearchableComboBox()
        self.ed_valor = CurrencyLineEdit()
        self.ed_percentual = PercentLineEdit()
        self.ed_obs = QTextEdit()
        form.addRow("Contrato:", self.cb_contrato)
        form.addRow("Planejamento:", self.cb_plan)
        form.addRow("Etapa:", self.cb_etapa)
        form.addRow("Grupo:", self.cb_grupo)
        form.addRow("Entregável:", self.cb_entregavel)
        form.addRow("Valor previsto total:", self.ed_valor)
        form.addRow("% previsto total:", self.ed_percentual)
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
        cur_etapa = self.cb_etapa.currentData()
        self.cb_plan.clear()
        self.cb_etapa.clear()
        if cid:
            for p in self.service.planejamentos(cid):
                self.cb_plan.addItem(f"v{p['versao']} - {p.get('descricao_versao','')}", p["id"])
            for e in self.service.etapas(cid):
                self.cb_etapa.addItem(f"{e['codigo']} - {e['descricao']}", e["id"])
        idxp = self.cb_plan.findData(cur_plan)
        self.cb_plan.setCurrentIndex(idxp if idxp >= 0 and self.cb_plan.count() > 0 else 0)
        idxe = self.cb_etapa.findData(cur_etapa)
        self.cb_etapa.setCurrentIndex(idxe if idxe >= 0 and self.cb_etapa.count() > 0 else 0)
        self.on_etapa_changed()

    def on_etapa_changed(self):
        eid = self.cb_etapa.currentData()
        cur = self.cb_grupo.currentData()
        self.cb_grupo.clear()
        if eid:
            for g in self.service.grupos(eid):
                self.cb_grupo.addItem(f"{g['codigo']} - {g['descricao']}", g["id"])
        idx = self.cb_grupo.findData(cur)
        self.cb_grupo.setCurrentIndex(idx if idx >= 0 and self.cb_grupo.count() > 0 else 0)
        self.on_grupo_changed()

    def on_grupo_changed(self):
        gid = self.cb_grupo.currentData()
        cur = self.cb_entregavel.currentData()
        self.cb_entregavel.clear()
        if gid:
            for ent in self.service.entregaveis(gid):
                self.cb_entregavel.addItem(f"{ent['codigo']} - {ent['descricao']}", ent["id"])
        idx = self.cb_entregavel.findData(cur)
        self.cb_entregavel.setCurrentIndex(idx if idx >= 0 and self.cb_entregavel.count() > 0 else 0)

    def reload_data(self):
        self._reload_contratos()
        self.on_contrato_changed()
        rows = self.service.list_all()
        if self.cb_contrato_filtro.currentData():
            rows = [r for r in rows if r["contrato_id"] == self.cb_contrato_filtro.currentData()]
        self.table.setRowCount(0)
        total = 0.0
        for row in rows:
            total += float(row["valor_previsto_total"] or 0)
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, IntegerItem(row["id"]))
            self.table.setItem(r, 1, TextItem(row["contrato_codigo"]))
            self.table.setItem(r, 2, TextItem(f"v{row['versao']}"))
            self.table.setItem(r, 3, TextItem(f"{row['entregavel_codigo']} - {row['entregavel_descricao']}"))
            self.table.setItem(r, 4, CurrencyItem(row["valor_previsto_total"]))
            self.table.setItem(r, 5, FloatItem(row["percentual_previsto_total"], 2))
            self.table.setItem(r, 6, TextItem(row["observacoes"] or ""))
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
        idxp = self.cb_plan.findData(obj["planejamento_id"])
        self.cb_plan.setCurrentIndex(idxp if idxp >= 0 else 0)
        idxe = self.cb_etapa.findData(obj["etapa_id"])
        self.cb_etapa.setCurrentIndex(idxe if idxe >= 0 else 0)
        self.on_etapa_changed()
        idxg = self.cb_grupo.findData(obj["grupo_id"])
        self.cb_grupo.setCurrentIndex(idxg if idxg >= 0 else 0)
        self.on_grupo_changed()
        idxent = self.cb_entregavel.findData(obj["entregavel_id"])
        self.cb_entregavel.setCurrentIndex(idxent if idxent >= 0 else 0)
        self.ed_valor.setText(str(obj["valor_previsto_total"] or ""))
        self.ed_percentual.setText(str(obj["percentual_previsto_total"] or ""))
        self.ed_obs.setPlainText(obj["observacoes"] or "")

    def get_data(self):
        return {
            "planejamento_id": self.cb_plan.currentData() or 0,
            "contrato_id": self.cb_contrato.currentData() or 0,
            "etapa_id": self.cb_etapa.currentData() or 0,
            "grupo_id": self.cb_grupo.currentData() or 0,
            "entregavel_id": self.cb_entregavel.currentData() or 0,
            "valor_previsto_total": self.ed_valor.text(),
            "percentual_previsto_total": self.ed_percentual.text(),
            "observacoes": self.ed_obs.toPlainText(),
        }

    def novo(self):
        self.current_id = None
        self.limpar()

    def limpar(self):
        self.table.clearSelection()
        if self.cb_contrato.count() > 0:
            self.cb_contrato.setCurrentIndex(0)
        self.on_contrato_changed()
        self.ed_valor.clear()
        self.ed_percentual.clear()
        self.ed_obs.clear()

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
