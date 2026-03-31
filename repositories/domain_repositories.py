from repositories.base import BaseRepository

class ContratoRepository(BaseRepository):
    def list_all(self):
        return self.fetchall("SELECT * FROM contratos ORDER BY codigo")
    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM contratos WHERE id = ?", (obj_id,))
    def create(self, d):
        return self.execute(
            '''INSERT INTO contratos
               (codigo,nome,cliente,data_inicio,data_fim,valor_total_contrato,percentual_sinal,status,observacoes)
               VALUES (?,?,?,?,?,?,?,?,?)''',
            (d["codigo"], d["nome"], d.get("cliente",""), d.get("data_inicio",""), d.get("data_fim",""),
             d.get("valor_total_contrato",0), d.get("percentual_sinal",0), d.get("status","planejamento"), d.get("observacoes",""))
        )
    def update(self, obj_id, d):
        self.execute(
            '''UPDATE contratos SET codigo=?,nome=?,cliente=?,data_inicio=?,data_fim=?,valor_total_contrato=?,
               percentual_sinal=?,status=?,observacoes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?''',
            (d["codigo"], d["nome"], d.get("cliente",""), d.get("data_inicio",""), d.get("data_fim",""),
             d.get("valor_total_contrato",0), d.get("percentual_sinal",0), d.get("status","planejamento"),
             d.get("observacoes",""), obj_id)
        )
    def delete(self, obj_id):
        self.execute("DELETE FROM contratos WHERE id = ?", (obj_id,))

class MedicaoRepository(BaseRepository):
    def list_all(self):
        return self.fetchall(
            '''
            SELECT m.*, c.codigo AS contrato_codigo, c.nome AS contrato_nome,
                   COALESCE(SUM(r.valor_realizado_mes),0) AS valor_lancado
            FROM medicoes m
            INNER JOIN contratos c ON c.id = m.contrato_id
            LEFT JOIN realizado_mensal r ON r.medicao_id = m.id
            GROUP BY m.id, c.codigo, c.nome
            ORDER BY c.codigo, m.numero_medicao
            '''
        )
    def list_by_contrato(self, contrato_id):
        return self.fetchall("SELECT * FROM medicoes WHERE contrato_id = ? ORDER BY numero_medicao", (contrato_id,))
    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM medicoes WHERE id = ?", (obj_id,))
    def create(self, d):
        return self.execute(
            '''INSERT INTO medicoes
               (contrato_id,numero_medicao,competencia,data_inicio_periodo,data_fim_periodo,status,observacoes)
               VALUES (?,?,?,?,?,?,?)''',
            (d["contrato_id"], d["numero_medicao"], d["competencia"], d.get("data_inicio_periodo",""),
             d.get("data_fim_periodo",""), d.get("status","aberta"), d.get("observacoes",""))
        )
    def update(self, obj_id, d):
        self.execute(
            '''UPDATE medicoes SET contrato_id=?,numero_medicao=?,competencia=?,data_inicio_periodo=?,data_fim_periodo=?,
               status=?,observacoes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?''',
            (d["contrato_id"], d["numero_medicao"], d["competencia"], d.get("data_inicio_periodo",""),
             d.get("data_fim_periodo",""), d.get("status","aberta"), d.get("observacoes",""), obj_id)
        )
    def delete(self, obj_id):
        self.execute("DELETE FROM medicoes WHERE id = ?", (obj_id,))

