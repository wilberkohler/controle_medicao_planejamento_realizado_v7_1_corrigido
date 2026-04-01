from __future__ import annotations

from repositories.base import BaseRepository


class ProdutividadeParametroRepository(BaseRepository):
    def list_all(self):
        return self.fetchall("SELECT * FROM produtividade_parametros ORDER BY disciplina")

    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM produtividade_parametros WHERE id=?", (obj_id,))

    def get_by_disciplina(self, disciplina):
        return self.fetchone("SELECT * FROM produtividade_parametros WHERE disciplina=?", (disciplina,))

    def create(self, d):
        return self.execute(
            "INSERT INTO produtividade_parametros (disciplina,horas_por_a1,custo_hora_equipe,ativo,observacoes) VALUES (?,?,?,?,?)",
            (d["disciplina"], d.get("horas_por_a1", 0), d.get("custo_hora_equipe", 0), d.get("ativo", 1), d.get("observacoes", "")),
        )

    def update(self, obj_id, d):
        self.execute(
            "UPDATE produtividade_parametros SET disciplina=?,horas_por_a1=?,custo_hora_equipe=?,ativo=?,observacoes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (d["disciplina"], d.get("horas_por_a1", 0), d.get("custo_hora_equipe", 0), d.get("ativo", 1), d.get("observacoes", ""), obj_id),
        )

    def delete(self, obj_id):
        self.execute("DELETE FROM produtividade_parametros WHERE id=?", (obj_id,))


class ProdutividadeMetaRepository(BaseRepository):
    def list_all(self):
        return self.fetchall(
            """SELECT m.*, u.nome AS usuario_nome, c.codigo AS contrato_codigo, c.nome AS contrato_nome
               FROM produtividade_metas m
               INNER JOIN usuarios u ON u.id=m.usuario_id
               INNER JOIN contratos c ON c.id=m.contrato_id
               ORDER BY m.competencia, c.codigo, u.nome, m.disciplina"""
        )

    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM produtividade_metas WHERE id=?", (obj_id,))

    def create(self, d):
        return self.execute(
            """INSERT INTO produtividade_metas
               (usuario_id,contrato_id,etapa_id,grupo_id,competencia,disciplina,meta_mensal_a1,horas_por_a1,horas_planejadas,receita_prevista,observacoes,status)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (d["usuario_id"], d["contrato_id"], d.get("etapa_id"), d.get("grupo_id"), d["competencia"], d["disciplina"], d.get("meta_mensal_a1", 0), d.get("horas_por_a1", 0), d.get("horas_planejadas", 0), d.get("receita_prevista", 0), d.get("observacoes", ""), d.get("status", "planejado")),
        )

    def update(self, obj_id, d):
        self.execute(
            """UPDATE produtividade_metas
               SET usuario_id=?,contrato_id=?,etapa_id=?,grupo_id=?,competencia=?,disciplina=?,meta_mensal_a1=?,horas_por_a1=?,horas_planejadas=?,receita_prevista=?,observacoes=?,status=?,updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (d["usuario_id"], d["contrato_id"], d.get("etapa_id"), d.get("grupo_id"), d["competencia"], d["disciplina"], d.get("meta_mensal_a1", 0), d.get("horas_por_a1", 0), d.get("horas_planejadas", 0), d.get("receita_prevista", 0), d.get("observacoes", ""), d.get("status", "planejado"), obj_id),
        )

    def delete(self, obj_id):
        self.execute("DELETE FROM produtividade_metas WHERE id=?", (obj_id,))


