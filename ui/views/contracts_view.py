from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSplitter, QTableWidget, QComboBox, QMessageBox
from ui.widgets.common import configure_table, status_labels_layout, apply_float_validator
from ui.widgets.table_items import IntegerItem, TextItem, CurrencyItem
from ui.views.base_mixins import FilterMixin
from ui.widgets.advanced_widgets import SearchableComboBox, DateFieldWidget
from ui.widgets.input_widgets import DateLineEdit, CurrencyLineEdit, PercentLineEdit

class ContratosView(QWidget, FilterMixin):
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

        left = QWidget(); left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Contratos"))
        self.ed_filtro = QLineEdit(); self.ed_filtro.setPlaceholderText("Filtrar por código, nome, cliente ou status...")
        self.ed_filtro.textChanged.connect(self.after_filter)
        left_layout.addWidget(self.ed_filtro)

        self.cb_status_filtro = SearchableComboBox()
        self.cb_status_filtro.addItems(["Todos","planejamento","em_andamento","encerrado","cancelado"])
        self.cb_status_filtro.currentIndexChanged.connect(self.reload_data)
        left_layout.addWidget(self.cb_status_filtro)

        self.table = QTableWidget(0,6)
        self.table.setHorizontalHeaderLabels(["ID","Código","Nome","Cliente","Valor Total","Status"])
        configure_table(self.table)
        self.table.itemSelectionChanged.connect(self.on_select)
        left_layout.addWidget(self.table)
        status_layout, labels = status_labels_layout()
        self.lbl_reg, self.lbl_1, self.lbl_2, self.lbl_f = labels
        left_layout.addLayout(status_layout)

        right = QWidget(); right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("Cadastro / edição"))
        form = QFormLayout()
        self.ed_codigo = QLineEdit(); self.ed_nome = QLineEdit(); self.ed_cliente = QLineEdit()
        self.ed_data_inicio = DateLineEdit()
        self.ed_data_fim = DateLineEdit()
        self.ed_valor = CurrencyLineEdit(); self.ed_percentual = PercentLineEdit()
        apply_float_validator(self.ed_valor, 999999999999.99, 2)
        apply_float_validator(self.ed_percentual, 100.0, 4)
        self.cb_status = SearchableComboBox(); self.cb_status.addItems(["planejamento","em_andamento","encerrado","cancelado"])
        self.ed_obs = QTextEdit()
        for label, widget in [("Código:",self.ed_codigo),("Nome:",self.ed_nome),("Cliente:",self.ed_cliente),("Data início:",DateFieldWidget(self.ed_data_inicio)),("Data fim:",DateFieldWidget(self.ed_data_fim)),("Valor total:",self.ed_valor),("% sinal:",self.ed_percentual),("Status:",self.cb_status),("Observações:",self.ed_obs)]:
            form.addRow(label, widget)
        right_layout.addLayout(form)
        buttons = QHBoxLayout()
        self.btn_novo = QPushButton("Novo"); self.btn_salvar = QPushButton("Salvar"); self.btn_excluir = QPushButton("Excluir"); self.btn_limpar = QPushButton("Limpar")
        self.btn_novo.clicked.connect(self.novo); self.btn_salvar.clicked.connect(self.salvar); self.btn_excluir.clicked.connect(self.excluir); self.btn_limpar.clicked.connect(self.limpar)
        for b in [self.btn_novo,self.btn_salvar,self.btn_excluir,self.btn_limpar]: buttons.addWidget(b)
        right_layout.addLayout(buttons); right_layout.addStretch()

        splitter.addWidget(left); splitter.addWidget(right); splitter.setSizes([850,500])

    def reload_data(self):
        rows = self.service.list_all()
        status_filter = self.cb_status_filtro.currentText()
        if status_filter != "Todos":
            rows = [r for r in rows if (r["status"] or "") == status_filter]
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        total = 0.0
        for row in rows:
            total += float(row["valor_total_contrato"] or 0)
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r,0,IntegerItem(row["id"]))
            self.table.setItem(r,1,TextItem(row["codigo"]))
            self.table.setItem(r,2,TextItem(row["nome"]))
            self.table.setItem(r,3,TextItem(row["cliente"] or ""))
            self.table.setItem(r,4,CurrencyItem(row["valor_total_contrato"]))
            status_item = TextItem(row["status"] or "")
            if (row["status"] or "") == "encerrado": status_item.setBackground(__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.green)
            elif (row["status"] or "") == "cancelado": status_item.setBackground(__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.red)
            else: status_item.setBackground(__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.yellow)
            self.table.setItem(r,5,status_item)
        self.table.setSortingEnabled(True)
        self.lbl_1.setText(f"Valor total: {self.table.item(0,4).text() if False else ''}")
        self.lbl_1.setText("Valor total: " + __import__("utils.number_utils", fromlist=["br_number"]).br_number(total,2))
        self.lbl_2.setText(f"Status: {status_filter}")
        self.after_filter()

    def after_filter(self):
        self.apply_text_filter(self.table, self.ed_filtro.text())
        visible = sum(1 for r in range(self.table.rowCount()) if not self.table.isRowHidden(r))
        self.lbl_reg.setText(f"Registros: {visible} / {self.table.rowCount()}")
        self.lbl_f.setText("Filtro: sim" if self.ed_filtro.text().strip() else "Filtro: não")

    def on_select(self):
        items = self.table.selectedItems()
        if not items: return
        row = items[0].row()
        self.current_id = int(self.table.item(row,0).text())
        obj = self.service.get_by_id(self.current_id)
        if obj is None: return
        self.ed_codigo.setText(obj["codigo"] or ""); self.ed_nome.setText(obj["nome"] or ""); self.ed_cliente.setText(obj["cliente"] or "")
        self.ed_data_inicio.setText(obj["data_inicio"] or ""); self.ed_data_fim.setText(obj["data_fim"] or "")
        self.ed_valor.setText(str(obj["valor_total_contrato"] or "")); self.ed_percentual.setText(str(obj["percentual_sinal"] or ""))
        idx = self.cb_status.findText(obj["status"] or ""); 
        if idx >= 0: self.cb_status.setCurrentIndex(idx)
        self.ed_obs.setPlainText(obj["observacoes"] or "")

    def get_data(self):
        return {"codigo": self.ed_codigo.text(), "nome": self.ed_nome.text(), "cliente": self.ed_cliente.text(), "data_inicio": self.ed_data_inicio.text(), "data_fim": self.ed_data_fim.text(), "valor_total_contrato": self.ed_valor.text(), "percentual_sinal": self.ed_percentual.text(), "status": self.cb_status.currentText(), "observacoes": self.ed_obs.toPlainText()}

    def novo(self): self.current_id = None; self.limpar()
    def limpar(self):
        for w in [self.ed_codigo,self.ed_nome,self.ed_cliente,self.ed_data_inicio,self.ed_data_fim,self.ed_valor,self.ed_percentual]: w.clear()
        self.cb_status.setCurrentIndex(0); self.ed_obs.clear(); self.table.clearSelection()

    def salvar(self):
        try:
            data = self.get_data()
            if self.current_id is None: self.service.create(data)
            else: self.service.update(self.current_id, data)
            QMessageBox.information(self,"Sucesso","Operação realizada com sucesso.")
            self.current_id = None; self.limpar(); self.reload_data(); self.data_changed.emit()
        except Exception as exc:
            QMessageBox.warning(self,"Atenção",str(exc))

    def excluir(self):
        if self.current_id is None:
            QMessageBox.information(self,"Excluir","Selecione um contrato para excluir."); return
        ok = QMessageBox.question(self,"Confirmar exclusão","Deseja realmente excluir este contrato?")
        if ok != QMessageBox.Yes: return
        try:
            self.service.delete(self.current_id)
            QMessageBox.information(self,"Sucesso","Contrato excluído com sucesso.")
            self.current_id = None; self.limpar(); self.reload_data(); self.data_changed.emit()
        except Exception as exc:
            QMessageBox.warning(self,"Atenção",str(exc))
