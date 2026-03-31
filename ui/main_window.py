import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget, QVBoxLayout, QLabel, QComboBox, QDialog, QLineEdit
from config.settings import APP_NAME, APP_WIDTH, APP_HEIGHT

from repositories.domain_repositories import (
    ContratoRepository, MedicaoRepository, EtapaRepository, GrupoRepository, EntregavelRepository,
    PlanejamentoCabecalhoRepository, PlanejamentoItemRepository, PlanejamentoMensalRepository,
    RealizadoRepository, AnalyticsRepository
)
from repositories.governance_repositories import UsuarioRepository, HistoricoRepository, WorkflowRepository
from repositories.expenses_repositories import DespesasPlanejamentoRepository, DespesasRealizadoRepository, ExportacaoRepository
from repositories.finance_import_repositories import FinanceiroImportRepository
from repositories.productivity_repositories import (
    ProdutividadeParametroRepository, ProdutividadeMetaRepository, ProdutividadeRealizadoRepository,
    ProdutividadeCustoRepository, ProdutividadeAnalyticsRepository, DREParametrosRepository
)

from services.domain_services import (
    ContratoService, MedicaoService, EtapaService, GrupoService, EntregavelService,
    PlanejamentoCabecalhoService, PlanejamentoItemService, PlanejamentoMensalService,
    RealizadoService, AnalyticsService
)
from services.governance_services import UsuarioService, HistoricoService, WorkflowService, SecurityService
from services.productivity_services import (
    ProdutividadeParametroService, ProdutividadeMetaService, ProdutividadeRealizadoService,
    ProdutividadeCustoService, ProdutividadeAnalyticsService, DREParametrosService
)
from services.app_context import AppContext
from services.expenses_services import DespesasPlanejamentoService, DespesasRealizadoService, ExportacaoService
from services.finance_import_service import FinanceImportService