class EtapaRepository(BaseRepository):
    def list_all(self):
        return self.fetchall(
            '''SELECT e.*, c.codigo AS contrato_codigo, c.nome AS contrato_nome
               FROM etapas e INNER JOIN contratos c ON c.id=e.contrato_id
               ORDER BY c.codigo,e.ordem,e.codigo'''
        )
    def list_by_contrato(self, contrato_id):
        return self.fetchall("SELECT * FROM etapas WHERE contrato_id=? ORDER BY ordem,codigo", (contrato_id,))
    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM etapas WHERE id=?", (obj_id,))
    def create(self, d):
        return self.execute(
            "INSERT INTO etapas (contrato_id,codigo,descricao,ordem,ativo,observacoes) VALUES (?,?,?,?,?,?)",
            (d["contrato_id"], d["codigo"], d["descricao"], d.get("ordem",0), d.get("ativo",1), d.get("observacoes",""))
        )
    def update(self, obj_id, d):
        self.execute(
            "UPDATE etapas SET contrato_id=?,codigo=?,descricao=?,ordem=?,ativo=?,observacoes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (d["contrato_id"], d["codigo"], d["descricao"], d.get("ordem",0), d.get("ativo",1), d.get("observacoes",""), obj_id)
        )
    def delete(self, obj_id):
        self.execute("DELETE FROM etapas WHERE id=?", (obj_id,))

class GrupoRepository(BaseRepository):
    def list_all(self):
        return self.fetchall(
            '''SELECT g.*, c.codigo AS contrato_codigo, e.codigo AS etapa_codigo, e.descricao AS etapa_descricao
               FROM grupos g
               INNER JOIN contratos c ON c.id=g.contrato_id
               INNER JOIN etapas e ON e.id=g.etapa_id
               ORDER BY c.codigo,e.ordem,g.ordem,g.codigo'''
        )
    def list_by_etapa(self, etapa_id):
        return self.fetchall("SELECT * FROM grupos WHERE etapa_id=? ORDER BY ordem,codigo", (etapa_id,))
    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM grupos WHERE id=?", (obj_id,))
    def create(self, d):
        return self.execute(
            "INSERT INTO grupos (contrato_id,etapa_id,codigo,descricao,ordem,ativo,observacoes) VALUES (?,?,?,?,?,?,?)",
            (d["contrato_id"], d["etapa_id"], d["codigo"], d["descricao"], d.get("ordem",0), d.get("ativo",1), d.get("observacoes",""))
        )
    def update(self, obj_id, d):
        self.execute(
            "UPDATE grupos SET contrato_id=?,etapa_id=?,codigo=?,descricao=?,ordem=?,ativo=?,observacoes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (d["contrato_id"], d["etapa_id"], d["codigo"], d["descricao"], d.get("ordem",0), d.get("ativo",1), d.get("observacoes",""), obj_id)
        )
    def delete(self, obj_id):
        self.execute("DELETE FROM grupos WHERE id=?", (obj_id,))

class EntregavelRepository(BaseRepository):
    def list_all(self):
        return self.fetchall(
            '''SELECT ent.*, c.codigo AS contrato_codigo, e.codigo AS etapa_codigo, g.codigo AS grupo_codigo
               FROM entregaveis ent
               INNER JOIN contratos c ON c.id=ent.contrato_id
               INNER JOIN etapas e ON e.id=ent.etapa_id
               INNER JOIN grupos g ON g.id=ent.grupo_id
               ORDER BY c.codigo,e.ordem,g.ordem,ent.ordem,ent.codigo'''
        )
    def list_by_grupo(self, grupo_id):
        return self.fetchall("SELECT * FROM entregaveis WHERE grupo_id=? ORDER BY ordem,codigo", (grupo_id,))
    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM entregaveis WHERE id=?", (obj_id,))
    def create(self, d):
        return self.execute(
            "INSERT INTO entregaveis (contrato_id,etapa_id,grupo_id,codigo,descricao,unidade,ordem,ativo,observacoes) VALUES (?,?,?,?,?,?,?,?,?)",
            (d["contrato_id"], d["etapa_id"], d["grupo_id"], d["codigo"], d["descricao"], d.get("unidade",""),
             d.get("ordem",0), d.get("ativo",1), d.get("observacoes",""))
        )
    def update(self, obj_id, d):
        self.execute(
            "UPDATE entregaveis SET contrato_id=?,etapa_id=?,grupo_id=?,codigo=?,descricao=?,unidade=?,ordem=?,ativo=?,observacoes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (d["contrato_id"], d["etapa_id"], d["grupo_id"], d["codigo"], d["descricao"], d.get("unidade",""),
             d.get("ordem",0), d.get("ativo",1), d.get("observacoes",""), obj_id)
        )
    def delete(self, obj_id):
        self.execute("DELETE FROM entregaveis WHERE id=?", (obj_id,))

