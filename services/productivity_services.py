from utils.number_utils import to_float

class BaseProdService:
    def __init__(self, repo, historico_repo=None, app_context=None, table_name=""):
        self.repo = repo
        self.historico_repo = historico_repo
        self.app_context = app_context
        self.table_name = table_name
    def log(self, registro_id, acao, resumo=""):
        if self.historico_repo and self.table_name:
            self.historico_repo.create({"tabela":self.table_name,"registro_id":registro_id,"acao":acao,"usuario_id":self.app_context.current_user_id() if self.app_context else None,"resumo":resumo,"workflow_status":""})

class ProdutividadeParametroService(BaseProdService):
    def __init__(self, repo, historico_repo=None, app_context=None):
        super().__init__(repo, historico_repo, app_context, "produtividade_parametros")
    def list_all(self): return self.repo.list_all()
    def get_by_id(self, obj_id): return self.repo.get_by_id(obj_id)
    def get_by_disciplina(self, disciplina): return self.repo.get_by_disciplina(disciplina)
    def create(self, d):
        d["disciplina"]=str(d.get("disciplina","")).strip(); d["horas_por_a1"]=to_float(d.get("horas_por_a1",0)); d["custo_hora_equipe"]=to_float(d.get("custo_hora_equipe",0)); d["ativo"]=1 if str(d.get("ativo","Sim")).lower() in {"1","sim","true","yes"} else 0
        if not d["disciplina"]: raise ValueError("Informe a disciplina.")
        new_id=self.repo.create(d); self.log(new_id,"create",f"Parâmetro criado: {d['disciplina']}")
    def update(self,obj_id,d):
        d["disciplina"]=str(d.get("disciplina","")).strip(); d["horas_por_a1"]=to_float(d.get("horas_por_a1",0)); d["custo_hora_equipe"]=to_float(d.get("custo_hora_equipe",0)); d["ativo"]=1 if str(d.get("ativo","Sim")).lower() in {"1","sim","true","yes"} else 0
        if not d["disciplina"]: raise ValueError("Informe a disciplina.")
        self.repo.update(obj_id,d); self.log(obj_id,"update",f"Parâmetro atualizado: {d['disciplina']}")
    def delete(self,obj_id): self.log(obj_id,"delete","Parâmetro excluído"); self.repo.delete(obj_id)

class ProdutividadeMetaService(BaseProdService):
    def __init__(self, repo, usuario_repo, contrato_repo, etapa_repo, grupo_repo, parametro_repo, historico_repo=None, app_context=None):
        super().__init__(repo, historico_repo, app_context, "produtividade_metas")
        self.usuario_repo=usuario_repo; self.contrato_repo=contrato_repo; self.etapa_repo=etapa_repo; self.grupo_repo=grupo_repo; self.parametro_repo=parametro_repo
    def list_all(self): return self.repo.list_all()
    def get_by_id(self,obj_id): return self.repo.get_by_id(obj_id)
    def usuarios(self): return self.usuario_repo.list_all()
    def contratos(self): return self.contrato_repo.list_all()
    def etapas(self,cid): return self.etapa_repo.list_by_contrato(cid)
    def grupos(self,eid): return self.grupo_repo.list_by_etapa(eid)
    def disciplinas(self): return self.parametro_repo.list_all()
    def _validate(self,d):
        d["usuario_id"]=int(d.get("usuario_id",0)); d["contrato_id"]=int(d.get("contrato_id",0))
        d["etapa_id"]=int(d.get("etapa_id",0)) if d.get("etapa_id") not in (None,"") else None
        d["grupo_id"]=int(d.get("grupo_id",0)) if d.get("grupo_id") not in (None,"") else None
        d["competencia"]=str(d.get("competencia","")).strip(); d["disciplina"]=str(d.get("disciplina","")).strip()
        d["meta_mensal_a1"]=to_float(d.get("meta_mensal_a1",0)); d["horas_por_a1"]=to_float(d.get("horas_por_a1",0)); d["receita_prevista"]=to_float(d.get("receita_prevista",0))
        if d["horas_por_a1"]==0:
            prm=self.parametro_repo.get_by_disciplina(d["disciplina"])
            if prm: d["horas_por_a1"]=float(prm["horas_por_a1"] or 0)
        d["horas_planejadas"]=d["meta_mensal_a1"]*d["horas_por_a1"]
        if d["usuario_id"]<=0 or d["contrato_id"]<=0 or not d["competencia"] or not d["disciplina"]:
            raise ValueError("Preencha usuário, contrato, competência e disciplina.")
        return d
    def create(self,d):
        d=self._validate(d); new_id=self.repo.create(d); self.log(new_id,"create","Meta criada")
    def update(self,obj_id,d):
        d=self._validate(d); self.repo.update(obj_id,d); self.log(obj_id,"update","Meta atualizada")
    def delete(self,obj_id): self.log(obj_id,"delete","Meta excluída"); self.repo.delete(obj_id)

