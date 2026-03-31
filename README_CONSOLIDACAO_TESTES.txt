VERSÃO DE CONSOLIDAÇÃO v6.0

Correções principais:
- reescrita dos módulos com erro de indentação:
  - ui/views/medicoes_view.py
  - ui/views/etapas_view.py
  - ui/views/grupos_view.py
  - ui/views/entregaveis_view.py
  - ui/views/planejamento_cabecalho_view.py
  - ui/views/planejamento_itens_view.py
  - ui/views/planejamento_mensal_view.py
  - ui/views/realizado_view.py
- reestruturação de ui/main_window.py para incluir imports e páginas de forma consistente
- reescrita de repositories/productivity_repositories.py para consolidar:
  - analytics de produtividade
  - DRE por nível
  - DRE mensal por competência
  - parâmetros de DRE

Testes executados:
1) Compilação Python de todos os arquivos .py
   Resultado: OK (0 erros)

2) Inicialização do banco SQLite
   Resultado: OK

3) Smoke test transacional com criação de dados de exemplo:
   - usuário
   - contrato
   - medição
   - etapa
   - grupo
   - entregável
   - planejamento cabeçalho/item/mensal
   - realizado
   - produtividade (parâmetro/meta/realizado/custo)
   - despesas previstas/realizadas
   Resultado: OK

4) Smoke test de consultas e consolidações:
   - analytics de contratos
   - DRE estrutural
   - DRE mensal
   - exportação contábil
   - exportação anual mensal
   - exportação por categoria
   Resultado: OK

Limitação do ambiente de teste:
- não foi possível testar a abertura real das telas Qt/PySide6 no ambiente atual porque a biblioteca PySide6 não está instalada neste container.
- mesmo assim, as telas foram verificadas por compilação sintática e correção estrutural dos módulos que estavam quebrando.
