# ⚠️ This repo has been superseded

This MCP has been **unified with the GSC MCP** into a single comprehensive Google SEO suite — including five **cross-platform tools** that connect Analytics 4 with Search Console (GSC↔GA4 journey, opportunity matrix, traffic health check, revenue attribution, full landing page diagnosis).

## 👉 New repo: [`google-seo-mcp-claude-code`](https://github.com/mario-hernandez/google-seo-mcp-claude-code)

The new MCP includes everything this one did (with prefixed `ga4_*` tool names) plus the five cross-platform tools that are only possible with unified auth — connecting your GA4 data with your Search Console rankings in a single tool call.

## Migration

```bash
pipx uninstall ga4-seo-mcp
pipx install git+https://github.com/mario-hernandez/google-seo-mcp-claude-code
```

Update your Claude config from `ga4-seo-mcp` to `google-seo-mcp`.

Tool names are prefixed in the new MCP:
- `anomalies` → `ga4_anomalies`
- `traffic_drops_by_channel` → `ga4_traffic_drops_by_channel`
- `gsc_to_ga4_journey` → `cross_gsc_to_ga4_journey` (now properly cross-platform native)
- (etc.)

This repo is kept for historical reference only and is no longer maintained.
