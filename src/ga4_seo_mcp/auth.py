"""Authentication for GA4 Admin & Data APIs.

Resolution order:
  1. ADC — `GOOGLE_APPLICATION_CREDENTIALS` env or default `gcloud` ADC file.
     Must include scope `analytics.readonly`.
  2. Service account — `GA4_SERVICE_ACCOUNT_FILE`.
  3. OAuth user flow — `GA4_OAUTH_CLIENT_FILE` (Desktop client JSON).
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.auth import default as google_auth_default
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as SACredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from platformdirs import user_config_dir

from . import __version__

log = logging.getLogger(__name__)

SCOPES_READ = ["https://www.googleapis.com/auth/analytics.readonly"]

_data_client: BetaAnalyticsDataClient | None = None
_admin_client: AnalyticsAdminServiceClient | None = None

USER_AGENT = f"ga4-seo-mcp/{__version__}"


def _config_dir() -> Path:
    p = Path(user_config_dir("ga4-seo-mcp"))
    p.mkdir(parents=True, exist_ok=True)
    return p


def _from_adc() -> Any | None:
    try:
        creds, project = google_auth_default(scopes=SCOPES_READ)
        log.info("Using ADC credentials (project=%s)", project)
        return creds
    except Exception as e:
        log.debug("ADC unavailable: %s", e)
        return None


def _from_service_account() -> Any | None:
    sa_path = os.getenv("GA4_SERVICE_ACCOUNT_FILE")
    if not sa_path or not Path(sa_path).exists():
        return None
    log.info("Using service account at %s", sa_path)
    return SACredentials.from_service_account_file(sa_path, scopes=SCOPES_READ)


def _from_oauth_flow() -> Any | None:
    client_file = os.getenv("GA4_OAUTH_CLIENT_FILE")
    if not client_file or not Path(client_file).exists():
        return None

    token_path = _config_dir() / "token.json"
    creds: Credentials | None = None
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_info(
                json.loads(token_path.read_text()), SCOPES_READ
            )
        except Exception as e:
            log.warning("Could not load cached token, re-authenticating: %s", e)
            creds = None

    if creds and not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = None

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(client_file, SCOPES_READ)
        creds = flow.run_local_server(port=0, open_browser=True)
        token_path.write_text(creds.to_json())
        token_path.chmod(0o600)

    return creds


def _build_creds() -> Any:
    creds = _from_adc() or _from_service_account() or _from_oauth_flow()
    if creds is None:
        raise RuntimeError(
            "No Google credentials found. Set up ADC with `gcloud auth application-default "
            "login --scopes=https://www.googleapis.com/auth/analytics.readonly`, or set "
            "GA4_SERVICE_ACCOUNT_FILE / GA4_OAUTH_CLIENT_FILE."
        )
    return creds


def get_data_client() -> BetaAnalyticsDataClient:
    """Returns a GA4 Data API v1beta client (runReport, runRealtimeReport, etc.)."""
    global _data_client
    if _data_client is None:
        _data_client = BetaAnalyticsDataClient(credentials=_build_creds())
    return _data_client


def get_admin_client() -> AnalyticsAdminServiceClient:
    """Returns a GA4 Admin API v1beta client (accounts, properties, custom dims)."""
    global _admin_client
    if _admin_client is None:
        _admin_client = AnalyticsAdminServiceClient(credentials=_build_creds())
    return _admin_client


def reset_clients() -> None:
    """Force rebuild on next access — used by `reauthenticate` tool."""
    global _data_client, _admin_client
    _data_client = None
    _admin_client = None


def normalize_property(property_id: int | str) -> str:
    """Accepts int, '123', 'properties/123' and returns canonical 'properties/123'."""
    s = str(property_id).strip()
    if s.startswith("properties/"):
        return s
    if s.isdigit():
        return f"properties/{s}"
    raise ValueError(f"Invalid property_id {property_id!r} — expected int or 'properties/<id>'")
