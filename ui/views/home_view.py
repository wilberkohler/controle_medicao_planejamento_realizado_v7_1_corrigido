from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget
from ui.widgets.common import configure_table, make_status_item
from ui.widgets.table_items import TextItem, CurrencyItem

class HomeView(QWidget):
    navigate_requested = Signal(str)

    def __init__(self, service):
        super().__init__()
        self.service = service
        self._build_ui()
        self.reload_data()

    def _card(self, title, value):
        lbl = QLabel(f"{title}\n{value}")
        lbl.setStyleSheet("border:1px solid #d1d5db; border-radius:10px; padding:10px; background:white; font-size:14px; font-weight:600;")
        lbl.setMinimumWidth(150)
        return lbl

    def _build_ui(self):
        root = QVBoxLayout(self)
        title = QLabel('Central de Trabalho')
        title.setStyleSheet('font-size:22px; font-weight:800; color:#123c67;')
        root.addWidget(title)
        cards = QHBoxLayout()
        self.lbl_pend = self._card('Pendências do mês', '0')
        self.lbl_comp = self._card('Competências abertas', '0')
        self.lbl_aprov = self._card('Itens aguardando aprovação', '0')
        self.lbl_div = self._card('Desvios críticos', '0')
        for w in [self.lbl_pend, self.lbl_comp, self.lbl_aprov, self.lbl_div]:
            cards.addWidget(w)
        root.addLayout(cards)
        quick = QHBoxLayout()
        quick.addWidget(QLabel('Atalhos rápidos:'))
        for page in ['Medições','Realizado','Prod. Receita','Desp. Realizado','DRE Gerencial','Exportação Excel']:
            btn = QPushButton(page)
            btn.clicked.connect(lambda _=False, p=page: self.navigate_requested.emit(p))
            quick.addWidget(btn)
        quick.addStretch()
        root.addLayout(quick)
        row = QHBoxLayout()
        self.tbl_comp = QTableWidget(0,3)
        self.tbl_comp.setHorizontalHeaderLabels(['Competência','Status','Qtde'])
        configure_table(self.tbl_comp)
        row.addWidget(self.tbl_comp)
        self.tbl_pending = QTableWidget(0,4)
        self.tbl_pending.setHorizontalHeaderLabels(['Módulo','Registro','Status','Referência'])
        configure_table(self.tbl_pending)
        row.addWidget(self.tbl_pending)
        root.addLayout(row)
        row2 = QHBoxLayout()
        self.tbl_dev = QTableWidget(0,6)
        self.tbl_dev.setHorizontalHeaderLabels(['Contrato','Etapa','Grupo','Entregável','Competência','Saldo'])
        configure_table(self.tbl_dev)
        row2.addWidget(self.tbl_dev)
        self.tbl_last = QTableWidget(0,5)
        self.tbl_last.setHorizontalHeaderLabels(['Origem','Registro','Competência','Responsável','Detalhe'])
        configure_table(self.tbl_last)
        row2.addWidget(self.tbl_last)
        root.addLayout(row2)

    def reload_data(self):
        s = self.service.home_summary()
        self.lbl_pend.setText(f"Pendências do mês\n{s['pendencias_mes']}")
        self.lbl_comp.setText(f"Competências abertas\n{s['competencias_abertas']}")
        self.lbl_aprov.setText(f"Itens aguardando aprovação\n{s['pendencias_mes']}")
        self.lbl_div.setText(f"Desvios críticos\n{s['itens_divergentes']}")
        self.tbl_comp.setRowCount(0)
        for row in self.service.open_competencias()[:20]:
            r = self.tbl_comp.rowCount(); self.tbl_comp.insertRow(r)
            self.tbl_comp.setItem(r,0,TextItem(row['competencia']))
            self.tbl_comp.setItem(r,1,make_status_item(row['status']))
            self.tbl_comp.setItem(r,2,TextItem(str(row['qtde'])))
        self.tbl_pending.setRowCount(0)
        for row in self.service.pending_items()[:20]:
            r = self.tbl_pending.rowCount(); self.tbl_pending.insertRow(r)
            self.tbl_pending.setItem(r,0,TextItem(row['modulo']))
            self.tbl_pending.setItem(r,1,TextItem(str(row['registro_id'])))
            self.tbl_pending.setItem(r,2,make_status_item(row['status']))
            self.tbl_pending.setItem(r,3,TextItem(row['referencia'] or ''))
        self.tbl_dev.setRowCount(0)
        for row in self.service.critical_deviations()[:20]:
            r = self.tbl_dev.rowCount(); self.tbl_dev.insertRow(r)
            self.tbl_dev.setItem(r,0,TextItem(row['contrato_codigo']))
            self.tbl_dev.setItem(r,1,TextItem(row['etapa_codigo']))
            self.tbl_dev.setItem(r,2,TextItem(row['grupo_codigo']))
            self.tbl_dev.setItem(r,3,TextItem(row['entregavel_codigo']))
            self.tbl_dev.setItem(r,4,TextItem(row['competencia'] or ''))
            self.tbl_dev.setItem(r,5,CurrencyItem(row['saldo']))
        self.tbl_last.setRowCount(0)
        for row in self.service.latest_launches()[:20]:
            r = self.tbl_last.rowCount(); self.tbl_last.insertRow(r)
            self.tbl_last.setItem(r,0,TextItem(row['origem']))
            self.tbl_last.setItem(r,1,TextItem(row['registro']))
            self.tbl_last.setItem(r,2,TextItem(row['competencia'] or ''))
            self.tbl_last.setItem(r,3,TextItem(row['responsavel'] or ''))
            self.tbl_last.setItem(r,4,TextItem(row['detalhe'] or ''))