class ProdutividadeRealizadoService(BaseProdService):
    def __init__(self, repo, usuario_repo, contrato_repo, etapa_repo, grupo_repo, entregavel_repo, parametro_repo, historico_repo=None, app_context=None):
        super().__init__(repo, historico_repo, app_context, "produtividade_realizado")
        self.usuario_repo=usuario_repo; self.contrato_repo=contrato_repo; self.etapa_repo=etapa_repo; self.grupo_repo=grupo_repo; self.entregavel_repo=entregavel_repo; self.parametro_repo=parametro_repo
    def list_all(self): return self.repo.list_all()
    def get_by_id(self,obj_id): return self.repo.get_by_id(obj_id)
    def usuarios(self): return self.usuario_repo.list_all()
    def contratos(self): return self.contrato_repo.list_all()
    def etapas(self,cid): return self.etapa_repo.list_by_contrato(cid)
    def grupos(self,eid): return self.grupo_repo.list_by_etapa(eid)
    def entregaveis(self,gid): return self.entregavel_repo.list_by_grupo(gid)
    def disciplinas(self): return self.parametro_repo.list_all()
    def _validate(self,d):
        d["usuario_id"]=int(d.get("usuario_id",0)); d["contrato_id"]=int(d.get("contrato_id",0))
        d["etapa_id"]=int(d.get("etapa_id",0)) if d.get("etapa_id") not in (None,"") else None
        d["grupo_id"]=int(d.get("grupo_id",0)) if d.get("grupo_id") not in (None,"") else None
        d["entregavel_id"]=int(d.get("entregavel_id",0)) if d.get("entregavel_id") not in (None,"") else None
        d["competencia"]=str(d.get("competencia","")).strip(); d["disciplina"]=str(d.get("disciplina","")).strip()
        d["produzido_a1"]=to_float(d.get("produzido_a1",0)); d["horas_por_a1"]=to_float(d.get("horas_por_a1",0)); d["receita_faturada"]=to_float(d.get("receita_faturada",0)); d["status_aprovacao"]=str(d.get("status_aprovacao","rascunho")).strip() or "rascunho"
        if d["horas_por_a1"]==0:
            prm=self.parametro_repo.get_by_disciplina(d["disciplina"])
            if prm: d["horas_por_a1"]=float(prm["horas_por_a1"] or 0)
        d["horas_equipe"]=to_float(d.get("horas_equipe",0)) or (d["produzido_a1"]*d["horas_por_a1"])
        if d["usuario_id"]<=0 or d["contrato_id"]<=0 or not d["competencia"] or not d["disciplina"]:
            raise ValueError("Preencha usuário, contrato, competência e disciplina.")
        return d
    def create(self,d):
        d=self._validate(d); new_id=self.repo.create(d); self.log(new_id,"create","Realizado criado")
    def update(self,obj_id,d):
        d=self._validate(d); self.repo.update(obj_id,d); self.log(obj_id,"update","Realizado atualizado")
    def delete(self,obj_id): self.log(obj_id,"delete","Realizado excluído"); self.repo.delete(obj_id)

