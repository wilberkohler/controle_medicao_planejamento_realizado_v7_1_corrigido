from repositories.base import BaseRepository
from utils.number_utils import to_float

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

    def comparativo_acumulado(self, contrato_id=None):
        rows = self.comparativo_mensal(contrato_id)
        acc = {}
        result = []
        for row in rows:
            key = (
                row["contrato_codigo"],
                row["etapa_codigo"],
                row["grupo_codigo"],
                row["entregavel_codigo"],
            )
            if key not in acc:
                acc[key] = {
                    "vp": 0.0,
                    "vr": 0.0,
                    "pp": 0.0,
                    "pr": 0.0,
                }
            acc[key]["vp"] += float(row["valor_previsto_mes"] or 0)
            acc[key]["vr"] += float(row["valor_realizado_mes"] or 0)
            acc[key]["pp"] += float(row["percentual_previsto_mes"] or 0)
            acc[key]["pr"] += float(row["percentual_realizado_mes"] or 0)
            result.append({
                "contrato_codigo": row["contrato_codigo"],
                "etapa_codigo": row["etapa_codigo"],
                "etapa_descricao": row["etapa_descricao"],
                "grupo_codigo": row["grupo_codigo"],
                "grupo_descricao": row["grupo_descricao"],
                "entregavel_codigo": row["entregavel_codigo"],
                "entregavel_descricao": row["entregavel_descricao"],
                "competencia": row["competencia"],
                "valor_previsto_acumulado": acc[key]["vp"],
                "valor_realizado_acumulado": acc[key]["vr"],
                "saldo_acumulado": acc[key]["vp"] - acc[key]["vr"],
                "percentual_previsto_acumulado": acc[key]["pp"],
                "percentual_realizado_acumulado": acc[key]["pr"],
                "saldo_percentual_acumulado": acc[key]["pp"] - acc[key]["pr"],
            })
        return result


    def aprovacoes_resumo(self):
        rows = self.fetchall(
            '''SELECT status, COUNT(*) AS qtde
               FROM workflow_aprovacoes
               GROUP BY status'''
        )
        result = {"rascunho": 0, "em_aprovacao": 0, "aprovado": 0, "rejeitado": 0}
        for r in rows:
            result[r["status"]] = r["qtde"]
        return result


    def dashboard_heatmap(self, contrato_id=None, level="contrato"):
        where = ""
        params = ()
        if contrato_id:
            where = "WHERE e.contrato_id = ?"
            params = (contrato_id,)

        if level == "grupo":
            select_label = "g.codigo AS nivel_codigo"
            group_by = "c.codigo, g.codigo, COALESCE(pm.competencia, rm.competencia)"
            order_by = "c.codigo, g.codigo, COALESCE(pm.competencia, rm.competencia)"
        elif level == "etapa":
            select_label = "e.codigo AS nivel_codigo"
            group_by = "c.codigo, e.codigo, COALESCE(pm.competencia, rm.competencia)"
            order_by = "c.codigo, e.codigo, COALESCE(pm.competencia, rm.competencia)"
        else:
            select_label = "c.codigo AS nivel_codigo"
            group_by = "c.codigo, COALESCE(pm.competencia, rm.competencia)"
            order_by = "c.codigo, COALESCE(pm.competencia, rm.competencia)"

        return self.fetchall(
            f'''SELECT c.codigo AS contrato_codigo,
                       e.codigo AS etapa_codigo,
                       g.codigo AS grupo_codigo,
                       {select_label},
                       COALESCE(pm.competencia, rm.competencia) AS competencia,
                       SUM(COALESCE(pm.valor_previsto_mes,0) - COALESCE(rm.valor_realizado_mes,0)) AS saldo
                FROM etapas e
                INNER JOIN contratos c ON c.id = e.contrato_id
                LEFT JOIN grupos g ON g.etapa_id = e.id
                LEFT JOIN planejamento_mensal pm ON pm.etapa_id = e.id
                LEFT JOIN realizado_mensal rm ON rm.etapa_id = e.id AND rm.competencia = pm.competencia
                {where}
                GROUP BY {group_by}
                ORDER BY {order_by}''',
            params
        )

    def produtividade_resumo_executivo(self, contrato_id=None):
        params = (contrato_id,) if contrato_id else ()
        clause = "WHERE contrato_id=?" if contrato_id else ""
        rec = self.fetchone(f"SELECT COALESCE(SUM(receita_faturada),0) AS receita_faturada FROM produtividade_realizado {clause}", params)
        ext = self.fetchone(f"SELECT COALESCE(SUM(custo_total),0) AS custo_ext FROM produtividade_custos {clause}", params)
        equipe = self.fetchone(
            f'''SELECT COALESCE(SUM(r.horas_equipe * COALESCE(p.custo_hora_equipe,0)),0) AS custo_eq
                FROM produtividade_realizado r
                LEFT JOIN produtividade_parametros p ON p.disciplina = r.disciplina
                {("WHERE r.contrato_id=?" if contrato_id else "")}''',
            params
        )
        custo_total = float(equipe["custo_eq"] or 0) + float(ext["custo_ext"] or 0)
        return {
            "receita_faturada_prod": rec["receita_faturada"],
            "custo_total_prod": custo_total,
            "margem_prod": float(rec["receita_faturada"] or 0) - custo_total
        }


    def home_summary(self):
        pend = self.fetchone("SELECT COUNT(*) AS qtde FROM workflow_aprovacoes WHERE status IN ('rascunho','em_aprovacao')")
        abertas = self.fetchone("SELECT COUNT(DISTINCT competencia) AS qtde FROM medicoes WHERE status='aberta'")
        aprov = self.fetchone("SELECT COUNT(*) AS qtde FROM workflow_aprovacoes WHERE status='aprovado'")
        div = self.fetchone("SELECT COUNT(*) AS qtde FROM workflow_aprovacoes WHERE status IN ('rejeitado','divergente')")
        return {
            'pendencias_mes': int((pend['qtde'] if pend else 0) or 0),
            'competencias_abertas': int((abertas['qtde'] if abertas else 0) or 0),
            'itens_aprovados': int((aprov['qtde'] if aprov else 0) or 0),
            'itens_divergentes': int((div['qtde'] if div else 0) or 0),
        }

    def open_competencias(self):
        return self.fetchall("SELECT competencia, status, COUNT(*) AS qtde FROM medicoes GROUP BY competencia, status ORDER BY competencia DESC")

    def pending_items(self):
        return self.fetchall("SELECT modulo, registro_id, status, COALESCE(data_solicitacao, created_at) AS referencia FROM workflow_aprovacoes WHERE status IN ('rascunho','em_aprovacao','rejeitado') ORDER BY COALESCE(updated_at, created_at) DESC LIMIT 20")

    def critical_deviations(self):
        return self.fetchall("SELECT c.codigo AS contrato_codigo, e.codigo AS etapa_codigo, g.codigo AS grupo_codigo, ent.codigo AS entregavel_codigo, COALESCE(pm.competencia, rm.competencia) AS competencia, COALESCE(pm.valor_previsto_mes,0) AS previsto, COALESCE(rm.valor_realizado_mes,0) AS realizado, (COALESCE(pm.valor_previsto_mes,0) - COALESCE(rm.valor_realizado_mes,0)) AS saldo FROM entregaveis ent INNER JOIN contratos c ON c.id=ent.contrato_id INNER JOIN etapas e ON e.id=ent.etapa_id INNER JOIN grupos g ON g.id=ent.grupo_id LEFT JOIN planejamento_mensal pm ON pm.entregavel_id=ent.id LEFT JOIN realizado_mensal rm ON rm.entregavel_id=ent.id AND rm.competencia=pm.competencia ORDER BY ABS(COALESCE(pm.valor_previsto_mes,0) - COALESCE(rm.valor_realizado_mes,0)) DESC LIMIT 20")

    def latest_launches(self):
        return self.fetchall("SELECT 'realizado' AS origem, CAST(r.id AS TEXT) AS registro, r.competencia, COALESCE(r.responsavel,'' ) AS responsavel, r.updated_at AS data_ref, r.observacoes AS detalhe FROM realizado_mensal r UNION ALL SELECT 'despesa_realizada', CAST(d.id AS TEXT), d.competencia, COALESCE(d.fornecedor,''), d.updated_at, d.descricao FROM despesas_realizado d UNION ALL SELECT 'produtividade', CAST(p.id AS TEXT), p.competencia, COALESCE(u.nome,''), p.updated_at, p.observacoes FROM produtividade_realizado p LEFT JOIN usuarios u ON u.id=p.usuario_id ORDER BY data_ref DESC LIMIT 20")

    def global_search(self, q):
        like = f"%{q}%"
        return self.fetchall("SELECT tipo, referencia, detalhe, extra FROM (SELECT 'contrato' AS tipo, codigo AS referencia, nome AS detalhe, COALESCE(cliente,'') AS extra FROM contratos UNION ALL SELECT 'projetista', nome, email, perfil FROM usuarios UNION ALL SELECT 'entregável', codigo, descricao, '' FROM entregaveis UNION ALL SELECT 'competência', competencia, status, CAST(numero_medicao AS TEXT) FROM medicoes UNION ALL SELECT 'categoria', categoria, COALESCE(descricao,''), COALESCE(competencia,'') FROM despesas_realizado UNION ALL SELECT 'categoria', categoria, COALESCE(descricao,''), COALESCE(competencia,'') FROM despesas_planejamento) x WHERE LOWER(COALESCE(referencia,'')) LIKE LOWER(?) OR LOWER(COALESCE(detalhe,'')) LIKE LOWER(?) OR LOWER(COALESCE(extra,'')) LIKE LOWER(?) ORDER BY tipo, referencia LIMIT 100", (like, like, like))


    def dashboard_contracts_detail(self):
        return self.fetchall(
            '''SELECT c.id AS contrato_id, c.codigo AS contrato_codigo, c.nome AS contrato_nome,
                      COALESCE(SUM(pm.valor_previsto_mes),0) AS valor_previsto,
                      COALESCE(SUM(rm.valor_realizado_mes),0) AS valor_realizado
               FROM contratos c
               LEFT JOIN planejamento_mensal pm ON pm.contrato_id=c.id
               LEFT JOIN realizado_mensal rm ON rm.contrato_id=c.id
               GROUP BY c.id, c.codigo, c.nome
               ORDER BY c.codigo'''
        )

    def dashboard_stage_detail(self, contrato_id=None):
        params=()
        where=''
        if contrato_id:
            where='WHERE e.contrato_id=?'
            params=(contrato_id,)
        return self.fetchall(
            f'''SELECT c.id AS contrato_id, c.codigo AS contrato_codigo, e.id AS etapa_id, e.codigo AS etapa_codigo,
                       COALESCE(SUM(pm.valor_previsto_mes),0) AS valor_previsto,
                       COALESCE(SUM(rm.valor_realizado_mes),0) AS valor_realizado
                FROM etapas e
                INNER JOIN contratos c ON c.id=e.contrato_id
                LEFT JOIN planejamento_mensal pm ON pm.etapa_id=e.id
                LEFT JOIN realizado_mensal rm ON rm.etapa_id=e.id
                {where}
                GROUP BY c.id, c.codigo, e.id, e.codigo
                ORDER BY c.codigo, e.codigo''',
            params
        )

    def dashboard_monthly_curve(self, contrato_id=None):
        params=()
        where=''
        if contrato_id:
            where='WHERE x.contrato_id=?'
            params=(contrato_id,)
        return self.fetchall(
            f'''SELECT x.competencia,
                       SUM(x.valor_previsto_mes) AS valor_previsto_mes,
                       SUM(x.valor_realizado_mes) AS valor_realizado_mes
                FROM (
                    SELECT contrato_id, competencia, valor_previsto_mes, 0 AS valor_realizado_mes FROM planejamento_mensal
                    UNION ALL
                    SELECT contrato_id, competencia, 0, valor_realizado_mes FROM realizado_mensal
                ) x
                {where}
                GROUP BY x.competencia
                ORDER BY x.competencia''',
            params
        )

    def dashboard_top_deviations(self, contrato_id=None, limite=15, competencia=None, etapa_codigo=None, grupo_codigo=None):
        params=[]; where=[]
        if contrato_id:
            where.append('ent.contrato_id=?'); params.append(contrato_id)
        if competencia:
            where.append('COALESCE(pm.competencia, rm.competencia)=?'); params.append(competencia)
        if etapa_codigo:
            where.append('e.codigo=?'); params.append(etapa_codigo)
        if grupo_codigo:
            where.append('g.codigo=?'); params.append(grupo_codigo)
        where_sql=('WHERE ' + ' AND '.join(where)) if where else ''
        return self.fetchall(
            f'''SELECT c.codigo AS contrato_codigo, e.codigo AS etapa_codigo, g.codigo AS grupo_codigo,
                       ent.codigo AS entregavel_codigo, ent.descricao AS entregavel_descricao,
                       COALESCE(pm.competencia, rm.competencia) AS competencia,
                       COALESCE(pm.valor_previsto_mes,0) AS valor_previsto_mes,
                       COALESCE(rm.valor_realizado_mes,0) AS valor_realizado_mes,
                       (COALESCE(pm.valor_previsto_mes,0)-COALESCE(rm.valor_realizado_mes,0)) AS saldo
                FROM entregaveis ent
                INNER JOIN contratos c ON c.id=ent.contrato_id
                INNER JOIN etapas e ON e.id=ent.etapa_id
                INNER JOIN grupos g ON g.id=ent.grupo_id
                LEFT JOIN planejamento_mensal pm ON pm.entregavel_id=ent.id
                LEFT JOIN realizado_mensal rm ON rm.entregavel_id=ent.id AND rm.competencia=pm.competencia
                {where_sql}
                ORDER BY ABS(COALESCE(pm.valor_previsto_mes,0)-COALESCE(rm.valor_realizado_mes,0)) DESC
                LIMIT 15''',
            tuple(params)
        )

    def dashboard_detail_rows(self, contrato_id=None, etapa_codigo=None, grupo_codigo=None, competencia=None):
        params=[]; where=[]
        if contrato_id:
            where.append('ent.contrato_id=?'); params.append(contrato_id)
        if etapa_codigo:
            where.append('e.codigo=?'); params.append(etapa_codigo)
        if grupo_codigo:
            where.append('g.codigo=?'); params.append(grupo_codigo)
        if competencia:
            where.append('COALESCE(pm.competencia, rm.competencia)=?'); params.append(competencia)
        where_sql=('WHERE ' + ' AND '.join(where)) if where else ''
        return self.fetchall(
            f'''SELECT c.codigo AS contrato_codigo, e.codigo AS etapa_codigo, g.codigo AS grupo_codigo,
                       ent.codigo AS entregavel_codigo, ent.descricao AS entregavel_descricao,
                       COALESCE(pm.competencia, rm.competencia) AS competencia,
                       COALESCE(pm.valor_previsto_mes,0) AS valor_previsto_mes,
                       COALESCE(rm.valor_realizado_mes,0) AS valor_realizado_mes,
                       (COALESCE(pm.valor_previsto_mes,0)-COALESCE(rm.valor_realizado_mes,0)) AS saldo
                FROM entregaveis ent
                INNER JOIN contratos c ON c.id=ent.contrato_id
                INNER JOIN etapas e ON e.id=ent.etapa_id
                INNER JOIN grupos g ON g.id=ent.grupo_id
                LEFT JOIN planejamento_mensal pm ON pm.entregavel_id=ent.id
                LEFT JOIN realizado_mensal rm ON rm.entregavel_id=ent.id AND rm.competencia=pm.competencia
                {where_sql}
                ORDER BY c.codigo, e.codigo, g.codigo, ent.codigo, COALESCE(pm.competencia, rm.competencia)''',
            tuple(params)
        )


    def _competencia_sort_key(self, comp):
        try:
            mm, yyyy = str(comp).split("/")
            return int(yyyy) * 100 + int(mm)
        except Exception:
            return 0

    def _collect_financial_rows(self, contrato_id=None):
        params = (contrato_id,) if contrato_id else ()
        clause_o = "WHERE contrato_id=?" if contrato_id else ""
        clause_f = "WHERE contrato_id=?" if contrato_id else ""
        clause_r = "WHERE r.contrato_id=?" if contrato_id else ""
        clause_c = "WHERE contrato_id=?" if contrato_id else ""
        clause_dp = "WHERE contrato_id=?" if contrato_id else ""
        clause_dr = "WHERE contrato_id=?" if contrato_id else ""

        contratos = self.fetchall(
            f'''SELECT DISTINCT c.id AS contrato_id, c.codigo AS contrato_codigo, c.nome AS contrato_nome
                FROM contratos c
                {"WHERE c.id=?" if contrato_id else ""}
                ORDER BY c.codigo''',
            params
        )
        initial = self.fetchall(
            f'''SELECT contrato_id, competencia, SUM(valor_receita) AS valor
                FROM financeiro_orcamento_oficial
                {clause_o + (" AND tipo_orcamento='inicial'" if clause_o else "WHERE tipo_orcamento='inicial'")}
                GROUP BY contrato_id, competencia''',
            params
        )
        revised = self.fetchall(
            f'''SELECT contrato_id, competencia, SUM(valor_receita) AS valor
                FROM financeiro_orcamento_oficial
                {clause_o + (" AND tipo_orcamento<>'inicial'" if clause_o else "WHERE tipo_orcamento<>'inicial'")}
                GROUP BY contrato_id, competencia''',
            params
        )
        fatur = self.fetchall(
            f'''SELECT contrato_id, competencia, SUM(valor_faturado) AS valor, AVG(impostos_percentual) AS imposto_percentual
                FROM financeiro_faturamento_oficial
                {clause_f}
                GROUP BY contrato_id, competencia''',
            params
        )
        equipe = self.fetchall(
            f'''SELECT r.contrato_id, r.competencia, SUM(r.horas_equipe * COALESCE(p.custo_hora_equipe,0)) AS valor
                FROM produtividade_realizado r
                LEFT JOIN produtividade_parametros p ON p.disciplina=r.disciplina
                {clause_r}
                GROUP BY r.contrato_id, r.competencia''',
            params
        )
        terceiros = self.fetchall(
            f'''SELECT contrato_id, competencia, SUM(custo_total) AS valor
                FROM produtividade_custos
                {clause_c}
                GROUP BY contrato_id, competencia''',
            params
        )
        desp_prev = self.fetchall(
            f'''SELECT contrato_id, competencia, SUM(valor_previsto) AS valor
                FROM despesas_planejamento
                {clause_dp}
                GROUP BY contrato_id, competencia''',
            params
        )
        desp_real = self.fetchall(
            f'''SELECT contrato_id, competencia, SUM(valor_realizado) AS valor
                FROM despesas_realizado
                {clause_dr}
                GROUP BY contrato_id, competencia''',
            params
        )

        contracts_idx = {r["contrato_id"]: {"contrato_codigo": r["contrato_codigo"], "contrato_nome": r["contrato_nome"]} for r in contratos}
        idx = {}

        def touch(cid, comp):
            k = (cid, comp)
            if k not in idx:
                base = contracts_idx.get(cid, {"contrato_codigo": "", "contrato_nome": ""})
                idx[k] = {
                    "contrato_id": cid,
                    "contrato_codigo": base["contrato_codigo"],
                    "contrato_nome": base["contrato_nome"],
                    "competencia": comp,
                    "receita_prevista_inicial": 0.0,
                    "receita_prevista_atual": 0.0,
                    "receita_realizada": 0.0,
                    "custo_equipe_previsto": 0.0,
                    "custo_equipe_realizado": 0.0,
                    "custo_terceiros_previsto": 0.0,
                    "custo_terceiros_realizado": 0.0,
                    "despesas_gerais_previstas": 0.0,
                    "despesas_gerais_realizadas": 0.0,
                    "imposto_percentual": 16.8,
                }
            return idx[k]

        for r in initial:
            item = touch(r["contrato_id"], r["competencia"])
            item["receita_prevista_inicial"] += float(r["valor"] or 0)
        for r in revised:
            item = touch(r["contrato_id"], r["competencia"])
            item["receita_prevista_atual"] += float(r["valor"] or 0)
        for r in fatur:
            item = touch(r["contrato_id"], r["competencia"])
            item["receita_realizada"] += float(r["valor"] or 0)
            item["imposto_percentual"] = float(r["imposto_percentual"] or 16.8)
        for r in equipe:
            item = touch(r["contrato_id"], r["competencia"])
            item["custo_equipe_realizado"] += float(r["valor"] or 0)
        for r in terceiros:
            item = touch(r["contrato_id"], r["competencia"])
            item["custo_terceiros_realizado"] += float(r["valor"] or 0)
        for r in desp_prev:
            item = touch(r["contrato_id"], r["competencia"])
            item["despesas_gerais_previstas"] += float(r["valor"] or 0)
        for r in desp_real:
            item = touch(r["contrato_id"], r["competencia"])
            item["despesas_gerais_realizadas"] += float(r["valor"] or 0)

        rows = []
        for item in idx.values():
            if item["receita_prevista_atual"] == 0:
                item["receita_prevista_atual"] = item["receita_prevista_inicial"]
            item["custo_total_previsto"] = item["custo_equipe_previsto"] + item["custo_terceiros_previsto"] + item["despesas_gerais_previstas"]
            item["custo_total_realizado"] = item["custo_equipe_realizado"] + item["custo_terceiros_realizado"] + item["despesas_gerais_realizadas"]
            item["imposto_previsto"] = item["receita_prevista_atual"] * (item["imposto_percentual"] / 100.0)
            item["imposto_real"] = item["receita_realizada"] * (item["imposto_percentual"] / 100.0)
            item["margem_prevista"] = item["receita_prevista_atual"] - item["custo_total_previsto"] - item["imposto_previsto"]
            item["margem_real"] = item["receita_realizada"] - item["custo_total_realizado"] - item["imposto_real"]
            item["desvio_receita"] = item["receita_realizada"] - item["receita_prevista_atual"]
            item["desvio_custo"] = item["custo_total_realizado"] - item["custo_total_previsto"]
            item["desvio_margem"] = item["margem_real"] - item["margem_prevista"]
            rows.append(item)
        rows.sort(key=lambda r: (r["contrato_codigo"], self._competencia_sort_key(r["competencia"])))
        return rows

    def painel_ano_vigente(self, contrato_id=None, year=None):
        year = int(year or 2026)
        rows = [r for r in self._collect_financial_rows(contrato_id) if str(r["competencia"]).endswith(str(year))]
        acc = {}
        out = []
        for r in rows:
            cid = r["contrato_id"]
            if cid not in acc:
                acc[cid] = {"receita_prevista": 0.0, "receita_realizada": 0.0, "custo_previsto": 0.0, "custo_realizado": 0.0, "margem_prevista": 0.0, "margem_real": 0.0}
            a = acc[cid]
            a["receita_prevista"] += r["receita_prevista_atual"]
            a["receita_realizada"] += r["receita_realizada"]
            a["custo_previsto"] += r["custo_total_previsto"]
            a["custo_realizado"] += r["custo_total_realizado"]
            a["margem_prevista"] += r["margem_prevista"]
            a["margem_real"] += r["margem_real"]
            row = dict(r)
            row["acumulado_receita_prevista"] = a["receita_prevista"]
            row["acumulado_receita_real"] = a["receita_realizada"]
            row["acumulado_custo_previsto"] = a["custo_previsto"]
            row["acumulado_custo_real"] = a["custo_realizado"]
            row["acumulado_margem_prevista"] = a["margem_prevista"]
            row["acumulado_margem_real"] = a["margem_real"]
            out.append(row)
        return out

    def painel_proximos_12_meses(self, contrato_id=None, start_year=2026, start_month=3):
        rows = self._collect_financial_rows(contrato_id)
        start_key = start_year * 100 + start_month
        end_key = (start_year + 1) * 100 + ((start_month + 11 - 1) % 12 + 1) + (((start_month + 11 - 1)//12) * 100 - 100 if False else 0)
        # easier: keep 12 keys list
        keys = []
        y, m = start_year, start_month
        for _ in range(12):
            keys.append(y * 100 + m)
            m += 1
            if m > 12:
                m = 1; y += 1
        return [r for r in rows if self._competencia_sort_key(r["competencia"]) in keys]

    def forecast_anual(self, contrato_id=None, year=None, current_month=3):
        year = int(year or 2026)
        rows = self.painel_ano_vigente(contrato_id, year)
        out = []
        for r in rows:
            mm = int(str(r["competencia"]).split("/")[0])
            row = dict(r)
            if mm <= current_month:
                row["receita_forecast"] = row["receita_realizada"]
                row["custo_forecast"] = row["custo_total_realizado"]
                row["margem_forecast"] = row["margem_real"]
                row["base_forecast"] = "real"
            else:
                row["receita_forecast"] = row["receita_prevista_atual"]
                row["custo_forecast"] = row["custo_total_previsto"]
                row["margem_forecast"] = row["margem_prevista"]
                row["base_forecast"] = "previsto"
            out.append(row)
        acc = {"receita": 0.0, "custo": 0.0, "margem": 0.0}
        for r in out:
            acc["receita"] += r["receita_forecast"]
            acc["custo"] += r["custo_forecast"]
            acc["margem"] += r["margem_forecast"]
            r["acumulado_receita_forecast"] = acc["receita"]
            r["acumulado_custo_forecast"] = acc["custo"]
            r["acumulado_margem_forecast"] = acc["margem"]
        return out

    def cockpit_mensal_oficial(self, competencia, contrato_id=None):
        rows = [r for r in self._collect_financial_rows(contrato_id) if r["competencia"] == competencia]
        resumo = {
            "receita_prevista_inicial": sum(r["receita_prevista_inicial"] for r in rows),
            "receita_prevista_atual": sum(r["receita_prevista_atual"] for r in rows),
            "receita_realizada": sum(r["receita_realizada"] for r in rows),
            "custo_total_previsto": sum(r["custo_total_previsto"] for r in rows),
            "custo_total_realizado": sum(r["custo_total_realizado"] for r in rows),
            "imposto_previsto": sum(r["imposto_previsto"] for r in rows),
            "imposto_real": sum(r["imposto_real"] for r in rows),
            "margem_prevista": sum(r["margem_prevista"] for r in rows),
            "margem_real": sum(r["margem_real"] for r in rows),
            "desvio_receita": sum(r["desvio_receita"] for r in rows),
            "desvio_custo": sum(r["desvio_custo"] for r in rows),
            "desvio_margem": sum(r["desvio_margem"] for r in rows),
        }
        return {"resumo": resumo, "linhas": rows}


    def cockpit_alertas_divergencia(self, competencia, contrato_id=None):
        data = self.cockpit_mensal_oficial(competencia, contrato_id)
        rows = data["linhas"]
        alerts = []
        for r in rows:
            codigo = r["contrato_codigo"] or f"Contrato {r['contrato_id']}"
            if r["receita_realizada"] > 0 and r["custo_total_realizado"] == 0:
                alerts.append({"nivel": "alto", "contrato_codigo": codigo, "competencia": r["competencia"], "mensagem": "Há faturamento realizado sem custo realizado correspondente."})
            if r["receita_prevista_atual"] == 0 and r["receita_realizada"] > 0:
                alerts.append({"nivel": "alto", "contrato_codigo": codigo, "competencia": r["competencia"], "mensagem": "Há faturamento realizado sem orçamento oficial para a competência."})
            if r["custo_total_realizado"] > 0 and r["receita_realizada"] == 0:
                alerts.append({"nivel": "medio", "contrato_codigo": codigo, "competencia": r["competencia"], "mensagem": "Há custos/despesas lançados sem faturamento realizado."})
            if r["despesas_gerais_previstas"] > 0 and r["despesas_gerais_realizadas"] > r["despesas_gerais_previstas"]:
                alerts.append({"nivel": "medio", "contrato_codigo": codigo, "competencia": r["competencia"], "mensagem": "Despesas gerais realizadas acima do previsto."})
            if r["margem_real"] < 0:
                alerts.append({"nivel": "alto", "contrato_codigo": codigo, "competencia": r["competencia"], "mensagem": "Margem real negativa na competência."})
            if abs(r["desvio_receita"]) > max(abs(r["receita_prevista_atual"]) * 0.15, 1):
                alerts.append({"nivel": "medio", "contrato_codigo": codigo, "competencia": r["competencia"], "mensagem": "Desvio de receita acima de 15% do previsto atual."})
        return alerts
