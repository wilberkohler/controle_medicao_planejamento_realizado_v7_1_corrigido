from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSplitter, QTableWidget, QComboBox, QMessageBox
from ui.widgets.common import configure_table, status_labels_layout
from ui.widgets.table_items import IntegerItem, TextItem, FloatItem, CurrencyItem
from ui.views.base_mixins import FilterMixin
from ui.widgets.input_widgets import CurrencyLineEdit

class ProdutividadeParametrosView(QWidget, FilterMixin):
    data_changed = Signal()
    def __init__(self, service):
        super().__init__(); self.service=service; self.current_id=None; self._build_ui(); self.reload_data()
    def _build_ui(self):
        root=QHBoxLayout(self); splitter=QSplitter(Qt.Horizontal); root.addWidget(splitter)
        left=QWidget(); ll=QVBoxLayout(left); ll.addWidget(QLabel("Parâmetros de produtividade")); self.ed_filtro=QLineEdit(); self.ed_filtro.setPlaceholderText("Pesquisar disciplina..."); self.ed_filtro.textChanged.connect(self.after_filter); ll.addWidget(self.ed_filtro); self.table=QTableWidget(0,5); self.table.setHorizontalHeaderLabels(["ID","Disciplina","Horas/A1","Custo hora equipe","Ativo"]); configure_table(self.table); self.table.itemSelectionChanged.connect(self.on_select); ll.addWidget(self.table); st,l=status_labels_layout(); self.lbl_reg,self.lbl_1,self.lbl_2,self.lbl_f=l; ll.addLayout(st)
        right=QWidget(); rl=QVBoxLayout(right); form=QFormLayout(); self.ed_disc=QLineEdit(); self.ed_horas=QLineEdit(); self.ed_custo=CurrencyLineEdit(); self.cb_ativo=QComboBox(); self.cb_ativo.addItems(["Sim","Não"]); self.ed_obs=QTextEdit(); form.addRow("Disciplina:",self.ed_disc); form.addRow("Horas por A1:",self.ed_horas); form.addRow("Custo hora equipe:",self.ed_custo); form.addRow("Ativo:",self.cb_ativo); form.addRow("Observações:",self.ed_obs); rl.addLayout(form); btns=QHBoxLayout(); self.btn_novo=QPushButton("Novo"); self.btn_salvar=QPushButton("Salvar"); self.btn_excluir=QPushButton("Excluir"); self.btn_limpar=QPushButton("Limpar"); [btns.addWidget(b) for b in [self.btn_novo,self.btn_salvar,self.btn_excluir,self.btn_limpar]]; self.btn_novo.clicked.connect(self.novo); self.btn_salvar.clicked.connect(self.salvar); self.btn_excluir.clicked.connect(self.excluir); self.btn_limpar.clicked.connect(self.limpar); rl.addLayout(btns); rl.addStretch(); splitter.addWidget(left); splitter.addWidget(right)
    def reload_data(self):
        rows=self.service.list_all(); self.table.setSortingEnabled(False); self.table.setRowCount(0)
        for row in rows:
            r=self.table.rowCount(); self.table.insertRow(r); self.table.setItem(r,0,IntegerItem(row["id"])); self.table.setItem(r,1,TextItem(row["disciplina"])); self.table.setItem(r,2,FloatItem(row["horas_por_a1"],2)); self.table.setItem(r,3,CurrencyItem(row["custo_hora_equipe"])); self.table.setItem(r,4,TextItem("Sim" if int(row["ativo"] or 0)==1 else "Não"))
        self.table.setSortingEnabled(True); self.lbl_1.setText(f"Disciplinas: {len(rows)}"); self.after_filter()
    def after_filter(self):
        self.apply_text_filter(self.table,self.ed_filtro.text()); vis=sum(1 for r in range(self.table.rowCount()) if not self.table.isRowHidden(r)); self.lbl_reg.setText(f"Registros: {vis} / {self.table.rowCount()}"); self.lbl_f.setText("Filtro texto: sim" if self.ed_filtro.text().strip() else "Filtro texto: não")
    def on_select(self):
        items=self.table.selectedItems()
        if not items: return
        self.current_id=int(self.table.item(items[0].row(),0).text()); obj=self.service.get_by_id(self.current_id); self.ed_disc.setText(obj["disciplina"] or ""); self.ed_horas.setText(str(obj["horas_por_a1"] or "")); self.ed_custo.setText(str(obj["custo_hora_equipe"] or "")); self.cb_ativo.setCurrentIndex(0 if int(obj["ativo"] or 0)==1 else 1); self.ed_obs.setPlainText(obj["observacoes"] or "")
    def get_data(self): return {"disciplina":self.ed_disc.text(),"horas_por_a1":self.ed_horas.text(),"custo_hora_equipe":self.ed_custo.text(),"ativo":self.cb_ativo.currentText(),"observacoes":self.ed_obs.toPlainText()}
    def novo(self): self.current_id=None; self.limpar()
    def limpar(self): self.ed_disc.clear(); self.ed_horas.clear(); self.ed_custo.clear(); self.cb_ativo.setCurrentIndex(0); self.ed_obs.clear(); self.table.clearSelection()
    def salvar(self):
        try:
            if self.current_id is None: self.service.create(self.get_data())
            else: self.service.update(self.current_id,self.get_data())
            QMessageBox.information(self,"Sucesso","Operação realizada com sucesso."); self.current_id=None; self.limpar(); self.reload_data(); self.data_changed.emit()
        except Exception as exc: QMessageBox.warning(self,"Atenção",str(exc))
    def excluir(self):
        if self.current_id is None: QMessageBox.information(self,"Excluir","Selecione um registro."); return
        if QMessageBox.question(self,"Confirmar exclusão","Deseja realmente excluir este registro?")!=QMessageBox.Yes: return
        try: self.service.delete(self.current_id); QMessageBox.information(self,"Sucesso","Registro excluído."); self.current_id=None; self.limpar(); self.reload_data(); self.data_changed.emit()
        except Exception as exc: QMessageBox.warning(self,"Atenção",str(exc))
