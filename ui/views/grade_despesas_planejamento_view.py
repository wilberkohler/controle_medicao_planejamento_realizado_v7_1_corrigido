from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from ui.widgets.common import configure_table, friendly_error

CATEGORIAS = ["Viagens","Combustível","Hospedagem","Alimentação","Software","Plotagem","Impressões","Veículos","Passagens","Taxas","Cartório","Outros"]

class GradeDespesasPlanejamentoView(QWidget):
    data_changed = Signal()

    def __init__(self, service):
        super().__init__()
        self.service = service
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        title = QLabel('Lançamentos em Grade - Despesas Planejadas')
        title.setStyleSheet('font-size:18px; font-weight:700;')
        root.addWidget(title)
        info = QLabel('Use esta grade para montar o orçamento mensal de despesas como viagens, software, hospedagem e outros. Campos mínimos: competência, categoria e valor previsto.')
        info.setWordWrap(True)
        root.addWidget(info)
        bar = QHBoxLayout()
        self.btn_add = QPushButton('Adicionar linha'); self.btn_add.clicked.connect(self.add_row)
        self.btn_save = QPushButton('Salvar linhas válidas'); self.btn_save.clicked.connect(self.save_rows)
        self.btn_load = QPushButton('Carregar últimas 20'); self.btn_load.clicked.connect(self.reload_data)
        for b in [self.btn_add, self.btn_save, self.btn_load]: bar.addWidget(b)
        bar.addStretch(); root.addLayout(bar)
        self.table = QTableWidget(0,8)
        self.table.setHorizontalHeaderLabels(['Contrato ID(opc.)','Competência','Categoria','Descrição','Fornecedor','Valor Previsto','Centro Custo','Observações'])
        configure_table(self.table)
        self.table.setEditTriggers(self.table.EditTrigger.AllEditTriggers)
        root.addWidget(self.table)
        for _ in range(8): self.add_row()

    def add_row(self, data=None):
        vals = data or {}
        r = self.table.rowCount(); self.table.insertRow(r)
        defaults=[vals.get('contrato_id',''), vals.get('competencia',''), vals.get('categoria',''), vals.get('descricao',''), vals.get('fornecedor',''), vals.get('valor_previsto',''), vals.get('centro_custo',''), vals.get('observacoes','')]
        for c,v in enumerate(defaults): self.table.setItem(r,c,QTableWidgetItem(str(v)))

    def reload_data(self):
        rows = self.service.list_all()[:20]
        self.table.setRowCount(0)
        for row in rows: self.add_row(row)
        for _ in range(max(0, 8-len(rows))): self.add_row()

    def save_rows(self):
        ok = 0; errs = []
        for r in range(self.table.rowCount()):
            vals=[self.table.item(r,c).text().strip() if self.table.item(r,c) else '' for c in range(self.table.columnCount())]
            if not any(vals):
                continue
            data={'contrato_id': int(vals[0]) if vals[0].isdigit() else None, 'competencia': vals[1], 'categoria': vals[2], 'descricao': vals[3], 'fornecedor': vals[4], 'valor_previsto': vals[5], 'centro_custo': vals[6], 'observacoes': vals[7]}
            try:
                self.service.create(data); ok += 1
            except Exception as exc:
                errs.append(f"Linha {r+1}: {friendly_error(exc)}")
        msg=f"Linhas salvas: {ok}."
        if errs:
            msg += "\n\nProblemas encontrados:\n- " + "\n- ".join(errs[:8])
        QMessageBox.information(self, 'Resultado do lançamento em grade', msg)
        self.reload_data(); self.data_changed.emit()
