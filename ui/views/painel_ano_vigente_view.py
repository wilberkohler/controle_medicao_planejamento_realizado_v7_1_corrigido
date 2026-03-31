from ui.views._base_financeiro_oficial import _BaseOficialView
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ui.widgets.common import configure_table
from ui.widgets.table_items import TextItem, CurrencyItem

class PainelAnoVigenteView(_BaseOficialView):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.rows_cache = []
        self._build_ui()
        self.reload_data()
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.addWidget(QLabel("Painel Ano Vigente"))
        top = QHBoxLayout()
        self.cb_contrato = QComboBox(); self.cb_contrato.currentIndexChanged.connect(self.reload_data)
        self.cb_year = QComboBox(); self.cb_year.addItems(["2026","2027"]); self.cb_year.currentIndexChanged.connect(self.reload_data)
        top.addWidget(QLabel("Contrato:")); top.addWidget(self.cb_contrato); top.addWidget(QLabel("Ano:")); top.addWidget(self.cb_year); top.addStretch(); root.addLayout(top)
        cards = QHBoxLayout()
        self.lbl1=self._card("Receita Prevista","0"); self.lbl2=self._card("Receita Real","0"); self.lbl3=self._card("Custo Real","0"); self.lbl4=self._card("Margem Real","0")
        [cards.addWidget(x) for x in [self.lbl1,self.lbl2,self.lbl3,self.lbl4]]; root.addLayout(cards)
        row = QHBoxLayout(); self.fig1=Figure(figsize=(6,3)); self.canvas1=FigureCanvas(self.fig1); self.fig2=Figure(figsize=(6,3)); self.canvas2=FigureCanvas(self.fig2); row.addWidget(self.canvas1); row.addWidget(self.canvas2); root.addLayout(row)
        self.table = QTableWidget(0,9)
        self.table.setHorizontalHeaderLabels(["Competência","Contrato","Rec. Prev.","Rec. Real","Custo Prev.","Custo Real","Margem Prev.","Margem Real","Desvio Margem"])
        configure_table(self.table); root.addWidget(self.table)
    def reload_data(self):
        self._reload_contracts(self.cb_contrato, self.service)
        rows = self.service.painel_ano_vigente(self.cb_contrato.currentData(), int(self.cb_year.currentText()))
        self.rows_cache = rows
        self.lbl1.setText(f"Receita Prevista\n{self._fmt(sum(r['receita_prevista_atual'] for r in rows))}")
        self.lbl2.setText(f"Receita Real\n{self._fmt(sum(r['receita_realizada'] for r in rows))}")
        self.lbl3.setText(f"Custo Real\n{self._fmt(sum(r['custo_total_realizado'] for r in rows))}")
        self.lbl4.setText(f"Margem Real\n{self._fmt(sum(r['margem_real'] for r in rows))}")
        self.table.setRowCount(0)
        for row in rows:
            r=self.table.rowCount(); self.table.insertRow(r)
            vals=[row["competencia"], row["contrato_codigo"], row["receita_prevista_atual"], row["receita_realizada"], row["custo_total_previsto"], row["custo_total_realizado"], row["margem_prevista"], row["margem_real"], row["desvio_margem"]]
            for c,v in enumerate(vals):
                self.table.setItem(r,c, TextItem(v) if c<2 else CurrencyItem(v))
        self._plot(rows)
    def _plot(self, rows):
        comps=[r["competencia"] for r in rows]
        x=list(range(len(comps)))
        self.fig1.clear(); ax=self.fig1.add_subplot(111)
        ax.plot(x,[r["receita_prevista_atual"] for r in rows], marker="o", label="Rec. Prev.")
        ax.plot(x,[r["receita_realizada"] for r in rows], marker="o", label="Rec. Real")
        ax.set_xticks(x); ax.set_xticklabels(comps, rotation=35, ha="right"); ax.legend(); ax.grid(True, axis="y", alpha=0.3); ax.set_title("Receita mês a mês"); self.fig1.tight_layout(); self.canvas1.draw()
        self.fig2.clear(); ax=self.fig2.add_subplot(111)
        ax.plot(x,[r["margem_prevista"] for r in rows], marker="o", label="Margem Prev.")
        ax.plot(x,[r["margem_real"] for r in rows], marker="o", label="Margem Real")
        ax.set_xticks(x); ax.set_xticklabels(comps, rotation=35, ha="right"); ax.legend(); ax.grid(True, axis="y", alpha=0.3); ax.set_title("Margem mês a mês"); self.fig2.tight_layout(); self.canvas2.draw()
