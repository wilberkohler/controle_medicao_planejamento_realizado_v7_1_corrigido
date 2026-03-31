class UsuarioService:
    def __init__(self, repo, historico_repo=None, app_context=None):
        self.repo = repo
        self.historico_repo = historico_repo
        self.app_context = app_context

    def list_all(self): return self.repo.list_all()
    def get_by_id(self, obj_id): return self.repo.get_by_id(obj_id)

    def _validate(self, d):
        d["nome"] = str(d.get("nome","")).strip()
        d["email"] = str(d.get("email","")).strip()
        d["ativo"] = 1 if str(d.get("ativo","Sim")).lower() in {"1","sim","true","yes"} else 0
        if not d["nome"] or not d["email"]:
            raise ValueError("Informe nome e email.")
        return d

    def _log(self, registro_id, acao, resumo="", workflow_status=""):
        if self.historico_repo:
            self.historico_repo.create({
                "tabela": "usuarios",
                "registro_id": registro_id,
                "acao": acao,
                "usuario_id": self.app_context.current_user_id() if self.app_context else None,
                "resumo": resumo,
                "workflow_status": workflow_status,
            })

    def create(self, d):
        d = self._validate(d)
        new_id = self.repo.create(d)
        self._log(new_id, "create", f"Usuário criado: {d['nome']}")

    def update(self, obj_id, d):
        d = self._validate(d)
        self.repo.update(obj_id, d)
        self._log(obj_id, "update", f"Usuário atualizado: {d['nome']}")

    def delete(self, obj_id):
        self._log(obj_id, "delete", "Usuário excluído")
        self.repo.delete(obj_id)


class HistoricoService:
    def __init__(self, repo, usuario_repo, app_context=None):
        self.repo = repo
        self.usuario_repo = usuario_repo
        self.app_context = app_context

    def list_all(self): return self.repo.list_all()
    def usuarios(self): return self.usuario_repo.list_all()

    def create(self, d):
        d["tabela"] = str(d.get("tabela","")).strip()
        d["acao"] = str(d.get("acao","")).strip()
        d["registro_id"] = int(d.get("registro_id",0))
        if not d["tabela"] or not d["acao"] or d["registro_id"] <= 0:
            raise ValueError("Informe tabela, ação e registro.")
        if not d.get("usuario_id") and self.app_context:
            d["usuario_id"] = self.app_context.current_user_id()
        self.repo.create(d)


class WorkflowService:
    def __init__(self, repo, usuario_repo, historico_repo=None, app_context=None):
        self.repo = repo
        self.usuario_repo = usuario_repo
        self.historico_repo = historico_repo
        self.app_context = app_context

    def list_all(self): return self.repo.list_all()
    def usuarios(self): return self.usuario_repo.list_all()

    def create(self, d):
        d["modulo"] = str(d.get("modulo","")).strip()
        d["registro_id"] = int(d.get("registro_id",0))
        d["status"] = str(d.get("status","rascunho")).strip() or "rascunho"
        if not d["modulo"] or d["registro_id"] <= 0:
            raise ValueError("Informe módulo e registro.")

        if d["status"] in {"em_aprovacao", "aprovado", "rejeitado"} and not d.get("usuario_aprovador_id") and d["status"] != "em_aprovacao":
            raise ValueError("Informe o aprovador para aprovar ou rejeitar.")

        if not d.get("usuario_solicitante_id") and self.app_context:
            d["usuario_solicitante_id"] = self.app_context.current_user_id()

        new_id = self.repo.create(d)
        if self.historico_repo:
            self.historico_repo.create({
                "tabela": "workflow_aprovacoes",
                "registro_id": new_id,
                "acao": "create",
                "usuario_id": self.app_context.current_user_id() if self.app_context else d.get("usuario_solicitante_id"),
                "resumo": f"Workflow criado para {d['modulo']} #{d['registro_id']}",
                "workflow_status": d["status"],
            })
        return new_id


class SecurityService:
    PROFILE_PERMISSIONS = {
        "administrador": {"edit_all": True, "delete_all": True, "workflow": True, "users": True},
        "gestor": {"edit_all": True, "delete_all": True, "workflow": True, "users": False},
        "aprovador": {"edit_all": False, "delete_all": False, "workflow": True, "users": False},
        "lancador": {"edit_all": True, "delete_all": False, "workflow": False, "users": False},
        "consulta": {"edit_all": False, "delete_all": False, "workflow": False, "users": False},
    }

    def __init__(self):
        self.current_user = None

    def set_current_user(self, user_row):
        self.current_user = user_row

    def permissions(self):
        perfil = self.current_user["perfil"] if self.current_user else "consulta"
        return self.PROFILE_PERMISSIONS.get(perfil, self.PROFILE_PERMISSIONS["consulta"])

    def can_edit_status(self, status):
        perms = self.permissions()
        if status == "aprovado":
            return False
        return perms["edit_all"]

    def can_delete_status(self, status):
        perms = self.permissions()
        if status == "aprovado":
            return False
        return perms["delete_all"]
