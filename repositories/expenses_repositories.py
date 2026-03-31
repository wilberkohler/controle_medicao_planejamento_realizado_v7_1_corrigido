from repositories.base import BaseRepository

class DespesasPlanejamentoRepository(BaseRepository):
    def upsert_prevista_import(self, d):
        row = self.fetchone(
            "SELECT id FROM despesas_planejamento WHERE COALESCE(contrato_id,0)=COALESCE(?,0) AND competencia=? AND categoria=? AND COALESCE(descricao,'')=COALESCE(?, '') AND COALESCE(fornecedor,'')=COALESCE(?, '')",
            (d.get("contrato_id"), d["competencia"], d["categoria"], d.get("descricao",""), d.get("fornecedor",""))
        )
        if row:
            self.execute(
                "UPDATE despesas_planejamento SET valor_previsto=?, centro_custo=?, observacoes=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (d.get("valor_previsto",0), d.get("centro_custo",""), d.get("observacoes",""), row["id"])
            )
            return row["id"]
        return self.execute(
            "INSERT INTO despesas_planejamento (contrato_id,competencia,categoria,descricao,fornecedor,valor_previsto,centro_custo,observacoes) VALUES (?,?,?,?,?,?,?,?)",
            (d.get("contrato_id"), d["competencia"], d["categoria"], d.get("descricao",""), d.get("fornecedor",""), d.get("valor_previsto",0), d.get("centro_custo",""), d.get("observacoes",""))
        )


    def list_all(self):
        return self.fetchall(
            "SELECT d.*, c.codigo AS contrato_codigo, c.nome AS contrato_nome FROM despesas_planejamento d LEFT JOIN contratos c ON c.id=d.contrato_id ORDER BY d.competencia, c.codigo, d.categoria, d.id"
        )
    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM despesas_planejamento WHERE id=?", (obj_id,))
    def create(self, d):
        return self.execute(
            "INSERT INTO despesas_planejamento (contrato_id,competencia,categoria,descricao,fornecedor,valor_previsto,centro_custo,observacoes) VALUES (?,?,?,?,?,?,?,?)",
            (d.get("contrato_id"), d["competencia"], d["categoria"], d.get("descricao",""), d.get("fornecedor",""), d.get("valor_previsto",0), d.get("centro_custo",""), d.get("observacoes",""))
        )
    def update(self, obj_id, d):
        self.execute(
            "UPDATE despesas_planejamento SET contrato_id=?,competencia=?,categoria=?,descricao=?,fornecedor=?,valor_previsto=?,centro_custo=?,observacoes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (d.get("contrato_id"), d["competencia"], d["categoria"], d.get("descricao",""), d.get("fornecedor",""), d.get("valor_previsto",0), d.get("centro_custo",""), d.get("observacoes",""), obj_id)
        )
    def delete(self, obj_id):
        self.execute("DELETE FROM despesas_planejamento WHERE id=?", (obj_id,))

class DespesasRealizadoRepository(BaseRepository):
    def upsert_realizada_import(self, d):
        row = self.fetchone(
            "SELECT id FROM despesas_realizado WHERE COALESCE(contrato_id,0)=COALESCE(?,0) AND competencia=? AND categoria=? AND COALESCE(descricao,'')=COALESCE(?, '') AND COALESCE(documento_ref,'')=COALESCE(?, '')",
            (d.get("contrato_id"), d["competencia"], d["categoria"], d.get("descricao",""), d.get("documento_ref",""))
        )
        if row:
            self.execute(
                "UPDATE despesas_realizado SET fornecedor=?, valor_realizado=?, centro_custo=?, observacoes=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (d.get("fornecedor",""), d.get("valor_realizado",0), d.get("centro_custo",""), d.get("observacoes",""), row["id"])
            )
            return row["id"]
        return self.execute(
            "INSERT INTO despesas_realizado (contrato_id,competencia,categoria,descricao,fornecedor,valor_realizado,documento_ref,centro_custo,observacoes) VALUES (?,?,?,?,?,?,?,?,?)",
            (d.get("contrato_id"), d["competencia"], d["categoria"], d.get("descricao",""), d.get("fornecedor",""), d.get("valor_realizado",0), d.get("documento_ref",""), d.get("centro_custo",""), d.get("observacoes",""))
        )


    def list_all(self):
        return self.fetchall(
            "SELECT d.*, c.codigo AS contrato_codigo, c.nome AS contrato_nome FROM despesas_realizado d LEFT JOIN contratos c ON c.id=d.contrato_id ORDER BY d.competencia, c.codigo, d.categoria, d.id"
        )
    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM despesas_realizado WHERE id=?", (obj_id,))
    def create(self, d):
        return self.execute(
            "INSERT INTO despesas_realizado (contrato_id,competencia,categoria,descricao,fornecedor,valor_realizado,documento_ref,centro_custo,observacoes) VALUES (?,?,?,?,?,?,?,?,?)",
            (d.get("contrato_id"), d["competencia"], d["categoria"], d.get("descricao",""), d.get("fornecedor",""), d.get("valor_realizado",0), d.get("documento_ref",""), d.get("centro_custo",""), d.get("observacoes",""))
        )
    def update(self, obj_id, d):
        self.execute(
            "UPDATE despesas_realizado SET contrato_id=?,competencia=?,categoria=?,descricao=?,fornecedor=?,valor_realizado=?,documento_ref=?,centro_custo=?,observacoes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (d.get("contrato_id"), d["competencia"], d["categoria"], d.get("descricao",""), d.get("fornecedor",""), d.get("valor_realizado",0), d.get("documento_ref",""), d.get("centro_custo",""), d.get("observacoes",""), obj_id)
        )
    def delete(self, obj_id):
        self.execute("DELETE FROM despesas_realizado WHERE id=?", (obj_id,))