from ui.views.home_view import HomeView
from ui.views.global_search_view import GlobalSearchView
from ui.views.lancamentos_grade_view import LancamentosGradeView
from ui.views.grade_despesas_planejamento_view import GradeDespesasPlanejamentoView
from ui.views.grade_produtividade_realizado_view import GradeProdutividadeRealizadoView
from ui.views.grade_realizado_financeiro_view import GradeRealizadoFinanceiroView
from ui.views.dashboard_view import DashboardView
from ui.views.contracts_view import ContratosView
from ui.views.medicoes_view import MedicoesView
from ui.views.etapas_view import EtapasView
from ui.views.grupos_view import GruposView
from ui.views.entregaveis_view import EntregaveisView
from ui.views.planejamento_cabecalho_view import PlanejamentoCabecalhoView
from ui.views.planejamento_itens_view import PlanejamentoItensView
from ui.views.planejamento_mensal_view import PlanejamentoMensalView
from ui.views.realizado_view import RealizadoView
from ui.views.comparativo_mensal_view import ComparativoMensalView
from ui.views.comparativo_acumulado_view import ComparativoAcumuladoView
from ui.views.usuarios_view import UsuariosView
from ui.views.historico_view import HistoricoView
from ui.views.workflow_view import WorkflowView
from ui.views.login_view import LoginView
from ui.views.despesas_planejamento_view import DespesasPlanejamentoView
from ui.views.despesas_realizado_view import DespesasRealizadoView
from ui.views.exportacao_view import ExportacaoView
from ui.views.exportacao_anual_view import ExportacaoAnualView
from ui.views.exportacao_excel_view import ExportacaoExcelView
from ui.views.exportacao_oficial_view import ExportacaoOficialView
from ui.views.exportacao_excel_oficial_view import ExportacaoExcelOficialView
from ui.views.importacao_financeira_view import ImportacaoFinanceiraView
from ui.views.painel_ano_vigente_view import PainelAnoVigenteView
from ui.views.painel_12m_view import Painel12MesesView
from ui.views.forecast_anual_view import ForecastAnualView
from ui.views.cockpit_mensal_oficial_view import CockpitMensalOficialView
from ui.widgets.tree_view import EstruturaArvoreView
from ui.views.produtividade_parametros_view import ProdutividadeParametrosView
from ui.views.produtividade_metas_view import ProdutividadeMetasView
from ui.views.produtividade_realizado_view import ProdutividadeRealizadoView
from ui.views.produtividade_custos_view import ProdutividadeCustosView
from ui.views.produtividade_dashboard_view import ProdutividadeDashboardView
from ui.views.produtividade_dre_view import ProdutividadeDREView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(APP_WIDTH, APP_HEIGHT)

        contrato_repo = ContratoRepository(); medicao_repo = MedicaoRepository(); etapa_repo = EtapaRepository(); grupo_repo = GrupoRepository(); entregavel_repo = EntregavelRepository(); plan_repo = PlanejamentoCabecalhoRepository(); plan_item_repo = PlanejamentoItemRepository(); plan_m_repo = PlanejamentoMensalRepository(); realizado_repo = RealizadoRepository(); analytics_repo = AnalyticsRepository(); usuario_repo = UsuarioRepository(); historico_repo = HistoricoRepository(); workflow_repo = WorkflowRepository(); desp_plan_repo = DespesasPlanejamentoRepository(); desp_real_repo = DespesasRealizadoRepository(); export_repo = ExportacaoRepository(); finance_import_repo = FinanceiroImportRepository(); prod_param_repo = ProdutividadeParametroRepository(); prod_meta_repo = ProdutividadeMetaRepository(); prod_real_repo = ProdutividadeRealizadoRepository(); prod_cost_repo = ProdutividadeCustoRepository(); prod_analytics_repo = ProdutividadeAnalyticsRepository(); dre_param_repo = DREParametrosRepository()
        self.usuario_repo = usuario_repo
        self.app_context = AppContext(); self.security = SecurityService()

        contrato_service = ContratoService(contrato_repo, historico_repo=historico_repo, app_context=self.app_context)
        medicao_service = MedicaoService(medicao_repo, contrato_repo, historico_repo=historico_repo, app_context=self.app_context)
        etapa_service = EtapaService(etapa_repo, contrato_repo, historico_repo=historico_repo, app_context=self.app_context)
        grupo_service = GrupoService(grupo_repo, contrato_repo, etapa_repo, historico_repo=historico_repo, app_context=self.app_context)
        entregavel_service = EntregavelService(entregavel_repo, contrato_repo, etapa_repo, grupo_repo, historico_repo=historico_repo, app_context=self.app_context)
        plan_service = PlanejamentoCabecalhoService(plan_repo, contrato_repo, historico_repo=historico_repo, app_context=self.app_context)
        plan_item_service = PlanejamentoItemService(plan_item_repo, plan_repo, contrato_repo, etapa_repo, grupo_repo, entregavel_repo, historico_repo=historico_repo, app_context=self.app_context)
        plan_m_service = PlanejamentoMensalService(plan_m_repo, plan_repo, plan_item_repo, contrato_repo, historico_repo=historico_repo, app_context=self.app_context)
        realizado_service = RealizadoService(realizado_repo, contrato_repo, medicao_repo, etapa_repo, grupo_repo, entregavel_repo, historico_repo=historico_repo, app_context=self.app_context)
        analytics_service = AnalyticsService(analytics_repo)
        usuario_service = UsuarioService(usuario_repo, historico_repo=historico_repo, app_context=self.app_context)
        historico_service = HistoricoService(historico_repo, usuario_repo, app_context=self.app_context)
        workflow_service = WorkflowService(workflow_repo, usuario_repo, historico_repo=historico_repo, app_context=self.app_context)
        despesas_plan_service = DespesasPlanejamentoService(desp_plan_repo, contrato_repo, historico_repo=historico_repo, app_context=self.app_context, table_name='despesas_planejamento')
        despesas_real_service = DespesasRealizadoService(desp_real_repo, contrato_repo, historico_repo=historico_repo, app_context=self.app_context, table_name='despesas_realizado')
        exportacao_service = ExportacaoService(export_repo, analytics_service=analytics_service)
        finance_import_service = FinanceImportService(finance_import_repo, despesas_plan_service, despesas_real_service)
        prod_param_service = ProdutividadeParametroService(prod_param_repo, historico_repo=historico_repo, app_context=self.app_context)
        prod_meta_service = ProdutividadeMetaService(prod_meta_repo, usuario_repo, contrato_repo, etapa_repo, grupo_repo, prod_param_repo, historico_repo=historico_repo, app_context=self.app_context)
        prod_real_service = ProdutividadeRealizadoService(prod_real_repo, usuario_repo, contrato_repo, etapa_repo, grupo_repo, entregavel_repo, prod_param_repo, historico_repo=historico_repo, app_context=self.app_context)
        prod_cost_service = ProdutividadeCustoService(prod_cost_repo, usuario_repo, contrato_repo, etapa_repo, grupo_repo, prod_param_repo, historico_repo=historico_repo, app_context=self.app_context)
        prod_dash_service = ProdutividadeAnalyticsService(prod_analytics_repo, contrato_repo)
        dre_param_service = DREParametrosService(dre_param_repo)

        central = QWidget(); self.setCentralWidget(central); layout = QHBoxLayout(central)
        leftcol = QVBoxLayout(); layout.addLayout(leftcol)
        leftcol.addWidget(QLabel('Usuário ativo'))
        self.cb_usuario = QComboBox(); self.cb_usuario.currentIndexChanged.connect(self.on_user_change); leftcol.addWidget(self.cb_usuario)
        self.lbl_welcome = QLabel(''); self.lbl_welcome.setStyleSheet('font-weight:600; color:#35516f;'); self.lbl_welcome.setWordWrap(True); leftcol.addWidget(self.lbl_welcome)
        leftcol.addWidget(QLabel('Busca global'))
        self.ed_global = QLineEdit(); self.ed_global.setPlaceholderText('Contrato, projetista, competência, categoria, entregável...'); self.ed_global.returnPressed.connect(self.do_global_search); leftcol.addWidget(self.ed_global)
        self.nav = QListWidget(); self.nav.setMaximumWidth(260); self.nav.setStyleSheet('QListWidget{font-size:13px;} QListWidget::item{padding:8px;} QListWidget::item:selected{background:#dceeff;}'); leftcol.addWidget(self.nav)
        self.stack = QStackedWidget(); layout.addWidget(self.stack)

        self.home = HomeView(analytics_service); self.home.navigate_requested.connect(self.navigate_to)
        self.search = GlobalSearchView(analytics_service)
        self.dashboard = DashboardView(analytics_service)
        self.usuarios = UsuariosView(usuario_service)
        self.contratos = ContratosView(contrato_service)
        self.medicoes = MedicoesView(medicao_service)
        self.etapas = EtapasView(etapa_service)
        self.grupos = GruposView(grupo_service)
        self.entregaveis = EntregaveisView(entregavel_service)
        self.estrutura_arvore = EstruturaArvoreView()
        self.plan = PlanejamentoCabecalhoView(plan_service)
        self.plan_itens = PlanejamentoItensView(plan_item_service)
        self.plan_m = PlanejamentoMensalView(plan_m_service)
        self.realizado = RealizadoView(realizado_service)
        self.prod_param = ProdutividadeParametrosView(prod_param_service)
        self.prod_meta = ProdutividadeMetasView(prod_meta_service)
        self.prod_real = ProdutividadeRealizadoView(prod_real_service)
        self.prod_cost = ProdutividadeCustosView(prod_cost_service)
        self.prod_dash = ProdutividadeDashboardView(prod_dash_service)
        self.prod_dre = ProdutividadeDREView(prod_dash_service, dre_param_service)
        self.comp_m = ComparativoMensalView(analytics_service, contrato_service)
        self.comp_a = ComparativoAcumuladoView(analytics_service, contrato_service)
        self.workflow = WorkflowView(workflow_service)
        self.historico = HistoricoView(historico_service)
        self.despesas_plan = DespesasPlanejamentoView(despesas_plan_service)
        self.despesas_real = DespesasRealizadoView(despesas_real_service)
        self.lanc_grade = LancamentosGradeView(despesas_real_service)
        self.grade_desp_plan = GradeDespesasPlanejamentoView(despesas_plan_service)
        self.grade_prod_real = GradeProdutividadeRealizadoView(prod_real_service)
        self.grade_realizado = GradeRealizadoFinanceiroView(realizado_service)
        self.exportacao = ExportacaoView(exportacao_service)
        self.exportacao_anual = ExportacaoAnualView(exportacao_service)
        self.exportacao_excel = ExportacaoExcelView(exportacao_service)
        self.exportacao_oficial = ExportacaoOficialView(exportacao_service)
        self.exportacao_excel_oficial = ExportacaoExcelOficialView(exportacao_service)
        template_path = Path(__file__).resolve().parents[1] / 'templates' / 'planilha_importacao_financeira_padrao.xlsx'
        self.importacao_fin = ImportacaoFinanceiraView(finance_import_service, template_path)
        self.painel_ano = PainelAnoVigenteView(analytics_service)
        self.painel_12 = Painel12MesesView(analytics_service)
        self.forecast_anual = ForecastAnualView(analytics_service)
        self.cockpit_mensal = CockpitMensalOficialView(analytics_service)

        self.page_map = {}
        grouped = {
            'Início': [('Home', self.home), ('Busca Global', self.search), ('Dashboard', self.dashboard)],
            'Operação': [('Contratos', self.contratos), ('Medições', self.medicoes), ('Realizado', self.realizado), ('Realizado em Grade', self.grade_realizado), ('Desp. Realizado', self.despesas_real), ('Lançamentos em Grade', self.lanc_grade)],
            'Planejamento': [('Etapas', self.etapas), ('Grupos', self.grupos), ('Entregáveis', self.entregaveis), ('Estrutura Árvore', self.estrutura_arvore), ('Planejamento', self.plan), ('Planej. Itens', self.plan_itens), ('Planej. Mensal', self.plan_m), ('Comparativo Mês', self.comp_m), ('Comparativo Acum.', self.comp_a), ('Desp. Planejamento', self.despesas_plan), ('Desp. Planejamento em Grade', self.grade_desp_plan)],
            'Produtividade': [('Prod. Parâmetros', self.prod_param), ('Prod. Metas', self.prod_meta), ('Prod. Receita', self.prod_real), ('Prod. Receita em Grade', self.grade_prod_real), ('Prod. Custos', self.prod_cost), ('Prod. Dashboard', self.prod_dash)],
            'Financeiro / DRE': [('DRE Gerencial', self.prod_dre), ('Importação Financeira', self.importacao_fin), ('Painel Ano Vigente', self.painel_ano), ('Próximos 12 Meses', self.painel_12), ('Forecast Anual', self.forecast_anual), ('Cockpit Mensal', self.cockpit_mensal)],
            'Governança': [('Workflow', self.workflow), ('Histórico', self.historico), ('Usuários', self.usuarios)],
            'Exportação': [('Exportação', self.exportacao), ('Exportação Anual', self.exportacao_anual), ('Exportação Excel', self.exportacao_excel), ('Exportação Oficial', self.exportacao_oficial), ('Excel Oficial', self.exportacao_excel_oficial)],
        }
        for group, pages in grouped.items():
            header = QListWidgetItem(group); header.setFlags(Qt.NoItemFlags); header.setBackground(Qt.lightGray); self.nav.addItem(header)
            for name, view in pages:
                item = QListWidgetItem('  ' + name); item.setData(Qt.UserRole, name); self.nav.addItem(item)
                self.stack.addWidget(view); self.page_map[name] = view
        self.nav.currentItemChanged.connect(self.on_nav_changed)
        self.navigate_to('Home')

        for view in [self.usuarios, self.contratos, self.medicoes, self.etapas, self.grupos, self.entregaveis, self.plan, self.plan_itens, self.plan_m, self.realizado, self.prod_param, self.prod_meta, self.prod_real, self.prod_cost, self.despesas_plan, self.despesas_real, self.lanc_grade, self.grade_desp_plan, self.grade_prod_real, self.grade_realizado]:
            if hasattr(view, 'data_changed'): view.data_changed.connect(self.refresh_all)
        self.refresh_user_combo(initial=True)

    def on_nav_changed(self, current, previous):
        if not current: return
        name = current.data(Qt.UserRole)
        if not name: return
        self.navigate_to(name)

    def navigate_to(self, name):
        view = self.page_map.get(name)
        if view is None: return
        self.stack.setCurrentWidget(view)
        for i in range(self.nav.count()):
            item = self.nav.item(i)
            if item.data(Qt.UserRole) == name:
                self.nav.setCurrentRow(i); break

    def do_global_search(self):
        q = self.ed_global.text().strip()
        self.search.perform_search(q)
        self.navigate_to('Busca Global')

    def refresh_user_combo(self, initial=False):
        cur = self.cb_usuario.currentData(); self.cb_usuario.blockSignals(True); self.cb_usuario.clear()
        for u in self.usuario_repo.list_all():
            if int(u['ativo'] or 0) == 1: self.cb_usuario.addItem(f"{u['nome']} - {u['perfil']}", u['id'])
        idx = self.cb_usuario.findData(cur); self.cb_usuario.setCurrentIndex(idx if idx >= 0 and self.cb_usuario.count() > 0 else 0); self.cb_usuario.blockSignals(False)
        if initial: self.show_login()
        else: self.on_user_change()

    def show_login(self):
        dlg = QDialog(self); dlg.setWindowTitle('Acesso ao sistema'); dlg.setModal(True); dlg.resize(760, 520)
        lay = QVBoxLayout(dlg); login = LoginView(self.usuario_repo); lay.addWidget(login)
        def handle(uid):
            idx = self.cb_usuario.findData(uid)
            if idx >= 0: self.cb_usuario.setCurrentIndex(idx)
            dlg.accept()
        login.login_success.connect(handle); dlg.exec(); self.on_user_change()

    def on_user_change(self):
        uid = self.cb_usuario.currentData(); user = self.usuario_repo.get_by_id(uid) if uid else None; self.app_context.set_current_user(user); self.security.set_current_user(user)
        nome = user['nome'] if user else ''; perfil = user['perfil'] if user else ''
        self.lbl_welcome.setText(f"Bem-vindo, {nome}\nPerfil: {perfil}" if user else '')
        self.apply_permissions()

    def apply_permissions(self):
        perms = self.security.permissions()
        default_views = [self.contratos, self.medicoes, self.etapas, self.grupos, self.entregaveis, self.plan, self.plan_itens, self.plan_m, self.realizado, self.prod_param, self.prod_meta, self.prod_real, self.prod_cost, self.despesas_plan, self.despesas_real, self.lanc_grade, self.grade_desp_plan, self.grade_prod_real, self.grade_realizado]
        for view in default_views:
            if hasattr(view, 'btn_salvar'): view.btn_salvar.setEnabled(perms['edit_all'])
            if hasattr(view, 'btn_novo'): view.btn_novo.setEnabled(perms['edit_all'])
            if hasattr(view, 'btn_excluir'): view.btn_excluir.setEnabled(perms['delete_all'])
            if hasattr(view, 'btn_save'): view.btn_save.setEnabled(perms['edit_all'])
        if hasattr(self.usuarios, 'btn_salvar'): self.usuarios.btn_salvar.setEnabled(perms['users'])
        if hasattr(self.usuarios, 'btn_novo'): self.usuarios.btn_novo.setEnabled(perms['users'])
        if hasattr(self.usuarios, 'btn_excluir'): self.usuarios.btn_excluir.setEnabled(perms['users'])
        if hasattr(self.workflow, 'btn_salvar'): self.workflow.btn_salvar.setEnabled(perms['workflow'])

    def refresh_all(self):
        for view in self.page_map.values():
            if hasattr(view, 'reload_data'): view.reload_data()
        self.refresh_user_combo(initial=False)


def run_app():
    app = QApplication(sys.argv)
    win = MainWindow(); win.show()
    sys.exit(app.exec())
