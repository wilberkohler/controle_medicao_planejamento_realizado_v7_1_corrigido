from repositories.base import BaseRepository

class UsuarioRepository(BaseRepository):
    def list_all(self):
        return self.fetchall("SELECT * FROM usuarios ORDER BY nome")
    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM usuarios WHERE id=?", (obj_id,))
    def create(self, d):
        return self.execute(
            "INSERT INTO usuarios (nome,email,perfil,ativo,observacoes) VALUES (?,?,?,?,?)",
            (d["nome"], d["email"], d.get("perfil","consulta"), d.get("ativo",1), d.get("observacoes",""))
        )
    def update(self, obj_id, d):
        self.execute(
            "UPDATE usuarios SET nome=?,email=?,perfil=?,ativo=?,observacoes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (d["nome"], d["email"], d.get("perfil","consulta"), d.get("ativo",1), d.get("observacoes",""), obj_id)
        )
    def delete(self, obj_id):
        self.execute("DELETE FROM usuarios WHERE id=?", (obj_id,))

class HistoricoRepository(BaseRepository):
    def list_all(self):
        return self.fetchall(
            "SELECT h.*, u.nome AS usuario_nome FROM historico_alteracoes h LEFT JOIN usuarios u ON u.id=h.usuario_id ORDER BY h.created_at DESC, h.id DESC"
        )
    def create(self, d):
        return self.execute(
            "INSERT INTO historico_alteracoes (tabela,registro_id,acao,usuario_id,resumo,workflow_status) VALUES (?,?,?,?,?,?)",
            (d["tabela"], d["registro_id"], d["acao"], d.get("usuario_id"), d.get("resumo",""), d.get("workflow_status",""))
        )

class WorkflowRepository(BaseRepository):
    def list_all(self):
        return self.fetchall(
            "SELECT w.*, us.nome AS solicitante_nome, ua.nome AS aprovador_nome FROM workflow_aprovacoes w LEFT JOIN usuarios us ON us.id=w.usuario_solicitante_id LEFT JOIN usuarios ua ON ua.id=w.usuario_aprovador_id ORDER BY w.updated_at DESC, w.id DESC"
        )
    def create(self, d):
        return self.execute(
            "INSERT INTO workflow_aprovacoes (modulo,registro_id,status,usuario_solicitante_id,usuario_aprovador_id,data_solicitacao,data_aprovacao,comentario) VALUES (?,?,?,?,?,?,?,?)",
            (d["modulo"], d["registro_id"], d.get("status","rascunho"), d.get("usuario_solicitante_id"), d.get("usuario_aprovador_id"), d.get("data_solicitacao",""), d.get("data_aprovacao",""), d.get("comentario",""))
        )
