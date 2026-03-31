from utils.number_utils import to_float, to_int
from utils.date_utils import normalize_date

class BaseService:
    def __init__(self, historico_repo=None, table_name="", app_context=None):
        self.historico_repo = historico_repo
        self.table_name = table_name
        self.app_context = app_context

    def norm_date(self, value):
        return normalize_date(value) if str(value or "").strip() else ""

    def log(self, registro_id, acao, resumo="", workflow_status=""):
        if self.historico_repo and self.table_name:
            self.historico_repo.create({
                "tabela": self.table_name,
                "registro_id": registro_id,
                "acao": acao,
                "usuario_id": self.app_context.current_user_id() if self.app_context else None,
                "resumo": resumo,
                "workflow_status": workflow_status,
            })

class ContratoService(BaseService):
    def __init__(self, repo, historico_repo=None, app_context=None):
        super().__init__(historico_repo, "contratos", app_context)
        self.repo = repo
    def list_all(self): return self.repo.list_all()
    def get_by_id(self, obj_id): return self.repo.get_by_id(obj_id)
    def validate(self, d):
        d["codigo"] = str(d.get("codigo","")).strip()
        d["nome"] = str(d.get("nome","")).strip()
        if not d["codigo"] or not d["nome"]:
            raise ValueError("Informe código e nome.")
        d["data_inicio"] = self.norm_date(d.get("data_inicio",""))
        d["data_fim"] = self.norm_date(d.get("data_fim",""))
        d["valor_total_contrato"] = to_float(d.get("valor_total_contrato",0))
        d["percentual_sinal"] = to_float(d.get("percentual_sinal",0))
        return d
    def create(self, d):
        d = self.validate(d)
        new_id = self.repo.create(d)
        self.log(new_id, "create", f"Contrato criado: {d['codigo']}")
    def update(self, obj_id, d):
        d = self.validate(d)
        self.repo.update(obj_id, d)
        self.log(obj_id, "update", f"Contrato atualizado: {d['codigo']}")
    def delete(self, obj_id):
        self.log(obj_id, "delete", "Contrato excluído")
        self.repo.delete(obj_id)

class MedicaoService(BaseService):
    def __init__(self, repo, contrato_repo, historico_repo=None, app_context=None):
        super().__init__(historico_repo, "medicoes", app_context)
        self.repo, self.contrato_repo = repo, contrato_repo
    def list_all(self): return self.repo.list_all()
    def get_by_id(self, obj_id): return self.repo.get_by_id(obj_id)
    def contratos(self): return self.contrato_repo.list_all()
    def by_contrato(self, cid): return self.repo.list_by_contrato(cid)
    def validate(self, d):
        d["contrato_id"] = int(d.get("contrato_id",0))
        d["numero_medicao"] = to_int(d.get("numero_medicao",0))
        d["competencia"] = str(d.get("competencia","")).strip()
        d["data_inicio_periodo"] = self.norm_date(d.get("data_inicio_periodo",""))
        d["data_fim_periodo"] = self.norm_date(d.get("data_fim_periodo",""))
        if d["contrato_id"] <= 0 or d["numero_medicao"] <= 0 or not d["competencia"]:
            raise ValueError("Informe contrato, número e competência.")
        return d
    def create(self, d):
        d = self.validate(d)
        new_id = self.repo.create(d)
        self.log(new_id, "create", f"Medição criada: {d['numero_medicao']}")
    def update(self, obj_id, d):
        d = self.validate(d)
        self.repo.update(obj_id, d)
        self.log(obj_id, "update", f"Medição atualizada: {d['numero_medicao']}")
    def delete(self, obj_id):
        self.log(obj_id, "delete", "Medição excluída")
        self.repo.delete(obj_id)

class EtapaService(BaseService):
    def __init__(self, repo, contrato_repo, historico_repo=None, app_context=None):
        super().__init__(historico_repo, "etapas", app_context)
        self.repo, self.contrato_repo = repo, contrato_repo
    def list_all(self): return self.repo.list_all()
    def get_by_id(self, obj_id): return self.repo.get_by_id(obj_id)
    def contratos(self): return self.contrato_repo.list_all()
    def by_contrato(self, cid): return self.repo.list_by_contrato(cid)
    def validate(self, d):
        d["contrato_id"] = int(d.get("contrato_id",0))
        d["codigo"] = str(d.get("codigo","")).strip()
        d["descricao"] = str(d.get("descricao","")).strip()
        d["ordem"] = to_int(d.get("ordem",0))
        d["ativo"] = 1 if str(d.get("ativo","Sim")).lower() in {"1","sim","true","yes"} else 0
        if d["contrato_id"] <= 0 or not d["codigo"] or not d["descricao"]:
            raise ValueError("Informe contrato, código e descrição.")
        return d
    def create(self, d):
        d = self.validate(d); new_id = self.repo.create(d); self.log(new_id, "create", f"Etapa criada: {d['codigo']}")
    def update(self, obj_id, d):
        d = self.validate(d); self.repo.update(obj_id, d); self.log(obj_id, "update", f"Etapa atualizada: {d['codigo']}")
    def delete(self, obj_id):
        self.log(obj_id, "delete", "Etapa excluída"); self.repo.delete(obj_id)

