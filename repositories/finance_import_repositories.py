from repositories.base import BaseRepository

class FinanceiroImportRepository(BaseRepository):
    def get_contrato_by_codigo(self, codigo):
        return self.fetchone("SELECT * FROM contratos WHERE codigo=?", (codigo,))

    def upsert_orcamento(self, d):
        row = self.fetchone(
            "SELECT id FROM financeiro_orcamento_oficial WHERE contrato_id=? AND competencia=? AND versao=? AND tipo_orcamento=?",
            (d["contrato_id"], d["competencia"], d["versao"], d["tipo_orcamento"])
        )
        if row:
            self.execute(
                """UPDATE financeiro_orcamento_oficial
                   SET valor_receita=?, centro_custo=?, observacoes=?, fonte=?, updated_at=CURRENT_TIMESTAMP
                   WHERE id=?""",
                (d["valor_receita"], d.get("centro_custo",""), d.get("observacoes",""), d.get("fonte","importacao_planilha"), row["id"])
            )
            return row["id"]
        return self.execute(
            """INSERT INTO financeiro_orcamento_oficial
               (contrato_id, competencia, versao, tipo_orcamento, valor_receita, centro_custo, observacoes, fonte)
               VALUES (?,?,?,?,?,?,?,?)""",
            (d["contrato_id"], d["competencia"], d["versao"], d["tipo_orcamento"], d["valor_receita"], d.get("centro_custo",""), d.get("observacoes",""), d.get("fonte","importacao_planilha"))
        )

    def upsert_faturamento(self, d):
        row = self.fetchone(
            "SELECT id FROM financeiro_faturamento_oficial WHERE contrato_id=? AND competencia=? AND COALESCE(documento_ref,'')=COALESCE(?, '')",
            (d["contrato_id"], d["competencia"], d.get("documento_ref",""))
        )
        if row:
            self.execute(
                """UPDATE financeiro_faturamento_oficial
                   SET valor_faturado=?, impostos_percentual=?, observacoes=?, fonte=?, updated_at=CURRENT_TIMESTAMP
                   WHERE id=?""",
                (d["valor_faturado"], d.get("impostos_percentual",16.8), d.get("observacoes",""), d.get("fonte","importacao_planilha"), row["id"])
            )
            return row["id"]
        return self.execute(
            """INSERT INTO financeiro_faturamento_oficial
               (contrato_id, competencia, documento_ref, valor_faturado, impostos_percentual, observacoes, fonte)
               VALUES (?,?,?,?,?,?,?)""",
            (d["contrato_id"], d["competencia"], d.get("documento_ref",""), d["valor_faturado"], d.get("impostos_percentual",16.8), d.get("observacoes",""), d.get("fonte","importacao_planilha"))
        )

    def create_log(self, arquivo_nome, status, resumo, detalhes_json):
        return self.execute(
            "INSERT INTO importacoes_financeiras_log (arquivo_nome, status, resumo, detalhes_json) VALUES (?,?,?,?)",
            (arquivo_nome, status, resumo, detalhes_json)
        )

    def list_logs(self):
        return self.fetchall("SELECT * FROM importacoes_financeiras_log ORDER BY id DESC LIMIT 30")
