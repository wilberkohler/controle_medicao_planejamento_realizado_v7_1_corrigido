v7.1 - instruções rápidas

1. Extraia este ZIP em uma NOVA pasta, para evitar misturar arquivos antigos.
2. No terminal, dentro da pasta do projeto, rode:
   python -m pip install -r requirements.txt
   python main.py

Observação:
- Não use 'requirements_v66_corrigido.txt' dentro desta pasta.
- O arquivo correto aqui é somente 'requirements.txt'.

Correções confirmadas:
- repositories/analytics_repository.py contém:
  - home_summary
  - open_competencias
  - pending_items
  - critical_deviations
  - latest_launches
  - global_search
- services/domain_services.py expõe esses métodos no AnalyticsService.