class GrupoService(BaseService):
    def __init__(self, repo, contrato_repo, etapa_repo, historico_repo=None, app_context=None):
        super().__init__(historico_repo, "grupos", app_context)
        self.repo, self.contrato_repo, self.etapa_repo = repo, contrato_repo, etapa_repo
    def list_all(self): return self.repo.list_all()
    def get_by_id(self, obj_id): return self.repo.get_by_id(obj_id)
    def contratos(self): return self.contrato_repo.list_all()
    def etapas(self, cid): return self.etapa_repo.list_by_contrato(cid)
    def grupos(self, eid): return self.repo.list_by_etapa(eid)
    def validate(self, d):
        d["contrato_id"] = int(d.get("contrato_id",0))
        d["etapa_id"] = int(d.get("etapa_id",0))
        d["codigo"] = str(d.get("codigo","")).strip()
        d["descricao"] = str(d.get("descricao","")).strip()
        d["ordem"] = to_int(d.get("ordem",0))
        d["ativo"] = 1 if str(d.get("ativo","Sim")).lower() in {"1","sim","true","yes"} else 0
        if d["contrato_id"] <= 0 or d["etapa_id"] <= 0 or not d["codigo"] or not d["descricao"]:
            raise ValueError("Informe contrato, etapa, código e descrição.")
        return d
    def create(self, d):
        d = self.validate(d); new_id = self.repo.create(d); self.log(new_id, "create", f"Grupo criado: {d['codigo']}")
    def update(self, obj_id, d):
        d = self.validate(d); self.repo.update(obj_id, d); self.log(obj_id, "update", f"Grupo atualizado: {d['codigo']}")
    def delete(self, obj_id):
        self.log(obj_id, "delete", "Grupo excluído"); self.repo.delete(obj_id)

class EntregavelService(BaseService):
    def __init__(self, repo, contrato_repo, etapa_repo, grupo_repo, historico_repo=None, app_context=None):
        super().__init__(historico_repo, "entregaveis", app_context)
        self.repo, self.contrato_repo, self.etapa_repo, self.grupo_repo = repo, contrato_repo, etapa_repo, grupo_repo
    def list_all(self): return self.repo.list_all()
    def get_by_id(self, obj_id): return self.repo.get_by_id(obj_id)
    def contratos(self): return self.contrato_repo.list_all()
    def etapas(self, cid): return self.etapa_repo.list_by_contrato(cid)
    def grupos(self, eid): return self.grupo_repo.list_by_etapa(eid)
    def entregaveis(self, gid): return self.repo.list_by_grupo(gid)
    def validate(self, d):
        d["contrato_id"] = int(d.get("contrato_id",0))
        d["etapa_id"] = int(d.get("etapa_id",0))
        d["grupo_id"] = int(d.get("grupo_id",0))
        d["codigo"] = str(d.get("codigo","")).strip()
        d["descricao"] = str(d.get("descricao","")).strip()
        d["unidade"] = str(d.get("unidade","")).strip()
        d["ordem"] = to_int(d.get("ordem",0))
        d["ativo"] = 1 if str(d.get("ativo","Sim")).lower() in {"1","sim","true","yes"} else 0
        if d["contrato_id"] <= 0 or d["etapa_id"] <= 0 or d["grupo_id"] <= 0 or not d["codigo"] or not d["descricao"]:
            raise ValueError("Informe contrato, etapa, grupo, código e descrição.")
        return d
    def create(self, d):
        d = self.validate(d); new_id = self.repo.create(d); self.log(new_id, "create", f"Entregável criado: {d['codigo']}")
    def update(self, obj_id, d):
        d = self.validate(d); self.repo.update(obj_id, d); self.log(obj_id, "update", f"Entregável atualizado: {d['codigo']}")
    def delete(self, obj_id):
        self.log(obj_id, "delete", "Entregável excluído"); self.repo.delete(obj_id)

