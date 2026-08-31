from config import settings


def test_frontend_ports_are_allowed_for_browser_requests():
    origins = {origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS}

    assert 'http://localhost:8084' in origins
    assert 'http://127.0.0.1:8084' in origins
