v7.0 - correções aplicadas

Correções incluídas:
- services/domain_services.py:
  - expostos no AnalyticsService os métodos usados pela Home e Busca Global:
    - home_summary
    - open_competencias
    - pending_items
    - critical_deviations
    - latest_launches
    - global_search
- requirements.txt:
  - adicionado openpyxl>=3.1

Erro corrigido:
- AttributeError: 'AnalyticsService' object has no attribute 'home_summary'
- ModuleNotFoundError: No module named 'openpyxl'
