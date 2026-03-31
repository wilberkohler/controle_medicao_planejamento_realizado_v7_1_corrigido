from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSplitter, QTableWidget, QMessageBox
from ui.widgets.common import configure_table, status_labels_layout, apply_float_validator
from ui.widgets.table_items import IntegerItem, TextItem, FloatItem, CurrencyItem
from ui.views.base_mixins import FilterMixin
from ui.widgets.advanced_widgets import SearchableComboBox

class ProdutividadeRealizadoView(QWidget, FilterMixin):
    data_changed = Signal()
    def __init__(self, service):
        super().__init__(); self.service=service; self.current_id=None; self._build_ui(); self.reload_data()
    def _build_ui(self):
        root=QHBoxLayout(self); splitter=QSplitter(Qt.Horizontal); root.addWidget(splitter)
        left=QWidget(); left_layout=QVBoxLayout(left); left_layout.addWidget(QLabel("Realizado de produtividade / custos"))
        self.ed_filtro=QLineEdit(); self.ed_filtro.setPlaceholderText("Pesquisar usuário, contrato, disciplina ou tipo de recurso..."); self.ed_filtro.textChanged.connect(self.after_filter); left_layout.addWidget(self.ed_filtro)
        self.table=QTableWidget(0,11)
        self.table.setHorizontalHeaderLabels(["ID","Usuário","Contrato","Competência","Disciplina","Tipo recurso","Produzido A1","Horas reais","Custo hora","Custo real","Status"])
        configure_table(self.table); self.table.itemSelectionChanged.connect(self.on_select)
        left_layout.addWidget(self.table)
        status_layout, labels=status_labels_layout(); self.lbl_reg,self.lbl_1,self.lbl_2,self.lbl_f=labels; left_layout.addLayout(status_layout)

        right=QWidget(); right_layout=QVBoxLayout(right); right_layout.addWidget(QLabel("Cadastro / edição"))
        form=QFormLayout()
        self.cb_usuario=SearchableComboBox(); self.cb_contrato=SearchableComboBox(); self.cb_contrato.currentIndexChanged.connect(self.on_contract_changed)
        self.cb_etapa=SearchableComboBox(); self.cb_etapa.currentIndexChanged.connect(self.on_etapa_changed)
        self.cb_grupo=SearchableComboBox(); self.cb_grupo.currentIndexChanged.connect(self.on_grupo_changed)
        self.cb_entregavel=SearchableComboBox()
        self.ed_comp=QLineEdit(); self.cb_disciplina=SearchableComboBox(); self.cb_tipo=SearchableComboBox(); self.cb_tipo.addItems(["equipe_interna","consultor","terceiro"])
        self.ed_fornecedor=QLineEdit()
        self.ed_prod=QLineEdit(); self.ed_horas_a1=QLineEdit(); self.ed_custo_h=QLineEdit()
        for w in [self.ed_prod,self.ed_horas_a1,self.ed_custo_h]: apply_float_validator(w, 999999, 4)
        self.cb_status=SearchableComboBox(); self.cb_status.addItems(["rascunho","em_aprovacao","aprovado","rejeitado"])
        self.ed_desc=QTextEdit()
        for label, widget in [("Usuário:",self.cb_usuario),("Contrato:",self.cb_contrato),("Etapa:",self.cb_etapa),("Grupo:",self.cb_grupo),("Entregável:",self.cb_entregavel),("Competência:",self.ed_comp),("Disciplina:",self.cb_disciplina),("Tipo recurso:",self.cb_tipo),("Consultor / terceiro:",self.ed_fornecedor),("Produzido (A1):",self.ed_prod),("Horas por A1:",self.ed_horas_a1),("Custo hora:",self.ed_custo_h),("Status aprovação:",self.cb_status),("Descrição:",self.ed_desc)]:
            form.addRow(label, widget)
        right_layout.addLayout(form)
        btns=QHBoxLayout(); self.btn_novo=QPushButton("Novo"); self.btn_salvar=QPushButton("Salvar"); self.btn_excluir=QPushButton("Excluir"); self.btn_limpar=QPushButton("Limpar")
        for b in [self.btn_novo,self.btn_salvar,self.btn_excluir,self.btn_limpar]: btns.addWidget(b)
        self.btn_novo.clicked.connect(self.novo); self.btn_salvar.clicked.connect(self.salvar); self.btn_excluir.clicked.connect(self.excluir); self.btn_limpar.clicked.connect(self.limpar)
        right_layout.addLayout(btns); right_layout.addStretch()
        splitter.addWidget(left); splitter.addWidget(right); splitter.setSizes([1080,560])
    def reload_data(self):
        cur_u=self.cb_usuario.currentData(); cur_c=self.cb_contrato.currentData(); cur_d=self.cb_disciplina.currentText()
        self.cb_usuario.clear(); self.cb_contrato.clear(); self.cb_disciplina.clear()
        for u in self.service.usuarios():
            if int(u["ativo"] or 0)==1: self.cb_usuario.addItem(u["nome"], u["id"])
        for c in self.service.contratos():
            self.cb_contrato.addItem(f'{c["codigo"]} - {c["nome"]}', c["id"])
        for p in self.service.parametros():
            self.cb_disciplina.addItem(p["disciplina"])
        idx=self.cb_usuario.findData(cur_u); self.cb_usuario.setCurrentIndex(idx if idx>=0 and self.cb_usuario.count()>0 else 0)
        idx=self.cb_contrato.findData(cur_c); self.cb_contrato.setCurrentIndex(idx if idx>=0 and self.cb_contrato.count()>0 else 0)
        self.on_contract_changed()
        idx=self.cb_disciplina.findText(cur_d); self.cb_disciplina.setCurrentIndex(idx if idx>=0 and self.cb_disciplina.count()>0 else 0)
        rows=self.service.list_all()
        self.table.setSortingEnabled(False); self.table.setRowCount(0)
        total=0.0
        for row in rows:
            total += float(row["custo_real"] or 0)
            r=self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r,0,IntegerItem(row["id"])); self.table.setItem(r,1,TextItem(row["usuario_nome"])); self.table.setItem(r,2,TextItem(row["contrato_codigo"])); self.table.setItem(r,3,TextItem(row["competencia"])); self.table.setItem(r,4,TextItem(row["disciplina"])); self.table.setItem(r,5,TextItem(row["tipo_recurso"])); self.table.setItem(r,6,FloatItem(row["produzido_a1"],2)); self.table.setItem(r,7,FloatItem(row["horas_realizadas"],2)); self.table.setItem(r,8,CurrencyItem(row["custo_hora"])); self.table.setItem(r,9,CurrencyItem(row["custo_real"]))
            st=TextItem(row["status_aprovacao"] or "rascunho")
            self.table.setItem(r,10,st)
        self.table.setSortingEnabled(True)
        self.lbl_1.setText("Custo real: " + __import__("utils.number_utils", fromlist=["br_number"]).br_number(total,2)); self.lbl_2.setText("Custos = horas reais x custo-hora")
        self.after_filter()
    def after_filter(self):
        self.apply_text_filter(self.table, self.ed_filtro.text()); visible=sum(1 for r in range(self.table.rowCount()) if not self.table.isRowHidden(r)); self.lbl_reg.setText(f"Registros: {visible} / {self.table.rowCount()}"); self.lbl_f.setText("Filtro: sim" if self.ed_filtro.text().strip() else "Filtro: não")
    def on_contract_changed(self):
        contrato_id=self.cb_contrato.currentData()
        cur=self.cb_etapa.currentData(); self.cb_etapa.clear(); self.cb_grupo.clear(); self.cb_entregavel.clear()
        self.cb_etapa.addItem("", None)
        if contrato_id:
            for e in self.service.etapas(int(contrato_id)): self.cb_etapa.addItem(f'{e["codigo"]} - {e["descricao"]}', e["id"])
        idx=self.cb_etapa.findData(cur); self.cb_etapa.setCurrentIndex(idx if idx>=0 else 0)
        self.on_etapa_changed()
    def on_etapa_changed(self):
        etapa_id=self.cb_etapa.currentData()
        cur=self.cb_grupo.currentData(); self.cb_grupo.clear(); self.cb_entregavel.clear(); self.cb_grupo.addItem("", None)
        if etapa_id:
            for g in self.service.grupos(int(etapa_id)): self.cb_grupo.addItem(f'{g["codigo"]} - {g["descricao"]}', g["id"])
        idx=self.cb_grupo.findData(cur); self.cb_grupo.setCurrentIndex(idx if idx>=0 else 0)
        self.on_grupo_changed()
    def on_grupo_changed(self):
        grupo_id=self.cb_grupo.currentData()
        cur=self.cb_entregavel.currentData(); self.cb_entregavel.clear(); self.cb_entregavel.addItem("", None)
        if grupo_id:
            for e in self.service.entregaveis(int(grupo_id)): self.cb_entregavel.addItem(f'{e["codigo"]} - {e["descricao"]}', e["id"])
        idx=self.cb_entregavel.findData(cur); self.cb_entregavel.setCurrentIndex(idx if idx>=0 else 0)
    def on_select(self):
        items=self.table.selectedItems()
        if not items: return
        row=items[0].row(); self.current_id=int(self.table.item(row,0).text()); obj=self.service.get_by_id(self.current_id)
        if obj is None: return
        idx=self.cb_usuario.findData(obj["usuario_id"]); self.cb_usuario.setCurrentIndex(idx if idx>=0 else 0)
        idx=self.cb_contrato.findData(obj["contrato_id"]); self.cb_contrato.setCurrentIndex(idx if idx>=0 else 0); self.on_contract_changed()
        idx=self.cb_etapa.findData(obj["etapa_id"]); self.cb_etapa.setCurrentIndex(idx if idx>=0 else 0); self.on_etapa_changed()
        idx=self.cb_grupo.findData(obj["grupo_id"]); self.cb_grupo.setCurrentIndex(idx if idx>=0 else 0); self.on_grupo_changed()
        idx=self.cb_entregavel.findData(obj["entregavel_id"]); self.cb_entregavel.setCurrentIndex(idx if idx>=0 else 0)
        self.ed_comp.setText(obj["competencia"] or ""); idx=self.cb_disciplina.findText(obj["disciplina"] or ""); self.cb_disciplina.setCurrentIndex(idx if idx>=0 else 0)
        idx=self.cb_tipo.findText(obj["tipo_recurso"] or ""); self.cb_tipo.setCurrentIndex(idx if idx>=0 else 0)
        self.ed_fornecedor.setText(obj["fornecedor_nome"] or ""); self.ed_prod.setText(str(obj["produzido_a1"] or "")); self.ed_horas_a1.setText(str(obj["horas_por_a1"] or "")); self.ed_custo_h.setText(str(obj["custo_hora"] or "")); idx=self.cb_status.findText(obj["status_aprovacao"] or "rascunho"); self.cb_status.setCurrentIndex(idx if idx>=0 else 0); self.ed_desc.setPlainText(obj["descricao"] or "")
        aprovado = str(obj["status_aprovacao"] or "rascunho") == "aprovado"; self.btn_salvar.setEnabled(not aprovado); self.btn_excluir.setEnabled(not aprovado)
    def get_data(self):
        return {"usuario_id":self.cb_usuario.currentData() or 0,"contrato_id":self.cb_contrato.currentData() or 0,"etapa_id":self.cb_etapa.currentData(),"grupo_id":self.cb_grupo.currentData(),"entregavel_id":self.cb_entregavel.currentData(),"competencia":self.ed_comp.text(),"disciplina":self.cb_disciplina.currentText(),"tipo_recurso":self.cb_tipo.currentText(),"fornecedor_nome":self.ed_fornecedor.text(),"produzido_a1":self.ed_prod.text(),"horas_por_a1":self.ed_horas_a1.text(),"custo_hora":self.ed_custo_h.text(),"status_aprovacao":self.cb_status.currentText(),"descricao":self.ed_desc.toPlainText()}
    def novo(self): self.current_id=None; self.limpar()
    def limpar(self):
        if self.cb_usuario.count()>0: self.cb_usuario.setCurrentIndex(0)
        if self.cb_contrato.count()>0: self.cb_contrato.setCurrentIndex(0)
        self.on_contract_changed()
        if self.cb_disciplina.count()>0: self.cb_disciplina.setCurrentIndex(0)
        self.cb_tipo.setCurrentIndex(0); self.cb_status.setCurrentIndex(0)
        for w in [self.ed_comp,self.ed_fornecedor,self.ed_prod,self.ed_horas_a1,self.ed_custo_h]: w.clear()
        self.ed_desc.clear(); self.table.clearSelection(); self.btn_salvar.setEnabled(True); self.btn_excluir.setEnabled(True)
    def salvar(self):
        try:
            data=self.get_data()
            if self.current_id is None: self.service.create(data)
            else: self.service.update(self.current_id, data)
            QMessageBox.information(self,"Sucesso","Operação realizada com sucesso."); self.current_id=None; self.limpar(); self.reload_data(); self.data_changed.emit()
        except Exception as exc:
            QMessageBox.warning(self,"Atenção",str(exc))
    def excluir(self):
        if self.current_id is None: QMessageBox.information(self,"Excluir","Selecione um registro."); return
        ok=QMessageBox.question(self,"Confirmar exclusão","Deseja realmente excluir este registro?")
        if ok != QMessageBox.Yes: return
        try:
            self.service.delete(self.current_id); QMessageBox.information(self,"Sucesso","Registro excluído."); self.current_id=None; self.limpar(); self.reload_data(); self.data_changed.emit()
        except Exception as exc:
            QMessageBox.warning(self,"Atenção",str(exc))
