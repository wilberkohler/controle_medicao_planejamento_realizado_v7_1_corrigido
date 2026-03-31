from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget
from ui.widgets.common import configure_table
from ui.widgets.table_items import TextItem, CurrencyItem, FloatItem
from utils.number_utils import br_number

class ComparativoMensalView(QWidget):
    def __init__(self, analytics_service, contrato_service):
        super().__init__()
        self.analytics_service = analytics_service
        self.contrato_service = contrato_service
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.addWidget(QLabel("Comparativo mensal"))
        top = QHBoxLayout()
        self.cb_contrato = QComboBox()
        self.cb_contrato.currentIndexChanged.connect(self.reload_data)
        top.addWidget(QLabel("Contrato:"))
        top.addWidget(self.cb_contrato)
        root.addLayout(top)
        self.table = QTableWidget(0,10)
        self.table.setHorizontalHeaderLabels(["Contrato","Competência","Etapa","Grupo","Entregável","Previsto Mês","Realizado Mês","Saldo Mês","% Previsto","% Realizado"])
        configure_table(self.table)
        root.addWidget(self.table)
        self.lbl = QLabel("")
        root.addWidget(self.lbl)

    def reload_data(self):
        cur = self.cb_contrato.currentData()
        self.cb_contrato.blockSignals(True)
        self.cb_contrato.clear(); self.cb_contrato.addItem("Todos", None)
        for c in self.contrato_service.list_all():
            self.cb_contrato.addItem(f"{c['codigo']} - {c['nome']}", c["id"])
        idx = self.cb_contrato.findData(cur); self.cb_contrato.setCurrentIndex(idx if idx >= 0 else 0)
        self.cb_contrato.blockSignals(False)

        rows = self.analytics_service.comparativo_mensal(self.cb_contrato.currentData())
        self.table.setSortingEnabled(False); self.table.setRowCount(0)
        saldo_total = 0.0
        for row in rows:
            saldo = float(row["valor_previsto_mes"] or 0) - float(row["valor_realizado_mes"] or 0)
            saldo_total += saldo
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r,0,TextItem(row["contrato_codigo"]))
            self.table.setItem(r,1,TextItem(row["competencia"]))
            self.table.setItem(r,2,TextItem(f"{row['etapa_codigo']} - {row['etapa_descricao']}"))
            self.table.setItem(r,3,TextItem(f"{row['grupo_codigo']} - {row['grupo_descricao']}"))
            self.table.setItem(r,4,TextItem(f"{row['entregavel_codigo']} - {row['entregavel_descricao']}"))
            self.table.setItem(r,5,CurrencyItem(row["valor_previsto_mes"]))
            self.table.setItem(r,6,CurrencyItem(row["valor_realizado_mes"]))
            self.table.setItem(r,7,CurrencyItem(saldo))
            self.table.setItem(r,8,FloatItem(row["percentual_previsto_mes"]))
            self.table.setItem(r,9,FloatItem(row["percentual_realizado_mes"]))
        self.table.setSortingEnabled(True)
        self.lbl.setText(f"Registros: {len(rows)} | Saldo total: {br_number(saldo_total,2)}")
