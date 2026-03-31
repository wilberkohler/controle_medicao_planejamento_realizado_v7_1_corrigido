from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QTableWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import csv
from ui.widgets.common import configure_table
from ui.widgets.table_items import TextItem, CurrencyItem

class ExportacaoAnualView(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.rows_contrato = []
        self.rows_mensal = []
        self.rows_categoria = []
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        title = QLabel("Exportação Anual Consolidada")
        title.setStyleSheet("font-size:18px;font-weight:700;")
        root.addWidget(title)

        bar = QHBoxLayout()
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self.reload_data)
        self.btn_contrato = QPushButton("Exportar contratos CSV")
        self.btn_contrato.clicked.connect(lambda: self.exportar_csv("contratos"))
        self.btn_mensal = QPushButton("Exportar mensal CSV")
        self.btn_mensal.clicked.connect(lambda: self.exportar_csv("mensal"))
        self.btn_categoria = QPushButton("Exportar categorias CSV")
        self.btn_categoria.clicked.connect(lambda: self.exportar_csv("categorias"))
        for b in [self.btn_atualizar, self.btn_contrato, self.btn_mensal, self.btn_categoria]:
            bar.addWidget(b)
        bar.addStretch()
        root.addLayout(bar)

        charts = QHBoxLayout()
        self.fig1 = Figure(figsize=(6,3.1)); self.canvas1 = FigureCanvas(self.fig1)
        self.fig2 = Figure(figsize=(6,3.1)); self.canvas2 = FigureCanvas(self.fig2)
        charts.addWidget(self.canvas1); charts.addWidget(self.canvas2)
        root.addLayout(charts)

        root.addWidget(QLabel("Resumo anual por contrato"))
        self.table1 = QTableWidget(0, 7)
        self.table1.setHorizontalHeaderLabels(["Contrato","Nome","Receita Faturada","Custo Equipe","Custo Terceiros","Desp. Previstas","Desp. Realizadas"])
        configure_table(self.table1)
        root.addWidget(self.table1)

        root.addWidget(QLabel("Resumo mensal consolidado"))
        self.table2 = QTableWidget(0, 5)
        self.table2.setHorizontalHeaderLabels(["Competência","Receita Faturada","Custo Equipe","Custo Terceiros","Desp. Realizadas"])
        configure_table(self.table2)
        root.addWidget(self.table2)

        root.addWidget(QLabel("Despesas por categoria"))
        self.table3 = QTableWidget(0, 3)
        self.table3.setHorizontalHeaderLabels(["Categoria","Desp. Previstas","Desp. Realizadas"])
        configure_table(self.table3)
        root.addWidget(self.table3)

        note = QLabel("Este painel foi pensado para apoio ao contador e ao planejamento anual, com visão por contrato, por mês e por categoria de despesa.")
        note.setWordWrap(True)
        root.addWidget(note)

    def reload_data(self):
        self.rows_contrato = self.service.resumo_contabil()
        self.rows_mensal = self.service.resumo_anual_mensal()
        self.rows_categoria = self.service.resumo_anual_categorias()

        self.table1.setRowCount(0)
        for row in self.rows_contrato:
            r = self.table1.rowCount(); self.table1.insertRow(r)
            self.table1.setItem(r,0,TextItem(row["contrato_codigo"]))
            self.table1.setItem(r,1,TextItem(row["contrato_nome"]))
            self.table1.setItem(r,2,CurrencyItem(row["receita_faturada"]))
            self.table1.setItem(r,3,CurrencyItem(row["custo_equipe"]))
            self.table1.setItem(r,4,CurrencyItem(row["custo_terceiros"]))
            self.table1.setItem(r,5,CurrencyItem(row["despesas_previstas"]))
            self.table1.setItem(r,6,CurrencyItem(row["despesas_realizadas"]))

        self.table2.setRowCount(0)
        for row in self.rows_mensal:
            r = self.table2.rowCount(); self.table2.insertRow(r)
            self.table2.setItem(r,0,TextItem(row["competencia"]))
            self.table2.setItem(r,1,CurrencyItem(row["receita_faturada"]))
            self.table2.setItem(r,2,CurrencyItem(row["custo_equipe"]))
            self.table2.setItem(r,3,CurrencyItem(row["custo_terceiros"]))
            self.table2.setItem(r,4,CurrencyItem(row["despesas_realizadas"]))

        self.table3.setRowCount(0)
        for row in self.rows_categoria:
            r = self.table3.rowCount(); self.table3.insertRow(r)
            self.table3.setItem(r,0,TextItem(row["categoria"]))
            self.table3.setItem(r,1,CurrencyItem(row["despesas_previstas"]))
            self.table3.setItem(r,2,CurrencyItem(row["despesas_realizadas"]))

        self._plot_mensal()
        self._plot_categorias()

    def _plot_mensal(self):
        self.fig1.clear()
        ax = self.fig1.add_subplot(111)
        labels = [r["competencia"] for r in self.rows_mensal[:15]]
        rec = [float(r["receita_faturada"] or 0) for r in self.rows_mensal[:15]]
        cus = [float(r["custo_equipe"] or 0) + float(r["custo_terceiros"] or 0) + float(r["despesas_realizadas"] or 0) for r in self.rows_mensal[:15]]
        x = list(range(len(labels)))
        ax.plot(x, rec, marker="o", label="Receita")
        ax.plot(x, cus, marker="o", label="Custos + despesas")
        ax.set_title("Receita x custos ao longo do ano")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=35, ha="right")
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend()
        self.fig1.tight_layout(); self.canvas1.draw()

    def _plot_categorias(self):
        self.fig2.clear()
        ax = self.fig2.add_subplot(111)
        labels = [r["categoria"] for r in self.rows_categoria[:12]]
        vals = [float(r["despesas_realizadas"] or 0) for r in self.rows_categoria[:12]]
        ax.barh(range(len(labels)), vals)
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels)
        ax.set_title("Despesas realizadas por categoria")
        ax.grid(True, axis="x", alpha=0.3)
        self.fig2.tight_layout(); self.canvas2.draw()

    def exportar_csv(self, modo):
        default_name = {
            "contratos": "resumo_anual_contratos.csv",
            "mensal": "resumo_anual_mensal.csv",
            "categorias": "resumo_anual_categorias.csv",
        }[modo]
        path, _ = QFileDialog.getSaveFileName(self, "Salvar exportação", default_name, "CSV (*.csv)")
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path += ".csv"
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, delimiter=";")
                if modo == "contratos":
                    w.writerow(["Contrato","Nome","Receita Faturada","Custo Equipe","Custo Terceiros","Despesas Previstas","Despesas Realizadas"])
                    for r in self.rows_contrato:
                        w.writerow([r["contrato_codigo"], r["contrato_nome"], r["receita_faturada"], r["custo_equipe"], r["custo_terceiros"], r["despesas_previstas"], r["despesas_realizadas"]])
                elif modo == "mensal":
                    w.writerow(["Competência","Receita Faturada","Custo Equipe","Custo Terceiros","Despesas Realizadas"])
                    for r in self.rows_mensal:
                        w.writerow([r["competencia"], r["receita_faturada"], r["custo_equipe"], r["custo_terceiros"], r["despesas_realizadas"]])
                else:
                    w.writerow(["Categoria","Despesas Previstas","Despesas Realizadas"])
                    for r in self.rows_categoria:
                        w.writerow([r["categoria"], r["despesas_previstas"], r["despesas_realizadas"]])
            QMessageBox.information(self, "Sucesso", f"CSV exportado para:\n{path}")
        except Exception as exc:
            QMessageBox.warning(self, "Erro", str(exc))