class PlanejamentoCabecalhoRepository(BaseRepository):
    def list_all(self):
        return self.fetchall(
            '''SELECT p.*, c.codigo AS contrato_codigo, c.nome AS contrato_nome
               FROM planejamento_cabecalho p
               INNER JOIN contratos c ON c.id=p.contrato_id
               ORDER BY c.codigo,p.versao DESC'''
        )
    def list_by_contrato(self, contrato_id):
        return self.fetchall("SELECT * FROM planejamento_cabecalho WHERE contrato_id=? ORDER BY versao DESC", (contrato_id,))
    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM planejamento_cabecalho WHERE id=?", (obj_id,))
    def create(self, d):
        return self.execute(
            "INSERT INTO planejamento_cabecalho (contrato_id,versao,descricao_versao,data_base,status,motivo_revisao,observacoes) VALUES (?,?,?,?,?,?,?)",
            (d["contrato_id"], d["versao"], d.get("descricao_versao",""), d.get("data_base",""), d.get("status","rascunho"),
             d.get("motivo_revisao",""), d.get("observacoes",""))
        )
    def update(self, obj_id, d):
        self.execute(
            "UPDATE planejamento_cabecalho SET contrato_id=?,versao=?,descricao_versao=?,data_base=?,status=?,motivo_revisao=?,observacoes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (d["contrato_id"], d["versao"], d.get("descricao_versao",""), d.get("data_base",""), d.get("status","rascunho"),
             d.get("motivo_revisao",""), d.get("observacoes",""), obj_id)
        )
    def delete(self, obj_id):
        self.execute("DELETE FROM planejamento_cabecalho WHERE id=?", (obj_id,))

class PlanejamentoItemRepository(BaseRepository):
    def list_all(self):
        return self.fetchall(
            '''SELECT pi.*, p.versao, c.codigo AS contrato_codigo,
                      ent.codigo AS entregavel_codigo, ent.descricao AS entregavel_descricao
               FROM planejamento_itens pi
               INNER JOIN planejamento_cabecalho p ON p.id=pi.planejamento_id
               INNER JOIN contratos c ON c.id=pi.contrato_id
               INNER JOIN entregaveis ent ON ent.id=pi.entregavel_id
               ORDER BY c.codigo,p.versao DESC,ent.codigo'''
        )
    def list_by_planejamento(self, planejamento_id):
        return self.fetchall("SELECT * FROM planejamento_itens WHERE planejamento_id=? ORDER BY entregavel_id", (planejamento_id,))
    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM planejamento_itens WHERE id=?", (obj_id,))
    def create(self, d):
        return self.execute(
            "INSERT INTO planejamento_itens (planejamento_id,contrato_id,etapa_id,grupo_id,entregavel_id,valor_previsto_total,percentual_previsto_total,observacoes) VALUES (?,?,?,?,?,?,?,?)",
            (d["planejamento_id"], d["contrato_id"], d["etapa_id"], d["grupo_id"], d["entregavel_id"],
             d.get("valor_previsto_total",0), d.get("percentual_previsto_total",0), d.get("observacoes",""))
        )
    def update(self, obj_id, d):
        self.execute(
            "UPDATE planejamento_itens SET planejamento_id=?,contrato_id=?,etapa_id=?,grupo_id=?,entregavel_id=?,valor_previsto_total=?,percentual_previsto_total=?,observacoes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (d["planejamento_id"], d["contrato_id"], d["etapa_id"], d["grupo_id"], d["entregavel_id"],
             d.get("valor_previsto_total",0), d.get("percentual_previsto_total",0), d.get("observacoes",""), obj_id)
        )
    def delete(self, obj_id):
        self.execute("DELETE FROM planejamento_itens WHERE id=?", (obj_id,))

