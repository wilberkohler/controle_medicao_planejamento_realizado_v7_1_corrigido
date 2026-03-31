from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ui.widgets.common import configure_table
from ui.widgets.table_items import TextItem, CurrencyItem

class _BaseOficialView(QWidget):
    def _fmt(self, v):
        try:
            return f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
        except Exception:
            return str(v)
    def _card(self, title, value):
        lbl = QLabel(f"{title}\n{value}")
        lbl.setStyleSheet("border:1px solid #cccccc; border-radius:8px; padding:10px; font-size:13px; background:#f8f8f8;")
        return lbl
    def _reload_contracts(self, cb, service):
        cur = cb.currentData()
        cb.blockSignals(True)
        cb.clear(); cb.addItem("Todos", None)
        for c in service.dashboard_contracts_detail():
            cb.addItem(f"{c['contrato_codigo']} - {c['contrato_nome']}", c["contrato_id"])
        idx = cb.findData(cur)
        cb.setCurrentIndex(idx if idx >= 0 else 0)
        cb.blockSignals(False)
