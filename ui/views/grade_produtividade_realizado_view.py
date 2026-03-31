from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from ui.widgets.common import configure_table, friendly_error

class GradeProdutividadeRealizadoView(QWidget):
    data_changed = Signal()

    def __init__(self, service):
        super().__init__()
        self.service = service
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        title = QLabel('Lançamentos em Grade - Produtividade Realizada')
        title.setStyleSheet('font-size:18px; font-weight:700;')
        root.addWidget(title)
        info = QLabel('Ideal para lançar produção mensal em lote. Campos mínimos: usuário ID, contrato ID, competência, disciplina, produzido A1 e receita faturada. Horas por A1 pode ficar em branco para usar o parâmetro da disciplina.')
        info.setWordWrap(True)
        root.addWidget(info)
        bar = QHBoxLayout()
        self.btn_add = QPushButton('Adicionar linha'); self.btn_add.clicked.connect(self.add_row)
        self.btn_save = QPushButton('Salvar linhas válidas'); self.btn_save.clicked.connect(self.save_rows)
        self.btn_load = QPushButton('Carregar últimas 20'); self.btn_load.clicked.connect(self.reload_data)
        for b in [self.btn_add, self.btn_save, self.btn_load]: bar.addWidget(b)
        bar.addStretch(); root.addLayout(bar)
        self.table = QTableWidget(0,12)
        self.table.setHorizontalHeaderLabels(['Usuário ID','Contrato ID','Etapa ID(opc.)','Grupo ID(opc.)','Entregável ID(opc.)','Competência','Disciplina','Produzido A1','Horas por A1','Receita Faturada','Status','Descrição'])
        configure_table(self.table)
        self.table.setEditTriggers(self.table.EditTrigger.AllEditTriggers)
        root.addWidget(self.table)
        for _ in range(8): self.add_row()

    def add_row(self, data=None):
        vals = data or {}
        r = self.table.rowCount(); self.table.insertRow(r)
        defaults=[vals.get('usuario_id',''), vals.get('contrato_id',''), vals.get('etapa_id',''), vals.get('grupo_id',''), vals.get('entregavel_id',''), vals.get('competencia',''), vals.get('disciplina',''), vals.get('produzido_a1',''), vals.get('horas_por_a1',''), vals.get('receita_faturada',''), vals.get('status_aprovacao','rascunho'), vals.get('descricao','')]
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
            def opt_int(v):
                return int(v) if v.isdigit() else None
            data={
                'usuario_id': int(vals[0]) if vals[0].isdigit() else 0,
                'contrato_id': int(vals[1]) if vals[1].isdigit() else 0,
                'etapa_id': opt_int(vals[2]),
                'grupo_id': opt_int(vals[3]),
                'entregavel_id': opt_int(vals[4]),
                'competencia': vals[5],
                'disciplina': vals[6],
                'produzido_a1': vals[7],
                'horas_por_a1': vals[8],
                'receita_faturada': vals[9],
                'status_aprovacao': vals[10] or 'rascunho',
                'descricao': vals[11],
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