class PlanejamentoMensalRepository(BaseRepository):
    def list_all(self):
        return self.fetchall(
            '''SELECT pm.*, p.versao, c.codigo AS contrato_codigo, ent.codigo AS entregavel_codigo
               FROM planejamento_mensal pm
               INNER JOIN planejamento_itens pi ON pi.id=pm.planejamento_item_id
               INNER JOIN planejamento_cabecalho p ON p.id=pi.planejamento_id
               INNER JOIN contratos c ON c.id=pm.contrato_id
               INNER JOIN entregaveis ent ON ent.id=pm.entregavel_id
               ORDER BY c.codigo,p.versao DESC,pm.competencia,ent.codigo'''
        )
    def list_by_planejamento(self, planejamento_id):
        return self.fetchall(
            '''SELECT pm.* FROM planejamento_mensal pm
               INNER JOIN planejamento_itens pi ON pi.id=pm.planejamento_item_id
               WHERE pi.planejamento_id=? ORDER BY pm.competencia,pm.entregavel_id''',
            (planejamento_id,)
        )
    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM planejamento_mensal WHERE id=?", (obj_id,))
    def create(self, d):
        return self.execute(
            "INSERT INTO planejamento_mensal (planejamento_item_id,contrato_id,etapa_id,grupo_id,entregavel_id,competencia,valor_previsto_mes,percentual_previsto_mes,observacoes) VALUES (?,?,?,?,?,?,?,?,?)",
            (d["planejamento_item_id"], d["contrato_id"], d["etapa_id"], d["grupo_id"], d["entregavel_id"],
             d["competencia"], d.get("valor_previsto_mes",0), d.get("percentual_previsto_mes",0), d.get("observacoes",""))
        )
    def update(self, obj_id, d):
        self.execute(
            "UPDATE planejamento_mensal SET planejamento_item_id=?,contrato_id=?,etapa_id=?,grupo_id=?,entregavel_id=?,competencia=?,valor_previsto_mes=?,percentual_previsto_mes=?,observacoes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (d["planejamento_item_id"], d["contrato_id"], d["etapa_id"], d["grupo_id"], d["entregavel_id"],
             d["competencia"], d.get("valor_previsto_mes",0), d.get("percentual_previsto_mes",0), d.get("observacoes",""), obj_id)
        )
    def delete(self, obj_id):
        self.execute("DELETE FROM planejamento_mensal WHERE id=?", (obj_id,))

class RealizadoRepository(BaseRepository):
    def list_all(self):
        return self.fetchall(
            '''SELECT r.*, c.codigo AS contrato_codigo, m.numero_medicao, e.codigo AS etapa_codigo, g.codigo AS grupo_codigo,
                      ent.codigo AS entregavel_codigo, ent.descricao AS entregavel_descricao
               FROM realizado_mensal r
               INNER JOIN contratos c ON c.id=r.contrato_id
               INNER JOIN medicoes m ON m.id=r.medicao_id
               INNER JOIN etapas e ON e.id=r.etapa_id
               INNER JOIN grupos g ON g.id=r.grupo_id
               INNER JOIN entregaveis ent ON ent.id=r.entregavel_id
               ORDER BY c.codigo,r.competencia,ent.codigo'''
        )
    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM realizado_mensal WHERE id=?", (obj_id,))
    def create(self, d):
        return self.execute(
            "INSERT INTO realizado_mensal (contrato_id,medicao_id,etapa_id,grupo_id,entregavel_id,competencia,valor_realizado_mes,percentual_realizado_mes,data_lancamento,responsavel,fonte,observacoes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (d["contrato_id"], d["medicao_id"], d["etapa_id"], d["grupo_id"], d["entregavel_id"], d["competencia"],
             d.get("valor_realizado_mes",0), d.get("percentual_realizado_mes",0), d.get("data_lancamento",""),
             d.get("responsavel",""), d.get("fonte","manual"), d.get("observacoes",""))
        )
    def update(self, obj_id, d):
        self.execute(
            "UPDATE realizado_mensal SET contrato_id=?,medicao_id=?,etapa_id=?,grupo_id=?,entregavel_id=?,competencia=?,valor_realizado_mes=?,percentual_realizado_mes=?,data_lancamento=?,responsavel=?,fonte=?,observacoes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (d["contrato_id"], d["medicao_id"], d["etapa_id"], d["grupo_id"], d["entregavel_id"], d["competencia"],
             d.get("valor_realizado_mes",0), d.get("percentual_realizado_mes",0), d.get("data_lancamento",""),
             d.get("responsavel",""), d.get("fonte","manual"), d.get("observacoes",""), obj_id)
        )
    def delete(self, obj_id):
        self.execute("DELETE FROM realizado_mensal WHERE id=?", (obj_id,))

