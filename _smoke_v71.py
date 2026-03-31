import json, sys
sys.path.insert(0, '.')
from repositories.analytics_repository import AnalyticsRepository
from services.domain_services import AnalyticsService
repo = AnalyticsRepository()
svc = AnalyticsService(repo)
print(json.dumps({
    "repo_has_home_summary": hasattr(repo, "home_summary"),
    "repo_has_open_competencias": hasattr(repo, "open_competencias"),
    "repo_has_pending_items": hasattr(repo, "pending_items"),
    "repo_has_critical_deviations": hasattr(repo, "critical_deviations"),
    "repo_has_latest_launches": hasattr(repo, "latest_launches"),
    "repo_has_global_search": hasattr(repo, "global_search"),
    "svc_has_home_summary": hasattr(svc, "home_summary"),
    "svc_has_global_search": hasattr(svc, "global_search"),
}, ensure_ascii=False))
