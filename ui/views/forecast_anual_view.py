from ui.views._base_financeiro_oficial import _BaseOficialView
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ui.widgets.common import configure_table
from ui.widgets.table_items import TextItem, CurrencyItem

class ForecastAnualView(_BaseOficialView):
    def __init__(self, service):
        super().__init__()
        self.service=service
        self._build_ui()
        self.reload_data()
    def _build_ui(self):
        root=QVBoxLayout(self); root.addWidget(QLabel("Forecast Anual"))
        top=QHBoxLayout(); self.cb_contrato=QComboBox(); self.cb_contrato.currentIndexChanged.connect(self.reload_data); top.addWidget(QLabel("Contrato:")); top.addWidget(self.cb_contrato); top.addStretch(); root.addLayout(top)
        self.fig=Figure(figsize=(8,3)); self.canvas=FigureCanvas(self.fig); root.addWidget(self.canvas)
        self.table=QTableWidget(0,7); self.table.setHorizontalHeaderLabels(["Competência","Base","Rec. Forecast","Custo Forecast","Margem Forecast","Acum. Receita","Acum. Margem"]); configure_table(self.table); root.addWidget(self.table)
    def reload_data(self):
        self._reload_contracts(self.cb_contrato, self.service)
        rows=self.service.forecast_anual(self.cb_contrato.currentData(), 2026, 3)
        self.table.setRowCount(0)
        for row in rows:
            r=self.table.rowCount(); self.table.insertRow(r)
            vals=[row["competencia"], row["base_forecast"], row["receita_forecast"], row["custo_forecast"], row["margem_forecast"], row["acumulado_receita_forecast"], row["acumulado_margem_forecast"]]
            for c,v in enumerate(vals):
                self.table.setItem(r,c, TextItem(v) if c<2 else CurrencyItem(v))
        self.fig.clear(); ax=self.fig.add_subplot(111)
        comps=[r["competencia"] for r in rows]; x=list(range(len(comps)))
        ax.plot(x,[r["acumulado_receita_forecast"] for r in rows], marker="o", label="Acum. Receita")
        ax.plot(x,[r["acumulado_margem_forecast"] for r in rows], marker="o", label="Acum. Margem")
        ax.set_xticks(x); ax.set_xticklabels(comps, rotation=35, ha="right"); ax.legend(); ax.grid(True, axis="y", alpha=0.3); ax.set_title("Forecast acumulado do ano")
        self.fig.tight_layout(); self.canvas.draw()