class ExportacaoRepository(BaseRepository):
    def resumo_contabil(self):
        return self.fetchall(
            """SELECT c.codigo AS contrato_codigo, c.nome AS contrato_nome,
                      COALESCE(rec.receita_faturada,0) AS receita_faturada,
                      COALESCE(cust_eq.custo_equipe,0) AS custo_equipe,
                      COALESCE(cust_ext.custo_terceiros,0) AS custo_terceiros,
                      COALESCE(desp_prev.valor_previsto,0) AS despesas_previstas,
                      COALESCE(desp_real.valor_realizado,0) AS despesas_realizadas
               FROM contratos c
               LEFT JOIN (
                    SELECT contrato_id, SUM(receita_faturada) AS receita_faturada
                    FROM produtividade_realizado GROUP BY contrato_id
               ) rec ON rec.contrato_id=c.id
               LEFT JOIN (
                    SELECT r.contrato_id, SUM(r.horas_equipe * COALESCE(p.custo_hora_equipe,0)) AS custo_equipe
                    FROM produtividade_realizado r
                    LEFT JOIN produtividade_parametros p ON p.disciplina=r.disciplina
                    GROUP BY r.contrato_id
               ) cust_eq ON cust_eq.contrato_id=c.id
               LEFT JOIN (
                    SELECT contrato_id, SUM(custo_total) AS custo_terceiros
                    FROM produtividade_custos GROUP BY contrato_id
               ) cust_ext ON cust_ext.contrato_id=c.id
               LEFT JOIN (
                    SELECT contrato_id, SUM(valor_previsto) AS valor_previsto
                    FROM despesas_planejamento GROUP BY contrato_id
               ) desp_prev ON desp_prev.contrato_id=c.id
               LEFT JOIN (
                    SELECT contrato_id, SUM(valor_realizado) AS valor_realizado
                    FROM despesas_realizado GROUP BY contrato_id
               ) desp_real ON desp_real.contrato_id=c.id
               ORDER BY c.codigo"""
        )


    def resumo_anual_mensal(self):
        return self.fetchall(
            """SELECT x.competencia,
                      SUM(x.receita_faturada) AS receita_faturada,
                      SUM(x.custo_equipe) AS custo_equipe,
                      SUM(x.custo_terceiros) AS custo_terceiros,
                      SUM(x.despesas_realizadas) AS despesas_realizadas
               FROM (
                    SELECT competencia, receita_faturada, 0 AS custo_equipe, 0 AS custo_terceiros, 0 AS despesas_realizadas
                    FROM produtividade_realizado
                    UNION ALL
                    SELECT r.competencia, 0,
                           (r.horas_equipe * COALESCE(p.custo_hora_equipe,0)) AS custo_equipe,
                           0, 0
                    FROM produtividade_realizado r
                    LEFT JOIN produtividade_parametros p ON p.disciplina=r.disciplina
                    UNION ALL
                    SELECT competencia, 0, 0, custo_total, 0
                    FROM produtividade_custos
                    UNION ALL
                    SELECT competencia, 0, 0, 0, valor_realizado
                    FROM despesas_realizado
               ) x
               GROUP BY x.competencia
               ORDER BY x.competencia"""
        )

    def resumo_anual_categorias(self):
        return self.fetchall(
            """SELECT categoria,
                      SUM(valor_previsto) AS despesas_previstas,
                      0 AS despesas_realizadas
               FROM despesas_planejamento
               GROUP BY categoria
               UNION ALL
               SELECT categoria,
                      0 AS despesas_previstas,
                      SUM(valor_realizado) AS despesas_realizadas
               FROM despesas_realizado
               GROUP BY categoria"""
        )