class ProdutividadeRealizadoRepository(BaseRepository):
    def list_all(self):
        return self.fetchall(
            """SELECT r.*, u.nome AS usuario_nome, c.codigo AS contrato_codigo, c.nome AS contrato_nome
               FROM produtividade_realizado r
               INNER JOIN usuarios u ON u.id=r.usuario_id
               INNER JOIN contratos c ON c.id=r.contrato_id
               ORDER BY r.competencia, c.codigo, u.nome, r.disciplina"""
        )

    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM produtividade_realizado WHERE id=?", (obj_id,))

    def create(self, d):
        return self.execute(
            """INSERT INTO produtividade_realizado
               (usuario_id,contrato_id,etapa_id,grupo_id,entregavel_id,competencia,disciplina,produzido_a1,horas_por_a1,horas_equipe,receita_faturada,observacoes,status_aprovacao)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (d["usuario_id"], d["contrato_id"], d.get("etapa_id"), d.get("grupo_id"), d.get("entregavel_id"), d["competencia"], d["disciplina"], d.get("produzido_a1", 0), d.get("horas_por_a1", 0), d.get("horas_equipe", 0), d.get("receita_faturada", 0), d.get("observacoes", ""), d.get("status_aprovacao", "rascunho")),
        )

    def update(self, obj_id, d):
        self.execute(
            """UPDATE produtividade_realizado
               SET usuario_id=?,contrato_id=?,etapa_id=?,grupo_id=?,entregavel_id=?,competencia=?,disciplina=?,produzido_a1=?,horas_por_a1=?,horas_equipe=?,receita_faturada=?,observacoes=?,status_aprovacao=?,updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (d["usuario_id"], d["contrato_id"], d.get("etapa_id"), d.get("grupo_id"), d.get("entregavel_id"), d["competencia"], d["disciplina"], d.get("produzido_a1", 0), d.get("horas_por_a1", 0), d.get("horas_equipe", 0), d.get("receita_faturada", 0), d.get("observacoes", ""), d.get("status_aprovacao", "rascunho"), obj_id),
        )

    def delete(self, obj_id):
        self.execute("DELETE FROM produtividade_realizado WHERE id=?", (obj_id,))


class ProdutividadeCustoRepository(BaseRepository):
    def list_all(self):
        return self.fetchall(
            """SELECT cst.*, c.codigo AS contrato_codigo
               FROM produtividade_custos cst
               INNER JOIN contratos c ON c.id=cst.contrato_id
               ORDER BY cst.competencia, c.codigo, cst.disciplina, cst.tipo_recurso"""
        )

    def get_by_id(self, obj_id):
        return self.fetchone("SELECT * FROM produtividade_custos WHERE id=?", (obj_id,))

    def create(self, d):
        return self.execute(
            """INSERT INTO produtividade_custos
               (usuario_id,contrato_id,etapa_id,grupo_id,competencia,disciplina,tipo_recurso,fornecedor_nome,horas,custo_hora,custo_total,observacoes,status_aprovacao)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (d.get("usuario_id"), d["contrato_id"], d.get("etapa_id"), d.get("grupo_id"), d["competencia"], d["disciplina"], d["tipo_recurso"], d.get("fornecedor_nome", ""), d.get("horas", 0), d.get("custo_hora", 0), d.get("custo_total", 0), d.get("observacoes", ""), d.get("status_aprovacao", "rascunho")),
        )

    def update(self, obj_id, d):
        self.execute(
            """UPDATE produtividade_custos
               SET usuario_id=?,contrato_id=?,etapa_id=?,grupo_id=?,competencia=?,disciplina=?,tipo_recurso=?,fornecedor_nome=?,horas=?,custo_hora=?,custo_total=?,observacoes=?,status_aprovacao=?,updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (d.get("usuario_id"), d["contrato_id"], d.get("etapa_id"), d.get("grupo_id"), d["competencia"], d["disciplina"], d["tipo_recurso"], d.get("fornecedor_nome", ""), d.get("horas", 0), d.get("custo_hora", 0), d.get("custo_total", 0), d.get("observacoes", ""), d.get("status_aprovacao", "rascunho"), obj_id),
        )

    def delete(self, obj_id):
        self.execute("DELETE FROM produtividade_custos WHERE id=?", (obj_id,))


