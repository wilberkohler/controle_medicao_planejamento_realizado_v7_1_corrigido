v6.4 - Importação Financeira Híbrida

Testes executados:
1. compilação completa dos arquivos .py -> OK
2. inicialização do banco SQLite -> OK
3. smoke test da importação:
   - criação de contrato CTR-001
   - validação da planilha padrão -> OK
   - importação da planilha padrão -> OK
   - registros criados:
     * financeiro_orcamento_oficial = 2
     * financeiro_faturamento_oficial = 1
     * despesas_planejamento = 1
     * despesas_realizado = 1
     * importacoes_financeiras_log = 1

Observação:
- a interface Qt não foi aberta no ambiente de teste porque a biblioteca visual não está disponível aqui
- a lógica de validação/importação foi testada com sucesso
