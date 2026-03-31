import json, sys
sys.path.insert(0, '.')
from repositories.analytics_repository import AnalyticsRepository
from services.domain_services import AnalyticsService
repo = AnalyticsRepository()
svc = AnalyticsService(repo)
out = {
    "home_summary_callable": isinstance(svc.home_summary(), dict),
    "open_competencias_callable": isinstance(svc.open_competencias(), list),
    "pending_items_callable": isinstance(svc.pending_items(), list),
    "critical_deviations_callable": isinstance(svc.critical_deviations(), list),
    "latest_launches_callable": isinstance(svc.latest_launches(), list),
    "global_search_callable": isinstance(svc.global_search('cont'), list),
}
print(json.dumps(out, ensure_ascii=False))
