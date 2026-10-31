from app.core.config import get_settings
from app.main import create_app
from app.services import srs_state


def test_fsrs_has_no_rollout_switch_or_fixed_interval_fallback():
    assert not hasattr(get_settings(), "srs_v2_enabled")
    assert not hasattr(srs_state, "transition")
    assert not hasattr(srs_state, "INTERVAL_DAYS")
    api = create_app().openapi()
    assert "/api/v1/me/srs/session-targets" not in api["paths"]
    assert "/api/v1/me/srs/daily-plans" in api["paths"]
    assert (
        api["components"]["schemas"]["Dashboard"]["properties"]["scheduler_version"]["default"]
        == "fsrs-6.3.2/binary-v2"
    )