class ProdutividadeCustoService(BaseProdService):
    def __init__(self, repo, usuario_repo, contrato_repo, etapa_repo, grupo_repo, parametro_repo, historico_repo=None, app_context=None):
        super().__init__(repo, historico_repo, app_context, "produtividade_custos")
        self.usuario_repo=usuario_repo; self.contrato_repo=contrato_repo; self.etapa_repo=etapa_repo; self.grupo_repo=grupo_repo; self.parametro_repo=parametro_repo
    def list_all(self): return self.repo.list_all()
    def get_by_id(self,obj_id): return self.repo.get_by_id(obj_id)
    def usuarios(self): return self.usuario_repo.list_all()
    def contratos(self): return self.contrato_repo.list_all()
    def etapas(self,cid): return self.etapa_repo.list_by_contrato(cid)
    def grupos(self,eid): return self.grupo_repo.list_by_etapa(eid)
    def disciplinas(self): return self.parametro_repo.list_all()
    def _validate(self,d):
        d["usuario_id"]=int(d.get("usuario_id",0)) if d.get("usuario_id") not in (None,"") else None
        d["contrato_id"]=int(d.get("contrato_id",0))
        d["etapa_id"]=int(d.get("etapa_id",0)) if d.get("etapa_id") not in (None,"") else None
        d["grupo_id"]=int(d.get("grupo_id",0)) if d.get("grupo_id") not in (None,"") else None
        d["competencia"]=str(d.get("competencia","")).strip(); d["disciplina"]=str(d.get("disciplina","")).strip(); d["tipo_recurso"]=str(d.get("tipo_recurso","")).strip(); d["fornecedor_nome"]=str(d.get("fornecedor_nome","")).strip()
        d["horas"]=to_float(d.get("horas",0)); d["custo_hora"]=to_float(d.get("custo_hora",0)); d["custo_total"]=to_float(d.get("custo_total",0)) or (d["horas"]*d["custo_hora"]); d["status_aprovacao"]=str(d.get("status_aprovacao","rascunho")).strip() or "rascunho"
        if d["contrato_id"]<=0 or not d["competencia"] or not d["disciplina"] or not d["tipo_recurso"]:
            raise ValueError("Preencha contrato, competência, disciplina e tipo de recurso.")
        return d
    def create(self,d):
        d=self._validate(d); new_id=self.repo.create(d); self.log(new_id,"create","Custo criado")
    def update(self,obj_id,d):
        d=self._validate(d); self.repo.update(obj_id,d); self.log(obj_id,"update","Custo atualizado")
    def delete(self,obj_id): self.log(obj_id,"delete","Custo excluído"); self.repo.delete(obj_id)

class ProdutividadeAnalyticsService:
    def __init__(self, repo, contrato_repo):
        self.repo=repo; self.contrato_repo=contrato_repo
    def contratos(self): return self.contrato_repo.list_all()
    def resumo(self, contrato_id=None): return self.repo.resumo(contrato_id)
    def ranking_projetistas(self, contrato_id=None): return self.repo.ranking_projetistas(contrato_id)
    def por_disciplina(self, contrato_id=None): return self.repo.por_disciplina(contrato_id)
    def comparativo_competencia(self, contrato_id=None): return self.repo.comparativo_competencia(contrato_id)
    def margem_por_estrutura(self, nivel='contrato', contrato_id=None): return self.repo.margem_por_estrutura(nivel, contrato_id)
    def top_desvios_estrutura(self, contrato_id=None, limite=10): return self.repo.top_desvios_estrutura(contrato_id, limite)
    def dre_gerencial_contratos(self, imposto_percentual=16.8): return self.repo.dre_gerencial_contratos(imposto_percentual)
    def dre_gerencial_por_nivel(self, nivel='contrato', imposto_percentual=16.8, contrato_id=None): return self.repo.dre_gerencial_por_nivel(nivel, imposto_percentual, contrato_id)
    def dre_mensal_competencia(self, imposto_percentual=16.8, contrato_id=None): return self.repo.dre_mensal_competencia(imposto_percentual, contrato_id)
    def dre_mensal_composicao(self, competencia, contrato_id=None): return self.repo.dre_mensal_composicao(competencia, contrato_id)


class DREParametrosService:
    def __init__(self, repo):
        self.repo = repo
    def get_ativo(self):
        return self.repo.get_ativo()
    def set_percentual(self, percentual):
        txt = str(percentual).strip()
        if txt == "":
            raise ValueError("Informe o percentual.")
        p = float(txt.replace(".", "").replace(",", "."))
        if p < 0:
            raise ValueError("Imposto não pode ser negativo.")
        self.repo.set_percentual(p)