class AnalyticsRepository(BaseRepository):
    def dashboard_totais_contrato(self):
        return self.fetchall(
            '''SELECT c.codigo AS contrato_codigo, c.nome AS contrato_nome,
                      COALESCE(SUM(pm.valor_previsto_mes),0) AS valor_previsto,
                      COALESCE(SUM(rm.valor_realizado_mes),0) AS valor_realizado,
                      COALESCE(SUM(pm.percentual_previsto_mes),0) AS percentual_previsto,
                      COALESCE(SUM(rm.percentual_realizado_mes),0) AS percentual_realizado,
                      COUNT(DISTINCT ent.id) AS qtde_entregaveis
               FROM contratos c
               LEFT JOIN entregaveis ent ON ent.contrato_id=c.id
               LEFT JOIN planejamento_mensal pm ON pm.contrato_id=c.id
               LEFT JOIN realizado_mensal rm ON rm.contrato_id=c.id
               GROUP BY c.codigo,c.nome
               ORDER BY c.codigo'''
        )
    def dashboard_etapas(self):
        return self.fetchall(
            '''SELECT c.codigo AS contrato_codigo, e.codigo AS etapa_codigo, e.descricao AS etapa_descricao,
                      COALESCE(SUM(pm.valor_previsto_mes),0) AS valor_previsto,
                      COALESCE(SUM(rm.valor_realizado_mes),0) AS valor_realizado,
                      COALESCE(SUM(rm.percentual_realizado_mes),0) AS percentual_realizado
               FROM etapas e
               INNER JOIN contratos c ON c.id=e.contrato_id
               LEFT JOIN planejamento_mensal pm ON pm.etapa_id=e.id
               LEFT JOIN realizado_mensal rm ON rm.etapa_id=e.id
               GROUP BY c.codigo,e.codigo,e.descricao
               ORDER BY c.codigo,e.codigo'''
        )
    def comparativo_mensal(self, contrato_id=None):
        where = ""
        params = ()
        if contrato_id:
            where = "WHERE x.contrato_id = ?"
            params = (contrato_id,)
        return self.fetchall(
            f'''SELECT * FROM (
                    SELECT ent.contrato_id, c.codigo AS contrato_codigo,
                           e.codigo AS etapa_codigo, e.descricao AS etapa_descricao,
                           g.codigo AS grupo_codigo, g.descricao AS grupo_descricao,
                           ent.codigo AS entregavel_codigo, ent.descricao AS entregavel_descricao,
                           COALESCE(pm.competencia, rm.competencia) AS competencia,
                           COALESCE(pm.valor_previsto_mes,0) AS valor_previsto_mes,
                           COALESCE(rm.valor_realizado_mes,0) AS valor_realizado_mes,
                           COALESCE(pm.percentual_previsto_mes,0) AS percentual_previsto_mes,
                           COALESCE(rm.percentual_realizado_mes,0) AS percentual_realizado_mes
                    FROM entregaveis ent
                    INNER JOIN contratos c ON c.id=ent.contrato_id
                    INNER JOIN etapas e ON e.id=ent.etapa_id
                    INNER JOIN grupos g ON g.id=ent.grupo_id
                    LEFT JOIN planejamento_mensal pm ON pm.entregavel_id=ent.id
                    LEFT JOIN realizado_mensal rm ON rm.entregavel_id=ent.id AND rm.competencia=pm.competencia
                ) x
                {where}
                ORDER BY x.contrato_codigo,x.competencia,x.etapa_codigo,x.grupo_codigo,x.entregavel_codigo''',
            params
        )
