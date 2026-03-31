from ui.views._base_financeiro_oficial import _BaseOficialView
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget
from ui.widgets.common import configure_table
from ui.widgets.table_items import TextItem, CurrencyItem

class CockpitMensalOficialView(_BaseOficialView):
    def __init__(self, service):
        super().__init__()
        self.service=service
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        root=QVBoxLayout(self)
        title = QLabel("Cockpit Mensal Oficial")
        title.setStyleSheet("font-size:18px;font-weight:700;")
        root.addWidget(title)

        top=QHBoxLayout()
        self.cb_contrato=QComboBox(); self.cb_contrato.currentIndexChanged.connect(self.reload_data)
        self.cb_comp=QComboBox(); self.cb_comp.currentIndexChanged.connect(self.reload_data)
        top.addWidget(QLabel("Contrato:")); top.addWidget(self.cb_contrato)
        top.addWidget(QLabel("Competência:")); top.addWidget(self.cb_comp)
        top.addStretch()
        root.addLayout(top)

        cards=QHBoxLayout()
        self.lbl1=self._card("Rec. Prev. Atual","0")
        self.lbl2=self._card("Rec. Real","0")
        self.lbl3=self._card("Custo Real","0")
        self.lbl4=self._card("Margem Real","0")
        self.lbl5=self._card("Desvio Receita","0")
        for x in [self.lbl1,self.lbl2,self.lbl3,self.lbl4,self.lbl5]:
            cards.addWidget(x)
        root.addLayout(cards)

        root.addWidget(QLabel("Alertas automáticos de divergência"))
        self.table_alertas = QTableWidget(0,4)
        self.table_alertas.setHorizontalHeaderLabels(["Nível","Contrato","Competência","Mensagem"])
        configure_table(self.table_alertas)
        root.addWidget(self.table_alertas)

        root.addWidget(QLabel("Composição por contrato"))
        self.table=QTableWidget(0,7)
        self.table.setHorizontalHeaderLabels(["Contrato","Competência","Rec. Prev.","Rec. Real","Custo Real","Imposto Real","Margem Real"])
        configure_table(self.table)
        root.addWidget(self.table)

    def reload_data(self):
        self._reload_contracts(self.cb_contrato, self.service)
        all_rows=self.service.painel_ano_vigente(self.cb_contrato.currentData(), 2026)
        cur=self.cb_comp.currentText()
        self.cb_comp.blockSignals(True)
        self.cb_comp.clear()
        comps=sorted({r["competencia"] for r in all_rows}, key=lambda s:(int(s.split('/')[1]), int(s.split('/')[0])) if '/' in s else (0,0))
        for c in comps:
            self.cb_comp.addItem(c)
        idx=self.cb_comp.findText(cur)
        self.cb_comp.setCurrentIndex(idx if idx>=0 else (self.cb_comp.count()-1 if self.cb_comp.count() else -1))
        self.cb_comp.blockSignals(False)

        comp=self.cb_comp.currentText()
        data=self.service.cockpit_mensal_oficial(comp, self.cb_contrato.currentData()) if comp else {"resumo":{},"linhas":[]}
        res=data["resumo"]; rows=data["linhas"]
        alerts=self.service.cockpit_alertas_divergencia(comp, self.cb_contrato.currentData()) if comp else []

        self.lbl1.setText(f"Rec. Prev. Atual\n{self._fmt(res.get('receita_prevista_atual',0))}")
        self.lbl2.setText(f"Rec. Real\n{self._fmt(res.get('receita_realizada',0))}")
        self.lbl3.setText(f"Custo Real\n{self._fmt(res.get('custo_total_realizado',0))}")
        self.lbl4.setText(f"Margem Real\n{self._fmt(res.get('margem_real',0))}")
        self.lbl5.setText(f"Desvio Receita\n{self._fmt(res.get('desvio_receita',0))}")

        self.table_alertas.setRowCount(0)
        for a in alerts:
            r=self.table_alertas.rowCount(); self.table_alertas.insertRow(r)
            self.table_alertas.setItem(r,0,TextItem(a["nivel"]))
            self.table_alertas.setItem(r,1,TextItem(a["contrato_codigo"]))
            self.table_alertas.setItem(r,2,TextItem(a["competencia"]))
            self.table_alertas.setItem(r,3,TextItem(a["mensagem"]))

        self.table.setRowCount(0)
        for row in rows:
            r=self.table.rowCount(); self.table.insertRow(r)
            vals=[row["contrato_codigo"], row["competencia"], row["receita_prevista_atual"], row["receita_realizada"], row["custo_total_realizado"], row["imposto_real"], row["margem_real"]]
            for c,v in enumerate(vals):
                self.table.setItem(r,c, TextItem(v) if c<2 else CurrencyItem(v))