class PlanejamentoCabecalhoService(BaseService):
    def __init__(self, repo, contrato_repo, historico_repo=None, app_context=None):
        super().__init__(historico_repo, "planejamento_cabecalho", app_context)
        self.repo, self.contrato_repo = repo, contrato_repo
    def list_all(self): return self.repo.list_all()
    def get_by_id(self, obj_id): return self.repo.get_by_id(obj_id)
    def contratos(self): return self.contrato_repo.list_all()
    def by_contrato(self, cid): return self.repo.list_by_contrato(cid)
    def validate(self, d):
        d["contrato_id"] = int(d.get("contrato_id",0))
        d["versao"] = to_int(d.get("versao",0))
        d["data_base"] = self.norm_date(d.get("data_base",""))
        if d["contrato_id"] <= 0 or d["versao"] <= 0:
            raise ValueError("Informe contrato e versão.")
        return d
    def create(self, d):
        d = self.validate(d); new_id = self.repo.create(d); self.log(new_id, "create", f"Planejamento criado: v{d['versao']}")
    def update(self, obj_id, d):
        d = self.validate(d); self.repo.update(obj_id, d); self.log(obj_id, "update", f"Planejamento atualizado: v{d['versao']}")
    def delete(self, obj_id):
        self.log(obj_id, "delete", "Planejamento excluído"); self.repo.delete(obj_id)

class PlanejamentoItemService(BaseService):
    def __init__(self, repo, plan_repo, contrato_repo, etapa_repo, grupo_repo, entregavel_repo, historico_repo=None, app_context=None):
        super().__init__(historico_repo, "planejamento_itens", app_context)
        self.repo, self.plan_repo, self.contrato_repo, self.etapa_repo, self.grupo_repo, self.entregavel_repo = repo, plan_repo, contrato_repo, etapa_repo, grupo_repo, entregavel_repo
    def list_all(self): return self.repo.list_all()
    def get_by_id(self, obj_id): return self.repo.get_by_id(obj_id)
    def contratos(self): return self.contrato_repo.list_all()
    def planejamentos(self, cid): return self.plan_repo.list_by_contrato(cid)
    def etapas(self, cid): return self.etapa_repo.list_by_contrato(cid)
    def grupos(self, eid): return self.grupo_repo.list_by_etapa(eid)
    def entregaveis(self, gid): return self.entregavel_repo.list_by_grupo(gid)
    def validate(self, d):
        for key in ["planejamento_id","contrato_id","etapa_id","grupo_id","entregavel_id"]:
            d[key] = int(d.get(key,0))
        d["valor_previsto_total"] = to_float(d.get("valor_previsto_total",0))
        d["percentual_previsto_total"] = to_float(d.get("percentual_previsto_total",0))
        if min(d["planejamento_id"], d["contrato_id"], d["etapa_id"], d["grupo_id"], d["entregavel_id"]) <= 0:
            raise ValueError("Preencha planejamento e estrutura.")
        return d
    def create(self, d):
        d = self.validate(d); new_id = self.repo.create(d); self.log(new_id, "create", "Item de planejamento criado")
    def update(self, obj_id, d):
        d = self.validate(d); self.repo.update(obj_id, d); self.log(obj_id, "update", "Item de planejamento atualizado")
    def delete(self, obj_id):
        self.log(obj_id, "delete", "Item de planejamento excluído"); self.repo.delete(obj_id)

class PlanejamentoMensalService(BaseService):
    def __init__(self, repo, plan_repo, item_repo, contrato_repo, historico_repo=None, app_context=None):
        super().__init__(historico_repo, "planejamento_mensal", app_context)
        self.repo, self.plan_repo, self.item_repo, self.contrato_repo = repo, plan_repo, item_repo, contrato_repo
    def list_all(self): return self.repo.list_all()
    def get_by_id(self, obj_id): return self.repo.get_by_id(obj_id)
    def contratos(self): return self.contrato_repo.list_all()
    def planejamentos(self, cid): return self.plan_repo.list_by_contrato(cid)
    def itens(self, pid): return self.item_repo.list_by_planejamento(pid)
    def validate(self, d):
        for key in ["planejamento_item_id","contrato_id","etapa_id","grupo_id","entregavel_id"]:
            d[key] = int(d.get(key,0))
        d["competencia"] = str(d.get("competencia","")).strip()
        d["valor_previsto_mes"] = to_float(d.get("valor_previsto_mes",0))
        d["percentual_previsto_mes"] = to_float(d.get("percentual_previsto_mes",0))
        if min(d["planejamento_item_id"], d["contrato_id"], d["etapa_id"], d["grupo_id"], d["entregavel_id"]) <= 0 or not d["competencia"]:
            raise ValueError("Preencha item, estrutura e competência.")
        return d
    def create(self, d):
        d = self.validate(d); new_id = self.repo.create(d); self.log(new_id, "create", "Planejamento mensal criado")
    def update(self, obj_id, d):
        d = self.validate(d); self.repo.update(obj_id, d); self.log(obj_id, "update", "Planejamento mensal atualizado")
    def delete(self, obj_id):
        self.log(obj_id, "delete", "Planejamento mensal excluído"); self.repo.delete(obj_id)

