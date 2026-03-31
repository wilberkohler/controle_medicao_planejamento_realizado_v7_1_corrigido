from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QTableWidget
import csv
from ui.widgets.common import configure_table
from ui.widgets.table_items import TextItem, CurrencyItem

class ExportacaoView(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.rows_cache = []
        self._build_ui()
        self.reload_data()
    def _build_ui(self):
        root = QVBoxLayout(self)
        title = QLabel("Centro de Exportação Contábil / Gerencial"); title.setStyleSheet("font-size:18px;font-weight:700;"); root.addWidget(title)
        bar = QHBoxLayout()
        self.btn_atualizar = QPushButton("Atualizar"); self.btn_atualizar.clicked.connect(self.reload_data)
        self.btn_exportar = QPushButton("Exportar resumo CSV"); self.btn_exportar.clicked.connect(self.exportar_csv)
        bar.addWidget(self.btn_atualizar); bar.addWidget(self.btn_exportar); bar.addStretch(); root.addLayout(bar)
        self.table = QTableWidget(0,8); self.table.setHorizontalHeaderLabels(["Contrato","Nome","Receita Faturada","Custo Equipe","Custo Terceiros","Desp. Previstas","Desp. Realizadas","Total Despesas/Custos"]); configure_table(self.table); root.addWidget(self.table)
        note = QLabel("Base de apoio ao contador e ao planejamento anual da empresa. As despesas gerais incluem viagens, combustíveis, hospedagem, alimentação, software, plotagem e outros itens operacionais.")
        note.setWordWrap(True); root.addWidget(note)
    def reload_data(self):
        self.rows_cache = self.service.resumo_contabil(); self.table.setRowCount(0)
        for row in self.rows_cache:
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r,0,TextItem(row["contrato_codigo"])); self.table.setItem(r,1,TextItem(row["contrato_nome"])); self.table.setItem(r,2,CurrencyItem(row["receita_faturada"])); self.table.setItem(r,3,CurrencyItem(row["custo_equipe"])); self.table.setItem(r,4,CurrencyItem(row["custo_terceiros"])); self.table.setItem(r,5,CurrencyItem(row["despesas_previstas"])); self.table.setItem(r,6,CurrencyItem(row["despesas_realizadas"])); self.table.setItem(r,7,CurrencyItem((row["custo_equipe"] or 0) + (row["custo_terceiros"] or 0) + (row["despesas_realizadas"] or 0)))
    def exportar_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar resumo", "resumo_contabil.csv", "CSV (*.csv)")
        if not path: return
        if not path.lower().endswith(".csv"): path += ".csv"
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, delimiter=";")
                w.writerow(["Contrato","Nome","Receita Faturada","Custo Equipe","Custo Terceiros","Despesas Previstas","Despesas Realizadas","Total Despesas/Custos"])
                for row in self.rows_cache:
                    w.writerow([row["contrato_codigo"], row["contrato_nome"], row["receita_faturada"], row["custo_equipe"], row["custo_terceiros"], row["despesas_previstas"], row["despesas_realizadas"], (row["custo_equipe"] or 0) + (row["custo_terceiros"] or 0) + (row["despesas_realizadas"] or 0)])
            QMessageBox.information(self, "Sucesso", f"CSV exportado para:\n{path}")
        except Exception as exc:
            QMessageBox.warning(self, "Erro", str(exc))
