
import json, sys
sys.path.insert(0, '.')
from database.db import initialize_database
initialize_database()
from repositories.analytics_repository import AnalyticsRepository
from repositories.expenses_repositories import ExportacaoRepository
from services.expenses_services import ExportacaoService

repo = AnalyticsRepository()
service = ExportacaoService(ExportacaoRepository(), analytics_service=repo)
payload = service.pacote_oficial_dict()
print(json.dumps({
    "alerts_type": isinstance(repo.cockpit_alertas_divergencia("03/2026", None), list),
    "official_keys": sorted(list(payload.keys()))
}, ensure_ascii=False))
