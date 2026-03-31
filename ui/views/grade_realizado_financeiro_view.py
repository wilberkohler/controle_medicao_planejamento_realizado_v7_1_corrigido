from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from ui.widgets.common import configure_table, friendly_error

class GradeRealizadoFinanceiroView(QWidget):
    data_changed = Signal()

    def __init__(self, service):
        super().__init__()
        self.service = service
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        title = QLabel('Lançamentos em Grade - Realizado Financeiro')
        title.setStyleSheet('font-size:18px; font-weight:700;')
        root.addWidget(title)
        info = QLabel('Use para lançar várias medições/entregáveis rapidamente. Campos mínimos: contrato ID, medição ID, etapa ID, grupo ID, entregável ID, competência e valor realizado.')
        info.setWordWrap(True)
        root.addWidget(info)
        bar = QHBoxLayout()
        self.btn_add = QPushButton('Adicionar linha'); self.btn_add.clicked.connect(self.add_row)
        self.btn_save = QPushButton('Salvar linhas válidas'); self.btn_save.clicked.connect(self.save_rows)
        self.btn_load = QPushButton('Carregar últimas 20'); self.btn_load.clicked.connect(self.reload_data)
        for b in [self.btn_add, self.btn_save, self.btn_load]: bar.addWidget(b)
        bar.addStretch(); root.addLayout(bar)
        self.table = QTableWidget(0,10)
        self.table.setHorizontalHeaderLabels(['Contrato ID','Medição ID','Etapa ID','Grupo ID','Entregável ID','Competência','Valor Realizado','% Realizado','Data','Responsável'])
        configure_table(self.table)
        self.table.setEditTriggers(self.table.EditTrigger.AllEditTriggers)
        root.addWidget(self.table)
        for _ in range(8): self.add_row()

    def add_row(self, data=None):
        vals = data or {}
        r = self.table.rowCount(); self.table.insertRow(r)
        defaults=[vals.get('contrato_id',''), vals.get('medicao_id',''), vals.get('etapa_id',''), vals.get('grupo_id',''), vals.get('entregavel_id',''), vals.get('competencia',''), vals.get('valor_realizado_mes',''), vals.get('percentual_realizado_mes',''), vals.get('data_lancamento',''), vals.get('responsavel','')]
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
            data={
                'contrato_id': int(vals[0]) if vals[0].isdigit() else 0,
                'medicao_id': int(vals[1]) if vals[1].isdigit() else 0,
                'etapa_id': int(vals[2]) if vals[2].isdigit() else 0,
                'grupo_id': int(vals[3]) if vals[3].isdigit() else 0,
                'entregavel_id': int(vals[4]) if vals[4].isdigit() else 0,
                'competencia': vals[5],
                'valor_realizado_mes': vals[6],
                'percentual_realizado_mes': vals[7],
                'data_lancamento': vals[8],
                'responsavel': vals[9],
                'fonte': 'grade',
                'observacoes': '',
            }
            try:
                self.service.create(data); ok += 1
            except Exception as exc:
                errs.append(f"Linha {r+1}: {friendly_error(exc)}")
        msg=f"Linhas salvas: {ok}."
        if errs:
            msg += "\n\nProblemas encontrados:\n- " + "\n- ".join(errs[:8])
        QMessageBox.information(self, 'Resultado do lançamento em grade', msg)
        self.reload_data(); self.data_changed.emit()
