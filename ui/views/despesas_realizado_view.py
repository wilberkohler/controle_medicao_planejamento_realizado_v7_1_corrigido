from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSplitter, QTableWidget, QMessageBox
from ui.widgets.common import configure_table
from ui.widgets.table_items import IntegerItem, TextItem, CurrencyItem
from ui.widgets.advanced_widgets import SearchableComboBox
from ui.views.base_mixins import FilterMixin

CATEGORIAS = ["Viagens","Combustível","Hospedagem","Alimentação","Software","Plotagem","Impressões","Veículos","Passagens","Taxas","Cartório","Outros"]

class DespesasRealizadoView(QWidget, FilterMixin):
    data_changed = Signal()
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.current_id = None
        self._build_ui()
        self.reload_data()
    def _build_ui(self):
        root = QHBoxLayout(self); splitter = QSplitter(Qt.Horizontal); root.addWidget(splitter)
        left = QWidget(); ll = QVBoxLayout(left)
        ll.addWidget(QLabel("Despesas - Realizado"))
        self.ed_filtro = QLineEdit(); self.ed_filtro.setPlaceholderText("Pesquisar..."); self.ed_filtro.textChanged.connect(self.after_filter); ll.addWidget(self.ed_filtro)
        self.table = QTableWidget(0,9); self.table.setHorizontalHeaderLabels(["ID","Contrato","Competência","Categoria","Descrição","Fornecedor","Valor Real.","Doc.","Centro Custo"]); configure_table(self.table); self.table.itemSelectionChanged.connect(self.on_select); ll.addWidget(self.table)
        right = QWidget(); rl = QVBoxLayout(right); form = QFormLayout()
        self.cb_contrato = SearchableComboBox(); self.cb_cat = SearchableComboBox(); self.cb_cat.addItems(CATEGORIAS)
        self.ed_comp = QLineEdit(); self.ed_desc = QLineEdit(); self.ed_forn = QLineEdit(); self.ed_valor = QLineEdit(); self.ed_doc = QLineEdit(); self.ed_cc = QLineEdit(); self.ed_obs = QTextEdit()
        for label, widget in [("Contrato:",self.cb_contrato),("Competência:",self.ed_comp),("Categoria:",self.cb_cat),("Descrição:",self.ed_desc),("Fornecedor:",self.ed_forn),("Valor Realizado:",self.ed_valor),("Documento Ref.:",self.ed_doc),("Centro de Custo:",self.ed_cc),("Observações:",self.ed_obs)]: form.addRow(label, widget)
        rl.addLayout(form)
        btns = QHBoxLayout()
        self.btn_novo = QPushButton("Novo"); self.btn_salvar = QPushButton("Salvar"); self.btn_excluir = QPushButton("Excluir"); self.btn_limpar = QPushButton("Limpar")
        self.btn_novo.clicked.connect(self.novo); self.btn_salvar.clicked.connect(self.salvar); self.btn_excluir.clicked.connect(self.excluir); self.btn_limpar.clicked.connect(self.limpar)
        for b in [self.btn_novo,self.btn_salvar,self.btn_excluir,self.btn_limpar]: btns.addWidget(b)
        rl.addLayout(btns); rl.addStretch()
        splitter.addWidget(left); splitter.addWidget(right); splitter.setSizes([900,520])
    def reload_data(self):
        cur = self.cb_contrato.currentData(); self.cb_contrato.blockSignals(True); self.cb_contrato.clear(); self.cb_contrato.addItem("(geral)", None)
        for c in self.service.contratos(): self.cb_contrato.addItem(f"{c['codigo']} - {c['nome']}", c["id"])
        idx = self.cb_contrato.findData(cur); self.cb_contrato.setCurrentIndex(idx if idx >= 0 else 0); self.cb_contrato.blockSignals(False)
        rows = self.service.list_all(); self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r,0,IntegerItem(row["id"])); self.table.setItem(r,1,TextItem(row["contrato_codigo"] or "(geral)")); self.table.setItem(r,2,TextItem(row["competencia"])); self.table.setItem(r,3,TextItem(row["categoria"])); self.table.setItem(r,4,TextItem(row["descricao"] or "")); self.table.setItem(r,5,TextItem(row["fornecedor"] or "")); self.table.setItem(r,6,CurrencyItem(row["valor_realizado"])); self.table.setItem(r,7,TextItem(row["documento_ref"] or "")); self.table.setItem(r,8,TextItem(row["centro_custo"] or ""))
        self.after_filter()
    def after_filter(self): self.apply_text_filter(self.table, self.ed_filtro.text())
    def on_select(self):
        items = self.table.selectedItems()
        if not items: return
        self.current_id = int(self.table.item(items[0].row(),0).text()); obj = self.service.get_by_id(self.current_id)
        idx = self.cb_contrato.findData(obj["contrato_id"]); self.cb_contrato.setCurrentIndex(idx if idx >= 0 else 0)
        idx2 = self.cb_cat.findText(obj["categoria"] or ""); self.cb_cat.setCurrentIndex(idx2 if idx2 >= 0 else 0)
        self.ed_comp.setText(obj["competencia"] or ""); self.ed_desc.setText(obj["descricao"] or ""); self.ed_forn.setText(obj["fornecedor"] or ""); self.ed_valor.setText(str(obj["valor_realizado"] or "")); self.ed_doc.setText(obj["documento_ref"] or ""); self.ed_cc.setText(obj["centro_custo"] or ""); self.ed_obs.setPlainText(obj["observacoes"] or "")
    def get_data(self):
        return {"contrato_id": self.cb_contrato.currentData(), "competencia": self.ed_comp.text(), "categoria": self.cb_cat.currentText(), "descricao": self.ed_desc.text(), "fornecedor": self.ed_forn.text(), "valor_realizado": self.ed_valor.text(), "documento_ref": self.ed_doc.text(), "centro_custo": self.ed_cc.text(), "observacoes": self.ed_obs.toPlainText()}
    def novo(self): self.current_id = None; self.limpar()
    def limpar(self): self.table.clearSelection(); self.ed_comp.clear(); self.ed_desc.clear(); self.ed_forn.clear(); self.ed_valor.clear(); self.ed_doc.clear(); self.ed_cc.clear(); self.ed_obs.clear(); self.cb_cat.setCurrentIndex(0); self.cb_contrato.setCurrentIndex(0)
    def salvar(self):
        try:
            data = self.get_data(); self.service.create(data) if self.current_id is None else self.service.update(self.current_id, data)
            QMessageBox.information(self, "Sucesso", "Registro salvo."); self.current_id = None; self.limpar(); self.reload_data(); self.data_changed.emit()
        except Exception as exc: QMessageBox.warning(self, "Atenção", str(exc))
    def excluir(self):
        if self.current_id is None: return
        try:
            self.service.delete(self.current_id); QMessageBox.information(self, "Sucesso", "Registro excluído."); self.current_id = None; self.limpar(); self.reload_data(); self.data_changed.emit()
        except Exception as exc: QMessageBox.warning(self, "Atenção", str(exc))
