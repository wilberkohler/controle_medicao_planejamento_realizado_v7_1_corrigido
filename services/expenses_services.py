from utils.number_utils import to_float

class _BaseDespesasService:
    def __init__(self, repo, contrato_repo, historico_repo=None, app_context=None, table_name=""):
        self.repo = repo
        self.contrato_repo = contrato_repo
        self.historico_repo = historico_repo
        self.app_context = app_context
        self.table_name = table_name

    def contratos(self):
        return self.contrato_repo.list_all()

    def _log(self, registro_id, acao, resumo=""):
        if self.historico_repo and self.table_name:
            self.historico_repo.create({
                "tabela": self.table_name,
                "registro_id": registro_id,
                "acao": acao,
                "usuario_id": self.app_context.current_user_id() if self.app_context else None,
                "resumo": resumo,
                "workflow_status": "",
            })

class DespesasPlanejamentoService(_BaseDespesasService):
    def list_all(self): return self.repo.list_all()
    def get_by_id(self, obj_id): return self.repo.get_by_id(obj_id)
    def validate(self, d):
        d["competencia"] = str(d.get("competencia","")).strip()
        d["categoria"] = str(d.get("categoria","")).strip()
        d["valor_previsto"] = to_float(d.get("valor_previsto",0))
        if not d["competencia"] or not d["categoria"]:
            raise ValueError("Informe competência e categoria.")
        return d
    def create(self, d):
        d = self.validate(d); new_id = self.repo.create(d); self._log(new_id, "create", "Despesa prevista criada")
    def update(self, obj_id, d):
        d = self.validate(d); self.repo.update(obj_id, d); self._log(obj_id, "update", "Despesa prevista atualizada")
    def delete(self, obj_id):
        self._log(obj_id, "delete", "Despesa prevista excluída"); self.repo.delete(obj_id)

class DespesasRealizadoService(_BaseDespesasService):
    def list_all(self): return self.repo.list_all()
    def get_by_id(self, obj_id): return self.repo.get_by_id(obj_id)
    def validate(self, d):
        d["competencia"] = str(d.get("competencia","")).strip()
        d["categoria"] = str(d.get("categoria","")).strip()
        d["valor_realizado"] = to_float(d.get("valor_realizado",0))
        if not d["competencia"] or not d["categoria"]:
            raise ValueError("Informe competência e categoria.")
        return d
    def create(self, d):
        d = self.validate(d); new_id = self.repo.create(d); self._log(new_id, "create", "Despesa realizada criada")
    def update(self, obj_id, d):
        d = self.validate(d); self.repo.update(obj_id, d); self._log(obj_id, "update", "Despesa realizada atualizada")
    def delete(self, obj_id):
        self._log(obj_id, "delete", "Despesa realizada excluída"); self.repo.delete(obj_id)

class ExportacaoService:
    def __init__(self, repo, analytics_service=None):
        self.repo = repo
        self.analytics_service = analytics_service

    def resumo_contabil(self):
        return self.repo.resumo_contabil()

    def resumo_anual_mensal(self):
        return self.repo.resumo_anual_mensal()

    def resumo_anual_categorias(self):
        rows = self.repo.resumo_anual_categorias()
        agg = {}
        for r in rows:
            cat = r['categoria']
            if cat not in agg:
                agg[cat] = {'categoria': cat, 'despesas_previstas': 0.0, 'despesas_realizadas': 0.0}
            agg[cat]['despesas_previstas'] += float(r['despesas_previstas'] or 0)
            agg[cat]['despesas_realizadas'] += float(r['despesas_realizadas'] or 0)
        return list(agg.values())

    def pacote_anual_dict(self):
        return {
            'Resumo_Contratos': self.resumo_contabil(),
            'Resumo_Mensal': self.resumo_anual_mensal(),
            'Despesas_Categorias': self.resumo_anual_categorias(),
        }

    def pacote_oficial_dict(self):
        if not self.analytics_service:
            return {}
        return {
            'Ano_Vigente_Oficial': self.analytics_service.painel_ano_vigente(None, 2026),
            'Proximos_12_Meses_Oficial': self.analytics_service.painel_proximos_12_meses(None, 2026, 3),
            'Forecast_Anual_Oficial': self.analytics_service.forecast_anual(None, 2026, 3),
        }
