from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QTreeWidget, QTreeWidgetItem, QPushButton, QHBoxLayout, QTextEdit
from repositories.domain_repositories import ContratoRepository, EtapaRepository, GrupoRepository, EntregavelRepository
from services.domain_services import AnalyticsService
from repositories.analytics_repository import AnalyticsRepository
from utils.number_utils import br_number

class EstruturaArvoreView(QWidget):
    def __init__(self):
        super().__init__()
        self.contrato_repo = ContratoRepository()
        self.etapa_repo = EtapaRepository()
        self.grupo_repo = GrupoRepository()
        self.entregavel_repo = EntregavelRepository()
        self.analytics = AnalyticsService(AnalyticsRepository())
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Estrutura do contrato em árvore")
        title.setStyleSheet("font-size:18px;font-weight:600;")
        layout.addWidget(title)

        top = QHBoxLayout()
        self.cb_contrato = QComboBox()
        self.cb_contrato.currentIndexChanged.connect(self.reload_tree)
        self.btn_expandir = QPushButton("Expandir tudo")
        self.btn_recolher = QPushButton("Recolher tudo")
        self.btn_expandir.clicked.connect(lambda: self.tree.expandAll())
        self.btn_recolher.clicked.connect(lambda: self.tree.collapseAll())
        top.addWidget(QLabel("Contrato:"))
        top.addWidget(self.cb_contrato)
        top.addWidget(self.btn_expandir)
        top.addWidget(self.btn_recolher)
        top.addStretch()
        layout.addLayout(top)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Estrutura", "Tipo", "Código", "Descrição"])
        self.tree.itemClicked.connect(self.show_details)
        layout.addWidget(self.tree)

        self.detail = QTextEdit()
        self.detail.setReadOnly(True)
        layout.addWidget(self.detail)

    def reload_data(self):
        current = self.cb_contrato.currentData()
        self.cb_contrato.blockSignals(True)
        self.cb_contrato.clear()
        for c in self.contrato_repo.list_all():
            self.cb_contrato.addItem(f"{c['codigo']} - {c['nome']}", c["id"])
        idx = self.cb_contrato.findData(current)
        self.cb_contrato.setCurrentIndex(idx if idx >= 0 and self.cb_contrato.count() > 0 else 0)
        self.cb_contrato.blockSignals(False)
        self.reload_tree()

    def reload_tree(self):
        self.tree.clear()
        self.detail.clear()
        contrato_id = self.cb_contrato.currentData()
        if contrato_id is None:
            return

        contrato = self.contrato_repo.get_by_id(contrato_id)
        root = QTreeWidgetItem([f"{contrato['codigo']} - {contrato['nome']}", "Contrato", contrato["codigo"], contrato["nome"]])
        root.setData(0, 32, {"tipo": "Contrato", "codigo": contrato["codigo"], "descricao": contrato["nome"]})
        self.tree.addTopLevelItem(root)

        etapas = self.etapa_repo.list_by_contrato(contrato_id)
        for e in etapas:
            item_e = QTreeWidgetItem([f"{e['codigo']} - {e['descricao']}", "Etapa", e["codigo"], e["descricao"]])
            item_e.setData(0, 32, {"tipo": "Etapa", "codigo": e["codigo"], "descricao": e["descricao"]})
            root.addChild(item_e)
            grupos = self.grupo_repo.list_by_etapa(e["id"])
            for g in grupos:
                item_g = QTreeWidgetItem([f"{g['codigo']} - {g['descricao']}", "Grupo", g["codigo"], g["descricao"]])
                item_g.setData(0, 32, {"tipo": "Grupo", "codigo": g["codigo"], "descricao": g["descricao"]})
                item_e.addChild(item_g)
                ents = self.entregavel_repo.list_by_grupo(g["id"])
                for ent in ents:
                    item_ent = QTreeWidgetItem([f"{ent['codigo']} - {ent['descricao']}", "Entregável", ent["codigo"], ent["descricao"]])
                    item_ent.setData(0, 32, {"tipo": "Entregável", "codigo": ent["codigo"], "descricao": ent["descricao"]})
                    item_g.addChild(item_ent)

        self.tree.expandToDepth(1)

    def show_details(self, item):
        data = item.data(0, 32) or {}
        tipo = data.get("tipo", "")
        codigo = data.get("codigo", "")
        desc = data.get("descricao", "")
        self.detail.setPlainText(f"Tipo: {tipo}\nCódigo: {codigo}\nDescrição: {desc}\n\nDica: use esta árvore para drill-down visual da estrutura do contrato.")
