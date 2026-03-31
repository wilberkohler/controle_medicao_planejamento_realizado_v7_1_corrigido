from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ui.widgets.common import configure_table
from ui.widgets.table_items import TextItem, CurrencyItem, FloatItem

class ProdutividadeDashboardView(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        title = QLabel("Dashboard de produtividade econômica")
        title.setStyleSheet("font-size:18px;font-weight:700;")
        root.addWidget(title)

        top = QHBoxLayout()
        top.addWidget(QLabel("Contrato:"))
        self.cb_contrato = QComboBox()
        self.cb_contrato.currentIndexChanged.connect(self.reload_data)
        top.addWidget(self.cb_contrato)

        top.addWidget(QLabel("Margem por:"))
        self.cb_nivel = QComboBox()
        self.cb_nivel.addItems(["contrato", "etapa", "grupo"])
        self.cb_nivel.currentIndexChanged.connect(self.reload_data)
        top.addWidget(self.cb_nivel)
        top.addStretch()
        root.addLayout(top)

        cards = QHBoxLayout()
        self.lbl_meta = self._card("Meta A1", "0")
        self.lbl_prod = self._card("Produzido A1", "0")
        self.lbl_receita_prev = self._card("Receita Prevista", "0,00")
        self.lbl_receita_real = self._card("Receita Faturada", "0,00")
        self.lbl_custo_eq = self._card("Custo Equipe", "0,00")
        self.lbl_custo_ext = self._card("Consult./Terceiros", "0,00")
        self.lbl_margem = self._card("Margem Total", "0,00")
        for c in [self.lbl_meta, self.lbl_prod, self.lbl_receita_prev, self.lbl_receita_real, self.lbl_custo_eq, self.lbl_custo_ext, self.lbl_margem]:
            cards.addWidget(c)
        root.addLayout(cards)

        row = QHBoxLayout()
        self.fig1 = Figure(figsize=(5.5,3.2)); self.canvas1 = FigureCanvas(self.fig1)
        self.fig2 = Figure(figsize=(5.5,3.2)); self.canvas2 = FigureCanvas(self.fig2)
        row.addWidget(self.canvas1); row.addWidget(self.canvas2)
        root.addLayout(row)

        row2 = QHBoxLayout()
        self.fig3 = Figure(figsize=(5.5,3.2)); self.canvas3 = FigureCanvas(self.fig3)
        self.fig4 = Figure(figsize=(5.5,3.2)); self.canvas4 = FigureCanvas(self.fig4)
        row2.addWidget(self.canvas3); row2.addWidget(self.canvas4)
        root.addLayout(row2)

        root.addWidget(QLabel("Ranking de projetistas"))
        self.table_rank = QTableWidget(0,8)
        self.table_rank.setHorizontalHeaderLabels(["Projetista","Disciplina","Produzido A1","Horas equipe","Produtividade A1/h","Receita Faturada","Custo Equipe","Margem"])
        configure_table(self.table_rank)
        root.addWidget(self.table_rank)

        root.addWidget(QLabel("Margem por estrutura"))
        self.table_struct = QTableWidget(0,7)
        self.table_struct.setHorizontalHeaderLabels(["Nível","Receita Prev.","Receita Fat.","Custo Equipe","Custo Terceiros","Custo Total","Margem"])
        configure_table(self.table_struct)
        root.addWidget(self.table_struct)

        root.addWidget(QLabel("Maiores desvios de receita / margem"))
        self.table_dev = QTableWidget(0,9)
        self.table_dev.setHorizontalHeaderLabels(["Contrato","Etapa","Grupo","Entregável","Meta A1","Prod. A1","Rec. Prev.","Rec. Fat.","Margem"])
        configure_table(self.table_dev)
        root.addWidget(self.table_dev)

    def _card(self, title, value):
        lbl = QLabel(f"{title}\n{value}")
        lbl.setStyleSheet("border:1px solid #cccccc; border-radius:8px; padding:10px; font-size:14px; background:#f8f8f8;")
        return lbl

    def _fmt(self, v):
        try:
            return f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
        except Exception:
            return str(v)

    def reload_data(self):
        cur = self.cb_contrato.currentData()
        self.cb_contrato.blockSignals(True)
        self.cb_contrato.clear(); self.cb_contrato.addItem("Todos", None)
        for c in self.service.contratos():
            self.cb_contrato.addItem(f"{c['codigo']} - {c['nome']}", c["id"])
        idx = self.cb_contrato.findData(cur); self.cb_contrato.setCurrentIndex(idx if idx >= 0 else 0)
        self.cb_contrato.blockSignals(False)

        cid = self.cb_contrato.currentData()
        nivel = self.cb_nivel.currentText()

        resumo = self.service.resumo(cid)
        self.lbl_meta.setText(f"Meta A1\n{self._fmt(resumo['meta_a1'])}")
        self.lbl_prod.setText(f"Produzido A1\n{self._fmt(resumo['produzido_a1'])}")
        self.lbl_receita_prev.setText(f"Receita Prevista\n{self._fmt(resumo['receita_prevista'])}")
        self.lbl_receita_real.setText(f"Receita Faturada\n{self._fmt(resumo['receita_faturada'])}")
        self.lbl_custo_eq.setText(f"Custo Equipe\n{self._fmt(resumo['custo_equipe_apropriado'])}")
        self.lbl_custo_ext.setText(f"Consult./Terceiros\n{self._fmt(resumo['custo_terceiros'])}")
        self.lbl_margem.setText(f"Margem Total\n{self._fmt(resumo['margem_total'])}")

        comp_rows = self.service.comparativo_competencia(cid)
        disc_rows = self.service.por_disciplina(cid)
        rank_rows = self.service.ranking_projetistas(cid)
        struct_rows = self.service.margem_por_estrutura(nivel, cid)
        dev_rows = self.service.top_desvios_estrutura(cid, 12)

        self._plot_competencia(comp_rows)
        self._plot_disciplina_margin(disc_rows)
        self._plot_structure_margin(struct_rows, nivel)
        self._plot_hours_vs_prod(rank_rows)
        self._fill_rank(rank_rows)
        self._fill_structure(struct_rows)
        self._fill_deviations(dev_rows)

    def _plot_competencia(self, rows):
        self.fig1.clear(); ax = self.fig1.add_subplot(111)
        comps = [r["competencia"] for r in rows]
        rp = [float(r["receita_prevista"] or 0) for r in rows]
        rr = [float(r["receita_faturada"] or 0) for r in rows]
        ce = [float(r["custo_equipe"] or 0) for r in rows]
        ct = [float(r["custo_terceiros"] or 0) for r in rows]
        x = list(range(len(comps)))
        ax.plot(x, rp, marker="o", label="Receita prevista")
        ax.plot(x, rr, marker="o", label="Receita faturada")
        ax.plot(x, ce, marker="o", label="Custo equipe")
        ax.plot(x, ct, marker="o", label="Custos ext.")
        ax.set_title("Receita x custos por competência")
        ax.set_xticks(x); ax.set_xticklabels(comps, rotation=35, ha="right")
        ax.grid(True, axis="y", alpha=0.3); ax.legend()
        self.fig1.tight_layout(); self.canvas1.draw()

    def _plot_disciplina_margin(self, rows):
        self.fig2.clear(); ax = self.fig2.add_subplot(111)
        labels = [r["disciplina"] for r in rows]
        margem = [float(r["receita_faturada"] or 0) - float(r["custo_total"] or 0) for r in rows]
        ax.bar(range(len(labels)), margem)
        ax.set_title("Margem por disciplina")
        ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, rotation=35, ha="right")
        ax.grid(True, axis="y", alpha=0.3)
        self.fig2.tight_layout(); self.canvas2.draw()

    def _plot_structure_margin(self, rows, nivel):
        self.fig3.clear(); ax = self.fig3.add_subplot(111)
        labels = [r["nivel"] for r in rows[:10]]
        margem = [float(r["margem"] or 0) for r in rows[:10]]
        ax.barh(range(len(labels)), margem)
        ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels)
        ax.set_title(f"Margem por {nivel}")
        ax.grid(True, axis="x", alpha=0.3)
        self.fig3.tight_layout(); self.canvas3.draw()

    def _plot_hours_vs_prod(self, rows):
        self.fig4.clear(); ax = self.fig4.add_subplot(111)
        rows = rows[:10]
        labels = [r["projetista"] for r in rows]
        horas = [float(r["horas_equipe"] or 0) for r in rows]
        prod = [float(r["produzido_a1"] or 0) for r in rows]
        x = list(range(len(labels)))
        ax.bar([i - 0.2 for i in x], horas, width=0.4, label="Horas equipe")
        ax.bar([i + 0.2 for i in x], prod, width=0.4, label="Produzido A1")
        ax.set_title("Horas x produção por projetista")
        ax.set_xticks(x); ax.set_xticklabels(labels, rotation=35, ha="right")
        ax.grid(True, axis="y", alpha=0.3); ax.legend()
        self.fig4.tight_layout(); self.canvas4.draw()

    def _fill_rank(self, rows):
        self.table_rank.setSortingEnabled(False); self.table_rank.setRowCount(0)
        for row in rows:
            r = self.table_rank.rowCount(); self.table_rank.insertRow(r)
            self.table_rank.setItem(r,0,TextItem(row["projetista"]))
            self.table_rank.setItem(r,1,TextItem(row["disciplina"]))
            self.table_rank.setItem(r,2,FloatItem(row["produzido_a1"],2))
            self.table_rank.setItem(r,3,FloatItem(row["horas_equipe"],2))
            self.table_rank.setItem(r,4,FloatItem(row["produtividade_a1_h"],4))
            self.table_rank.setItem(r,5,CurrencyItem(row["receita_faturada"]))
            self.table_rank.setItem(r,6,CurrencyItem(row["custo_equipe"]))
            self.table_rank.setItem(r,7,CurrencyItem(row["margem_equipe"]))
        self.table_rank.setSortingEnabled(True)

    def _fill_structure(self, rows):
        self.table_struct.setSortingEnabled(False); self.table_struct.setRowCount(0)
        for row in rows:
            r = self.table_struct.rowCount(); self.table_struct.insertRow(r)
            self.table_struct.setItem(r,0,TextItem(row["nivel"]))
            self.table_struct.setItem(r,1,CurrencyItem(row["receita_prevista"]))
            self.table_struct.setItem(r,2,CurrencyItem(row["receita_faturada"]))
            self.table_struct.setItem(r,3,CurrencyItem(row["custo_equipe"]))
            self.table_struct.setItem(r,4,CurrencyItem(row["custo_terceiros"]))
            self.table_struct.setItem(r,5,CurrencyItem(row["custo_total"]))
            self.table_struct.setItem(r,6,CurrencyItem(row["margem"]))
        self.table_struct.setSortingEnabled(True)

    def _fill_deviations(self, rows):
        self.table_dev.setSortingEnabled(False); self.table_dev.setRowCount(0)
        for row in rows:
            r = self.table_dev.rowCount(); self.table_dev.insertRow(r)
            self.table_dev.setItem(r,0,TextItem(row["contrato_codigo"]))
            self.table_dev.setItem(r,1,TextItem(row["etapa_codigo"]))
            self.table_dev.setItem(r,2,TextItem(row["grupo_codigo"]))
            self.table_dev.setItem(r,3,TextItem(f"{row['entregavel_codigo']} - {row['entregavel_descricao']}"))
            self.table_dev.setItem(r,4,FloatItem(row["meta_a1"],2))
            self.table_dev.setItem(r,5,FloatItem(row["produzido_a1"],2))
            self.table_dev.setItem(r,6,CurrencyItem(row["receita_prevista"]))
            self.table_dev.setItem(r,7,CurrencyItem(row["receita_faturada"]))
            self.table_dev.setItem(r,8,CurrencyItem(row["margem"]))
        self.table_dev.setSortingEnabled(True)
