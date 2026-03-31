from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSplitter, QTableWidget, QComboBox, QMessageBox
from ui.widgets.common import configure_table, status_labels_layout
from ui.widgets.table_items import IntegerItem, TextItem, CurrencyItem, FloatItem
from ui.views.base_mixins import FilterMixin
from ui.widgets.advanced_widgets import SearchableComboBox
from ui.widgets.input_widgets import CurrencyLineEdit

class ProdutividadeCustosView(QWidget, FilterMixin):
    data_changed = Signal()
    def __init__(self, service):
        super().__init__(); self.service=service; self.current_id=None; self._build_ui(); self.reload_data()
    def _build_ui(self):
        root=QHBoxLayout(self); splitter=QSplitter(Qt.Horizontal); root.addWidget(splitter)
        left=QWidget(); ll=QVBoxLayout(left); ll.addWidget(QLabel("Custos de equipe, consultores e terceiros")); self.ed_filtro=QLineEdit(); self.ed_filtro.setPlaceholderText("Pesquisar contrato, disciplina, tipo..."); self.ed_filtro.textChanged.connect(self.after_filter); ll.addWidget(self.ed_filtro)
        self.table=QTableWidget(0,10); self.table.setHorizontalHeaderLabels(["ID","Contrato","Comp.","Disciplina","Tipo","Fornecedor","Horas","Custo hora","Custo total","Status"]); configure_table(self.table); self.table.itemSelectionChanged.connect(self.on_select); ll.addWidget(self.table); st,l=status_labels_layout(); self.lbl_reg,self.lbl_1,self.lbl_2,self.lbl_f=l; ll.addLayout(st)
        right=QWidget(); rl=QVBoxLayout(right); form=QFormLayout()
        self.cb_usuario=SearchableComboBox(); self.cb_contrato=SearchableComboBox(); self.cb_contrato.currentIndexChanged.connect(self.on_contrato_changed); self.cb_etapa=SearchableComboBox(); self.cb_etapa.currentIndexChanged.connect(self.on_etapa_changed); self.cb_grupo=SearchableComboBox()
        self.ed_comp=QLineEdit(); self.cb_disc=SearchableComboBox(); self.cb_tipo=QComboBox(); self.cb_tipo.addItems(["equipe","consultor","terceiro"]); self.ed_forn=QLineEdit(); self.ed_horas=QLineEdit(); self.ed_custo_h=CurrencyLineEdit(); self.ed_custo_total=CurrencyLineEdit(); self.cb_status=QComboBox(); self.cb_status.addItems(["rascunho","em_aprovacao","aprovado","rejeitado"]); self.ed_obs=QTextEdit()
        for label, widget in [("Usuário (opcional):",self.cb_usuario),("Contrato:",self.cb_contrato),("Etapa:",self.cb_etapa),("Grupo:",self.cb_grupo),("Competência:",self.ed_comp),("Disciplina:",self.cb_disc),("Tipo recurso:",self.cb_tipo),("Fornecedor:",self.ed_forn),("Horas:",self.ed_horas),("Custo hora:",self.ed_custo_h),("Custo total:",self.ed_custo_total),("Status:",self.cb_status),("Observações:",self.ed_obs)]: form.addRow(label, widget)
        rl.addLayout(form); self.ed_horas.editingFinished.connect(self.calc_total); self.ed_custo_h.editingFinished.connect(self.calc_total)
        btns=QHBoxLayout(); self.btn_novo=QPushButton("Novo"); self.btn_salvar=QPushButton("Salvar"); self.btn_excluir=QPushButton("Excluir"); self.btn_limpar=QPushButton("Limpar"); [btns.addWidget(b) for b in [self.btn_novo,self.btn_salvar,self.btn_excluir,self.btn_limpar]]; self.btn_novo.clicked.connect(self.novo); self.btn_salvar.clicked.connect(self.salvar); self.btn_excluir.clicked.connect(self.excluir); self.btn_limpar.clicked.connect(self.limpar); rl.addLayout(btns); rl.addStretch(); splitter.addWidget(left); splitter.addWidget(right)
    def reload_data(self):
        self._load_combos(); rows=self.service.list_all(); self.table.setSortingEnabled(False); self.table.setRowCount(0); total=0
        for row in rows:
            total += float(row["custo_total"] or 0)
            r=self.table.rowCount(); self.table.insertRow(r); self.table.setItem(r,0,IntegerItem(row["id"])); self.table.setItem(r,1,TextItem(row["contrato_codigo"])); self.table.setItem(r,2,TextItem(row["competencia"])); self.table.setItem(r,3,TextItem(row["disciplina"])); self.table.setItem(r,4,TextItem(row["tipo_recurso"])); self.table.setItem(r,5,TextItem(row["fornecedor_nome"] or row["usuario_nome"] or "")); self.table.setItem(r,6,FloatItem(row["horas"],2)); self.table.setItem(r,7,CurrencyItem(row["custo_hora"])); self.table.setItem(r,8,CurrencyItem(row["custo_total"])); self.table.setItem(r,9,TextItem(row["status_aprovacao"] or ""))
        self.table.setSortingEnabled(True); self.lbl_1.setText(f"Custo total: {total:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")); self.after_filter()
    def _load_combos(self):
        curu=self.cb_usuario.currentData(); curc=self.cb_contrato.currentData(); curd=self.cb_disc.currentText()
        self.cb_usuario.clear(); self.cb_usuario.addItem("Nenhum", None)
        for u in self.service.usuarios(): self.cb_usuario.addItem(f"{u['id']} - {u['nome']}", u["id"])
        self.cb_contrato.clear()
        for c in self.service.contratos(): self.cb_contrato.addItem(f"{c['id']} - {c['codigo']} - {c['nome']}", c["id"])
        self.cb_disc.clear()
        for d in self.service.disciplinas(): self.cb_disc.addItem(d["disciplina"], d["disciplina"])
        i=self.cb_usuario.findData(curu); self.cb_usuario.setCurrentIndex(i if i>=0 else 0); i=self.cb_contrato.findData(curc); self.cb_contrato.setCurrentIndex(i if i>=0 and self.cb_contrato.count()>0 else 0); i=self.cb_disc.findText(curd); self.cb_disc.setCurrentIndex(i if i>=0 and self.cb_disc.count()>0 else 0); self.on_contrato_changed()
    def on_contrato_changed(self):
        cur=self.cb_etapa.currentData(); self.cb_etapa.clear(); cid=self.cb_contrato.currentData()
        if cid:
            for e in self.service.etapas(int(cid)): self.cb_etapa.addItem(f"{e['id']} - {e['codigo']} - {e['descricao']}", e["id"])
        i=self.cb_etapa.findData(cur); self.cb_etapa.setCurrentIndex(i if i>=0 and self.cb_etapa.count()>0 else 0); self.on_etapa_changed()
    def on_etapa_changed(self):
        cur=self.cb_grupo.currentData(); self.cb_grupo.clear(); eid=self.cb_etapa.currentData()
        if eid:
            for g in self.service.grupos(int(eid)): self.cb_grupo.addItem(f"{g['id']} - {g['codigo']} - {g['descricao']}", g["id"])
        i=self.cb_grupo.findData(cur); self.cb_grupo.setCurrentIndex(i if i>=0 and self.cb_grupo.count()>0 else 0)
    def calc_total(self):
        try: horas=float((self.ed_horas.text() or "0").replace(".","").replace(",","."))
        except: horas=0
        try: ch=float((self.ed_custo_h.text() or "0").replace(".","").replace(",","."))
        except: ch=0
        self.ed_custo_total.setText(str(round(horas*ch,2)))
    def after_filter(self):
        self.apply_text_filter(self.table,self.ed_filtro.text()); vis=sum(1 for r in range(self.table.rowCount()) if not self.table.isRowHidden(r)); self.lbl_reg.setText(f"Registros: {vis} / {self.table.rowCount()}"); self.lbl_f.setText("Filtro texto: sim" if self.ed_filtro.text().strip() else "Filtro texto: não")
    def on_select(self):
        items=self.table.selectedItems()
        if not items: return
        self.current_id=int(self.table.item(items[0].row(),0).text()); obj=self.service.get_by_id(self.current_id); self.cb_usuario.setCurrentIndex(self.cb_usuario.findData(obj["usuario_id"])); self.cb_contrato.setCurrentIndex(self.cb_contrato.findData(obj["contrato_id"])); self.on_contrato_changed(); self.cb_etapa.setCurrentIndex(self.cb_etapa.findData(obj["etapa_id"])); self.on_etapa_changed(); self.cb_grupo.setCurrentIndex(self.cb_grupo.findData(obj["grupo_id"])); self.ed_comp.setText(obj["competencia"] or ""); self.cb_disc.setCurrentIndex(self.cb_disc.findText(obj["disciplina"] or "")); self.cb_tipo.setCurrentIndex(self.cb_tipo.findText(obj["tipo_recurso"] or "")); self.ed_forn.setText(obj["fornecedor_nome"] or ""); self.ed_horas.setText(str(obj["horas"] or "")); self.ed_custo_h.setText(str(obj["custo_hora"] or "")); self.ed_custo_total.setText(str(obj["custo_total"] or "")); self.cb_status.setCurrentIndex(self.cb_status.findText(obj["status_aprovacao"] or "rascunho")); self.ed_obs.setPlainText(obj["observacoes"] or "")
    def get_data(self): return {"usuario_id":self.cb_usuario.currentData(),"contrato_id":self.cb_contrato.currentData() or 0,"etapa_id":self.cb_etapa.currentData(),"grupo_id":self.cb_grupo.currentData(),"competencia":self.ed_comp.text(),"disciplina":self.cb_disc.currentText(),"tipo_recurso":self.cb_tipo.currentText(),"fornecedor_nome":self.ed_forn.text(),"horas":self.ed_horas.text(),"custo_hora":self.ed_custo_h.text(),"custo_total":self.ed_custo_total.text(),"status_aprovacao":self.cb_status.currentText(),"observacoes":self.ed_obs.toPlainText()}
    def novo(self): self.current_id=None; self.limpar()
    def limpar(self): self.cb_usuario.setCurrentIndex(0); self.cb_contrato.setCurrentIndex(0 if self.cb_contrato.count()>0 else -1); self.on_contrato_changed(); self.ed_comp.clear(); self.ed_forn.clear(); self.ed_horas.clear(); self.ed_custo_h.clear(); self.ed_custo_total.clear(); self.cb_status.setCurrentIndex(0); self.ed_obs.clear(); self.table.clearSelection()
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