class RealizadoService(BaseService):
    def __init__(self, repo, contrato_repo, medicao_repo, etapa_repo, grupo_repo, entregavel_repo, historico_repo=None, app_context=None):
        super().__init__(historico_repo, "realizado_mensal", app_context)
        self.repo, self.contrato_repo, self.medicao_repo, self.etapa_repo, self.grupo_repo, self.entregavel_repo = repo, contrato_repo, medicao_repo, etapa_repo, grupo_repo, entregavel_repo
    def list_all(self): return self.repo.list_all()
    def get_by_id(self, obj_id): return self.repo.get_by_id(obj_id)
    def contratos(self): return self.contrato_repo.list_all()
    def medicoes(self, cid): return self.medicao_repo.list_by_contrato(cid)
    def etapas(self, cid): return self.etapa_repo.list_by_contrato(cid)
    def grupos(self, eid): return self.grupo_repo.list_by_etapa(eid)
    def entregaveis(self, gid): return self.entregavel_repo.list_by_grupo(gid)
    def validate(self, d):
        for key in ["contrato_id","medicao_id","etapa_id","grupo_id","entregavel_id"]:
            d[key] = int(d.get(key,0))
        d["competencia"] = str(d.get("competencia","")).strip()
        d["valor_realizado_mes"] = to_float(d.get("valor_realizado_mes",0))
        d["percentual_realizado_mes"] = to_float(d.get("percentual_realizado_mes",0))
        d["data_lancamento"] = self.norm_date(d.get("data_lancamento",""))
        if min(d["contrato_id"], d["medicao_id"], d["etapa_id"], d["grupo_id"], d["entregavel_id"]) <= 0 or not d["competencia"]:
            raise ValueError("Preencha contrato, medição, estrutura e competência.")
        return d
    def create(self, d):
        d = self.validate(d); new_id = self.repo.create(d); self.log(new_id, "create", "Realizado criado")
    def update(self, obj_id, d):
        d = self.validate(d); self.repo.update(obj_id, d); self.log(obj_id, "update", "Realizado atualizado")
    def delete(self, obj_id):
        self.log(obj_id, "delete", "Realizado excluído"); self.repo.delete(obj_id)

class AnalyticsService:
    def __init__(self, repo): self.repo = repo
    def dashboard_totais_contrato(self): return self.repo.dashboard_totais_contrato()
    def dashboard_etapas(self): return self.repo.dashboard_etapas()
    def comparativo_mensal(self, contrato_id=None): return self.repo.comparativo_mensal(contrato_id)
    def comparativo_acumulado(self, contrato_id=None): return self.repo.comparativo_acumulado(contrato_id)
    def aprovacoes_resumo(self): return self.repo.aprovacoes_resumo()
    def dashboard_heatmap(self, contrato_id=None, level='contrato'): return self.repo.dashboard_heatmap(contrato_id, level)
    def dashboard_contracts_detail(self): return self.repo.dashboard_contracts_detail()
    def dashboard_stage_detail(self, contrato_id=None): return self.repo.dashboard_stage_detail(contrato_id)
    def dashboard_monthly_curve(self, contrato_id=None): return self.repo.dashboard_monthly_curve(contrato_id)
    def dashboard_top_deviations(self, contrato_id=None, limite=15, competencia=None, etapa_codigo=None, grupo_codigo=None): return self.repo.dashboard_top_deviations(contrato_id, limite, competencia, etapa_codigo, grupo_codigo)
    def dashboard_detail_rows(self, contrato_id=None, etapa_codigo=None, grupo_codigo=None, competencia=None): return self.repo.dashboard_detail_rows(contrato_id, etapa_codigo, grupo_codigo, competencia)

    def home_summary(self): return self.repo.home_summary()
    def open_competencias(self): return self.repo.open_competencias()
    def pending_items(self): return self.repo.pending_items()
    def critical_deviations(self): return self.repo.critical_deviations()
    def latest_launches(self): return self.repo.latest_launches()
    def global_search(self, q): return self.repo.global_search(q)
