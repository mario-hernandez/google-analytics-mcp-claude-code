"""MCP server entrypoint — registers all GA4 tools."""
from __future__ import annotations

import logging
import os

from mcp.server.fastmcp import FastMCP

from . import auth as auth_module
from .guardrails import GUARDRAIL_SUFFIX
from .tools import admin as t_admin
from .tools import intelligence as t_intel
from .tools import reporting as t_reporting

logging.basicConfig(
    level=os.getenv("GA4_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

mcp = FastMCP("ga4-seo-mcp")


def _register(fn, *, name: str | None = None):
    """Register a tool, appending the guardrail suffix to its docstring."""
    base_doc = (fn.__doc__ or "").rstrip()
    fn.__doc__ = base_doc + GUARDRAIL_SUFFIX
    return mcp.tool(name=name)(fn)


# Admin / discovery
_register(t_admin.list_properties, name="list_properties")
_register(t_admin.get_property_details, name="get_property_details")

# Reporting basics
_register(t_reporting.search_ga4_schema, name="search_ga4_schema")
_register(t_reporting.list_schema_categories, name="list_schema_categories")
_register(t_reporting.estimate_query_size, name="estimate_query_size")
_register(t_reporting.query_ga4, name="query_ga4")

# Intelligence — diagnostic SEO/marketing
_register(t_intel.anomalies, name="anomalies")
_register(t_intel.traffic_drops_by_channel, name="traffic_drops_by_channel")
_register(t_intel.landing_page_health, name="landing_page_health")
_register(t_intel.conversion_funnel, name="conversion_funnel")
_register(t_intel.cohort_retention, name="cohort_retention")
_register(t_intel.channel_attribution, name="channel_attribution")
_register(t_intel.content_decay, name="content_decay")
_register(t_intel.gsc_to_ga4_journey, name="gsc_to_ga4_journey")


@mcp.tool()
def reauthenticate() -> dict:
    """Force re-authentication on the next API call.

    Useful when ADC credentials have changed or OAuth token has expired and
    cached state is stale. Does not delete files; just resets in-process clients.
    """
    auth_module.reset_clients()
    return {"status": "ok", "message": "Auth clients reset; next call will rebuild credentials."}


@mcp.tool()
def get_capabilities() -> dict:
    """List all tools exposed by this MCP and current auth status. Call FIRST.

    Returns the tool catalog grouped by category, plus a quick check of whether
    credentials are reachable.
    """
    auth_ok = True
    auth_error: str | None = None
    try:
        # Cheap probe — list account summaries (paginates lazily)
        admin = auth_module.get_admin_client()
        next(iter(admin.list_account_summaries()), None)
    except Exception as e:
        auth_ok = False
        auth_error = str(e)[:300]

    return {
        "auth": {"ok": auth_ok, "error": auth_error},
        "categories": {
            "admin": ["list_properties", "get_property_details"],
            "schema": ["search_ga4_schema", "list_schema_categories"],
            "reporting": ["estimate_query_size", "query_ga4"],
            "intelligence": [
                "anomalies",
                "traffic_drops_by_channel",
                "landing_page_health",
                "conversion_funnel",
                "cohort_retention",
                "channel_attribution",
                "content_decay",
                "gsc_to_ga4_journey",
            ],
            "meta": ["reauthenticate", "get_capabilities"],
        },
        "tip": (
            "Workflow: (1) `list_properties` to enumerate. (2) `search_ga4_schema` "
            "with a keyword to find dim/metric names. (3) `estimate_query_size` "
            "before any heavy report. (4) Use `anomalies`, `traffic_drops_by_channel`, "
            "`landing_page_health`, or `gsc_to_ga4_journey` for SEO investigation."
        ),
    }


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
