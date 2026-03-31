Testes executados nesta consolidação de usabilidade:
- py_compile em todos os arquivos .py: OK
- initialize_database(): OK
- smoke test AnalyticsRepository.home_summary(): OK
- smoke test open_competencias(): OK
- smoke test pending_items(): OK
- smoke test critical_deviations(): OK
- smoke test latest_launches(): OK
- smoke test global_search('cont'): OK
- smoke test DespesasRealizadoService.validate(): OK

Observação:
- Testes de abertura real das telas Qt não foram executados neste ambiente por indisponibilidade do runtime gráfico/PySide6 no container.