class ProdutividadeAnalyticsRepository(BaseRepository):
    def resumo(self, contrato_id=None):
        clause = "WHERE contrato_id=?" if contrato_id else ""
        params = (contrato_id,) if contrato_id else ()
        meta = self.fetchone(f"SELECT COALESCE(SUM(meta_mensal_a1),0) AS meta_a1, COALESCE(SUM(horas_planejadas),0) AS horas_planejadas, COALESCE(SUM(receita_prevista),0) AS receita_prevista FROM produtividade_metas {clause}", params)
        real = self.fetchone(f"SELECT COALESCE(SUM(produzido_a1),0) AS produzido_a1, COALESCE(SUM(horas_equipe),0) AS horas_equipe, COALESCE(SUM(receita_faturada),0) AS receita_faturada FROM produtividade_realizado {clause}", params)
        custo_ext = self.fetchone(f"SELECT COALESCE(SUM(custo_total),0) AS custo_total, COALESCE(SUM(horas),0) AS horas_total FROM produtividade_custos {clause}", params)
        custo_equipe = self.fetchone(f"""SELECT COALESCE(SUM(r.horas_equipe * COALESCE(p.custo_hora_equipe,0)),0) AS custo_apropriado FROM produtividade_realizado r LEFT JOIN produtividade_parametros p ON p.disciplina = r.disciplina {('WHERE r.contrato_id=?' if contrato_id else '')}""", params)
        return {"meta_a1": meta["meta_a1"], "produzido_a1": real["produzido_a1"], "desvio_a1": float(real["produzido_a1"] or 0) - float(meta["meta_a1"] or 0), "horas_planejadas": meta["horas_planejadas"], "horas_equipe": real["horas_equipe"], "horas_terceiros": custo_ext["horas_total"], "receita_prevista": meta["receita_prevista"], "receita_faturada": real["receita_faturada"], "custo_equipe_apropriado": custo_equipe["custo_apropriado"], "custo_terceiros": custo_ext["custo_total"], "custo_total": float(custo_equipe["custo_apropriado"] or 0) + float(custo_ext["custo_total"] or 0), "margem_total": float(real["receita_faturada"] or 0) - (float(custo_equipe["custo_apropriado"] or 0) + float(custo_ext["custo_total"] or 0))}

    def ranking_projetistas(self, contrato_id=None):
        clause = "WHERE r.contrato_id=?" if contrato_id else ""
        params = (contrato_id,) if contrato_id else ()
        return self.fetchall(f"""SELECT u.nome AS projetista, r.disciplina, SUM(r.produzido_a1) AS produzido_a1, SUM(r.horas_equipe) AS horas_equipe, CASE WHEN SUM(r.horas_equipe)=0 THEN 0 ELSE SUM(r.produzido_a1)/SUM(r.horas_equipe) END AS produtividade_a1_h, SUM(r.receita_faturada) AS receita_faturada, SUM(r.horas_equipe * COALESCE(p.custo_hora_equipe,0)) AS custo_equipe, SUM(r.receita_faturada) - SUM(r.horas_equipe * COALESCE(p.custo_hora_equipe,0)) AS margem_equipe FROM produtividade_realizado r INNER JOIN usuarios u ON u.id=r.usuario_id LEFT JOIN produtividade_parametros p ON p.disciplina=r.disciplina {clause} GROUP BY u.nome, r.disciplina ORDER BY produtividade_a1_h DESC, produzido_a1 DESC""", params)

    def por_disciplina(self, contrato_id=None):
        clause = "WHERE x.contrato_id=?" if contrato_id else ""
        params = (contrato_id,) if contrato_id else ()
        return self.fetchall(f"""SELECT x.disciplina, SUM(x.meta_a1) AS meta_a1, SUM(x.produzido_a1) AS produzido_a1, SUM(x.receita_prevista) AS receita_prevista, SUM(x.receita_faturada) AS receita_faturada, SUM(x.custo_equipe) AS custo_equipe, SUM(x.custo_terceiros) AS custo_terceiros, SUM(x.custo_equipe + x.custo_terceiros) AS custo_total FROM ( SELECT contrato_id, disciplina, meta_mensal_a1 AS meta_a1, 0 AS produzido_a1, receita_prevista, 0 AS receita_faturada, 0 AS custo_equipe, 0 AS custo_terceiros FROM produtividade_metas UNION ALL SELECT r.contrato_id, r.disciplina, 0, r.produzido_a1, 0, r.receita_faturada, (r.horas_equipe * COALESCE(p.custo_hora_equipe,0)), 0 FROM produtividade_realizado r LEFT JOIN produtividade_parametros p ON p.disciplina = r.disciplina UNION ALL SELECT contrato_id, disciplina, 0, 0, 0, 0, 0, custo_total FROM produtividade_custos ) x {clause} GROUP BY x.disciplina ORDER BY x.disciplina""", params)

    def comparativo_competencia(self, contrato_id=None):
        clause = "WHERE x.contrato_id=?" if contrato_id else ""
        params = (contrato_id,) if contrato_id else ()
        return self.fetchall(f"""SELECT x.competencia, SUM(x.receita_prevista) AS receita_prevista, SUM(x.receita_faturada) AS receita_faturada, SUM(x.custo_equipe) AS custo_equipe, SUM(x.custo_terceiros) AS custo_terceiros, SUM(x.custo_equipe + x.custo_terceiros) AS custo_total FROM ( SELECT contrato_id, competencia, receita_prevista, 0 AS receita_faturada, 0 AS custo_equipe, 0 AS custo_terceiros FROM produtividade_metas UNION ALL SELECT r.contrato_id, r.competencia, 0, r.receita_faturada, (r.horas_equipe * COALESCE(p.custo_hora_equipe,0)), 0 FROM produtividade_realizado r LEFT JOIN produtividade_parametros p ON p.disciplina = r.disciplina UNION ALL SELECT contrato_id, competencia, 0, 0, 0, custo_total FROM produtividade_custos ) x {clause} GROUP BY x.competencia ORDER BY x.competencia""", params)

    def dre_gerencial_contratos(self, imposto_percentual=16.8):
        return self.dre_gerencial_por_nivel("contrato", imposto_percentual, None)

    def dre_gerencial_por_nivel(self, nivel="contrato", imposto_percentual=16.8, contrato_id=None):
        nivel = (nivel or "contrato").lower()
        if nivel == "etapa":
            label_sql = "COALESCE(e.codigo,'(sem etapa)')"
            join_extra = "LEFT JOIN etapas e ON e.id = x.etapa_id"
            group_sql = "COALESCE(e.codigo,'(sem etapa)')"
            select_nome = "''"
        elif nivel == "grupo":
            label_sql = "COALESCE(g.codigo,'(sem grupo)')"
            join_extra = "LEFT JOIN grupos g ON g.id = x.grupo_id LEFT JOIN etapas e ON e.id = x.etapa_id"
            group_sql = "COALESCE(g.codigo,'(sem grupo)')"
            select_nome = "COALESCE(e.codigo,'')"
        else:
            label_sql = "c.codigo"
            join_extra = ""
            group_sql = "c.codigo"
            select_nome = "c.nome"
        clause = "WHERE x.contrato_id=?" if contrato_id else ""
        params = (contrato_id,) if contrato_id else ()
        rows = self.fetchall(f"""SELECT {label_sql} AS nivel_codigo, {select_nome} AS nivel_nome, SUM(x.receita_prevista) AS receita_prevista, SUM(x.receita_faturada) AS receita_faturada, SUM(x.custo_equipe) AS custo_equipe, SUM(x.custo_terceiros) AS custo_terceiros, SUM(x.despesas_gerais) AS despesas_gerais FROM ( SELECT m.contrato_id, m.etapa_id, m.grupo_id, m.receita_prevista, 0 AS receita_faturada, 0 AS custo_equipe, 0 AS custo_terceiros, 0 AS despesas_gerais FROM produtividade_metas m UNION ALL SELECT r.contrato_id, r.etapa_id, r.grupo_id, 0, r.receita_faturada, (r.horas_equipe * COALESCE(p.custo_hora_equipe,0)), 0, 0 FROM produtividade_realizado r LEFT JOIN produtividade_parametros p ON p.disciplina = r.disciplina UNION ALL SELECT cst.contrato_id, cst.etapa_id, cst.grupo_id, 0, 0, 0, cst.custo_total, 0 FROM produtividade_custos cst UNION ALL SELECT dr.contrato_id, NULL, NULL, 0, 0, 0, 0, dr.valor_realizado FROM despesas_realizado dr ) x INNER JOIN contratos c ON c.id=x.contrato_id {join_extra} {clause} GROUP BY {group_sql} ORDER BY {group_sql}""", params)
        return [self._dre_row_dict(r, imposto_percentual) for r in rows]

    def _dre_row_dict(self, r, imposto_percentual):
        receita_prevista = float(r["receita_prevista"] or 0)
        receita_faturada = float(r["receita_faturada"] or 0)
        custo_equipe = float(r["custo_equipe"] or 0)
        custo_terceiros = float(r["custo_terceiros"] or 0)
        despesas_gerais = float(r["despesas_gerais"] or 0)
        custo_total = custo_equipe + custo_terceiros + despesas_gerais
        margem_bruta = receita_faturada - custo_total
        imp = float(imposto_percentual or 0)
        impostos = receita_faturada * (imp / 100.0) if receita_faturada > 0 else 0.0
        receita_liquida = receita_faturada - impostos
        margem_operacional = margem_bruta - impostos
        return {"nivel_codigo": r["nivel_codigo"], "nivel_nome": r["nivel_nome"], "receita_prevista": receita_prevista, "receita_faturada": receita_faturada, "receita_bruta": receita_faturada, "imposto_percentual": imp, "impostos_sobre_faturamento": impostos, "deducoes_impostos": impostos, "receita_liquida": receita_liquida, "custo_equipe": custo_equipe, "custo_terceiros": custo_terceiros, "despesas_gerais": despesas_gerais, "custo_total": custo_total, "margem_bruta": margem_bruta, "margem_operacional": margem_operacional, "margem_percentual": (margem_bruta / receita_faturada * 100.0) if receita_faturada else 0.0, "margem_liquida_percentual": (margem_operacional / receita_faturada * 100.0) if receita_faturada else 0.0, "desvio_receita": receita_faturada - receita_prevista}

    def dre_mensal_competencia(self, imposto_percentual=16.8, contrato_id=None):
        params = (contrato_id,) if contrato_id else ()
        clause_meta = "WHERE contrato_id=?" if contrato_id else ""
        clause_real = "WHERE r.contrato_id=?" if contrato_id else ""
        clause_cust = "WHERE contrato_id=?" if contrato_id else ""
        clause_desp = "WHERE contrato_id=?" if contrato_id else ""
        idx = {}
        def touch(comp):
            if comp not in idx:
                idx[comp] = {"competencia": comp, "receita_prevista": 0.0, "receita_bruta": 0.0, "custo_equipe": 0.0, "custo_terceiros": 0.0, "despesas_previstas": 0.0, "despesas_realizadas": 0.0, "imposto_percentual": float(imposto_percentual or 0)}
            return idx[comp]
        for r in self.fetchall(f"SELECT competencia, SUM(receita_prevista) AS receita_prevista FROM produtividade_metas {clause_meta} GROUP BY competencia", params): touch(r["competencia"])["receita_prevista"] = float(r["receita_prevista"] or 0)
        for r in self.fetchall(f"SELECT r.competencia, SUM(r.receita_faturada) AS receita_faturada, SUM(r.horas_equipe * COALESCE(p.custo_hora_equipe,0)) AS custo_equipe FROM produtividade_realizado r LEFT JOIN produtividade_parametros p ON p.disciplina=r.disciplina {clause_real} GROUP BY r.competencia", params):
            item = touch(r["competencia"]); item["receita_bruta"] = float(r["receita_faturada"] or 0); item["custo_equipe"] = float(r["custo_equipe"] or 0)
        for r in self.fetchall(f"SELECT competencia, SUM(custo_total) AS custo_terceiros FROM produtividade_custos {clause_cust} GROUP BY competencia", params): touch(r["competencia"])["custo_terceiros"] = float(r["custo_terceiros"] or 0)
        for r in self.fetchall(f"SELECT competencia, SUM(valor_previsto) AS despesas_previstas FROM despesas_planejamento {clause_desp} GROUP BY competencia", params): touch(r["competencia"])["despesas_previstas"] = float(r["despesas_previstas"] or 0)
        for r in self.fetchall(f"SELECT competencia, SUM(valor_realizado) AS despesas_realizadas FROM despesas_realizado {clause_desp} GROUP BY competencia", params): touch(r["competencia"])["despesas_realizadas"] = float(r["despesas_realizadas"] or 0)
        out = []
        imp = float(imposto_percentual or 0)
        for comp in sorted(idx.keys()):
            item = idx[comp]
            receita_bruta = item["receita_bruta"]
            impostos = receita_bruta * (imp / 100.0) if receita_bruta > 0 else 0.0
            receita_liquida = receita_bruta - impostos
            custo_total = item["custo_equipe"] + item["custo_terceiros"] + item["despesas_realizadas"]
            margem_bruta = receita_bruta - custo_total
            margem_operacional = margem_bruta - impostos
            out.append({"competencia": comp, "receita_prevista": item["receita_prevista"], "receita_bruta": receita_bruta, "receita_faturada": receita_bruta, "deducoes_impostos": impostos, "impostos_sobre_faturamento": impostos, "receita_liquida": receita_liquida, "custo_equipe": item["custo_equipe"], "custo_terceiros": item["custo_terceiros"], "despesas_previstas": item["despesas_previstas"], "despesas_gerais": item["despesas_realizadas"], "despesas_realizadas": item["despesas_realizadas"], "custo_total": custo_total, "margem_bruta": margem_bruta, "margem_operacional": margem_operacional, "imposto_percentual": imp, "margem_percentual": (margem_bruta / receita_bruta * 100.0) if receita_bruta else 0.0, "margem_liquida_percentual": (margem_operacional / receita_bruta * 100.0) if receita_bruta else 0.0})
        return out

    def dre_mensal_composicao(self, competencia, contrato_id=None):
        params = [competencia, competencia, competencia, competencia, competencia]
        clause_contrato = ''
        if contrato_id:
            clause_contrato = ' AND c.id=?'
            params.append(contrato_id)
        return self.fetchall(f'''SELECT c.codigo AS referencia, c.nome AS nome, COALESCE(mp.receita_prevista,0) AS receita_prevista, COALESCE(rp.receita_faturada,0) AS receita_bruta, COALESCE(eq.custo_equipe,0) AS custo_equipe, COALESCE(ct.custo_terceiros,0) AS custo_terceiros, COALESCE(dg.despesas_gerais,0) AS despesas_gerais FROM contratos c LEFT JOIN (SELECT contrato_id, SUM(receita_prevista) AS receita_prevista FROM produtividade_metas WHERE competencia=? GROUP BY contrato_id) mp ON mp.contrato_id=c.id LEFT JOIN (SELECT contrato_id, SUM(receita_faturada) AS receita_faturada FROM produtividade_realizado WHERE competencia=? GROUP BY contrato_id) rp ON rp.contrato_id=c.id LEFT JOIN (SELECT r.contrato_id, SUM(r.horas_equipe * COALESCE(p.custo_hora_equipe,0)) AS custo_equipe FROM produtividade_realizado r LEFT JOIN produtividade_parametros p ON p.disciplina=r.disciplina WHERE r.competencia=? GROUP BY r.contrato_id) eq ON eq.contrato_id=c.id LEFT JOIN (SELECT contrato_id, SUM(custo_total) AS custo_terceiros FROM produtividade_custos WHERE competencia=? GROUP BY contrato_id) ct ON ct.contrato_id=c.id LEFT JOIN (SELECT contrato_id, SUM(valor_realizado) AS despesas_gerais FROM despesas_realizado WHERE competencia=? GROUP BY contrato_id) dg ON dg.contrato_id=c.id WHERE 1=1 {clause_contrato} ORDER BY c.codigo''', tuple(params))


class DREParametrosRepository(BaseRepository):
    def get_ativo(self):
        row = self.fetchone("SELECT * FROM dre_parametros WHERE ativo=1 ORDER BY id DESC LIMIT 1")
        if row:
            return row
        self.execute("INSERT INTO dre_parametros (imposto_percentual, ativo) VALUES (?,1)", (16.8,))
        return self.fetchone("SELECT * FROM dre_parametros WHERE ativo=1 ORDER BY id DESC LIMIT 1")

    def set_percentual(self, percentual):
        self.execute("UPDATE dre_parametros SET ativo=0")
        self.execute("INSERT INTO dre_parametros (imposto_percentual, ativo) VALUES (?,1)", (percentual,))
