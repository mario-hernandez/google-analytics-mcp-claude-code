<!-- mcp-name: io.github.mario-hernandez/google-analytics-mcp-claude-code -->

# Google Analytics 4 MCP for Claude — diagnostic SEO/marketing intelligence in Python

<p align="center">
  <img src="docs/hero.png" alt="Google Analytics 4 MCP server for Claude — diagnostic SEO/marketing intelligence in Python (anomaly detection, traffic-drop classification, content decay, conversion funnel, GSC→GA4 journey)" width="100%">
</p>

<p align="center">
  <b>Ask Claude <i>"why did organic conversions drop last week?"</i> and get a real diagnosis — anomalies flagged with rolling Z-score, channels classified by cause (volume / engagement / conversion / bounce), funnels with severity-tagged drop-offs, and a journey tool that completes the loop from GSC organic landing pages to GA4 conversions. Not a CSV dump. Not a hallucination. A diagnosis.</b>
</p>

<p align="center">
  <a href="https://github.com/mario-hernandez/google-analytics-mcp-claude-code/stargazers"><img src="https://img.shields.io/github/stars/mario-hernandez/google-analytics-mcp-claude-code?style=flat&color=10b981" alt="Stars"></a>
  <img src="https://img.shields.io/badge/python-3.11+-3776ab?logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/MCP-compatible-7c3aed" alt="MCP compatible">
  <img src="https://img.shields.io/badge/no--telemetry-10b981" alt="No telemetry">
  <img src="https://img.shields.io/badge/read--only-10b981" alt="Read-only">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-10b981" alt="MIT"></a>
</p>

> Stop pasting GA4 reports into ChatGPT. Connect Google Analytics 4 to Claude as native tools and ask the questions that actually matter: which channels are decaying, where is the funnel leaking, which spike yesterday was real signal vs noise, and which organic landing pages from Search Console are converting once users arrive.

## 30-second quickstart

```bash
# 1. Install (Python 3.11+)
pipx install git+https://github.com/mario-hernandez/google-analytics-mcp-claude-code

# 2. Authenticate (one-time, opens browser)
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/analytics.readonly

# 3. Add to Claude Code
claude mcp add ga4-seo-mcp -- $(which ga4-seo-mcp)
```

Then ask Claude: *"List my GA4 properties, then run anomaly detection on sessions for knowingbitcoin.com over the last 30 days."*

Works with **Claude Code**, **Claude Desktop**, **Cursor**, **Windsurf**, and any other MCP-compatible client.

## What you actually get

Five things no other GA4 MCP gives you out of the box:

- 🩺 **Diagnoses, not data dumps** — `traffic_drops_by_channel` doesn't return rows; it returns channels classified by *why* they declined (`volume_loss`, `engagement_decay`, `conversion_decay`, `bounce_surge`). Multiple diagnoses can co-occur on the same channel.
- 🔍 **Anti-hallucination guardrails** — every response is wrapped with `_meta` provenance (source, property, period, fetched_at). Your agent literally cannot make up the numbers when reporting to clients.
- 📐 **Rigorous statistics** — `anomalies` uses leave-one-out rolling Z-score (the day being tested is excluded from its own baseline), avoiding the contamination bug present in some other MCPs.
- 🔗 **The killer feature: `gsc_to_ga4_journey`** — given a path that surfaces in Google Search Console (organic), return what users did after landing on it: sessions, engagement, bounce, conversions, revenue, secondary pages. Closes the loop nobody else closes.
- 🛡️ **Read-only by default** — only requests `analytics.readonly` scope. Safe to point at production.

## Real example — `traffic_drops_by_channel`

Ask Claude: *"Why did sofrologia.com lose conversions this month?"*

```json
[
  {
    "channel": "Organic Search",
    "diagnoses": ["volume_loss", "engagement_decay"],
    "current":  { "sessions": 8420, "engagementRate": 0.51, "bounceRate": 0.49, "conversions": 47 },
    "previous": { "sessions": 11380, "engagementRate": 0.63, "bounceRate": 0.37, "conversions": 89 },
    "session_delta": -2960,
    "session_delta_pct": -0.26
  },
  {
    "channel": "Paid Search",
    "diagnoses": ["conversion_decay"],
    "current":  { "sessions": 1820, "engagementRate": 0.55, "bounceRate": 0.45, "conversions": 8 },
    "previous": { "sessions": 1790, "engagementRate": 0.58, "bounceRate": 0.42, "conversions": 23 },
    "session_delta": 30,
    "session_delta_pct": 0.017
  }
]
```

Claude can now *explain* the drop — Organic Search lost 26% of sessions AND its quality collapsed (engagement down 19%, bounce up 32%); Paid Search held its volume but conversions per session crashed 65% (likely a landing-page or offer issue). Two completely different problems, two different fixes.

## Tools

<details open>
<summary><b>The 8 diagnostic tools</b></summary>

| Tool | What it surfaces |
|------|------------------|
| `anomalies` | Daily spikes/drops via leave-one-out Z-score on any metric, optionally segmented by channel/device/etc. |
| `traffic_drops_by_channel` | Channels in decline, multi-axis classified (volume / engagement / conversion / bounce). |
| `landing_page_health` | Health score (red/amber/green) for top landing pages: bounce, engagement, duration, conversion. |
| `conversion_funnel` | Step-by-step user counts with severity-tagged drop-off (`critical` >70%, `warning` >40%). |
| `cohort_retention` | New vs returning visitor metrics over the period. |
| `channel_attribution` | First-touch vs last-touch comparison; classifies channels as `assister` / `closer` / `balanced`. |
| `content_decay` | Pages with **monotonic decline** across 3 consecutive 30-day windows (filters single-week noise). |
| `gsc_to_ga4_journey` | **Killer**: given an organic landing path (from GSC), returns full GA4 behavior on that page. |

</details>

<details>
<summary><b>The 6 foundation tools</b></summary>

| Tool | What it does |
|------|--------------|
| `list_properties` | Every GA4 property the auth account has access to |
| `get_property_details` | Timezone, currency, industry, service level for one property |
| `search_ga4_schema` | Find dimensions/metrics by keyword (TF-IDF scoring, top-N — avoids dumping 10k tokens) |
| `list_schema_categories` | Cheap discovery of what's available without fetching the full schema |
| `estimate_query_size` | Anti-context-blowup probe — runs `limit=1` to get total `row_count` before committing |
| `query_ga4` | Full Data API report — dimensions, metrics, filters (and/or/not), order_bys, aggregations |

</details>

<details>
<summary><b>Meta</b></summary>

| Tool | What it does |
|------|--------------|
| `get_capabilities` | Tool catalog + auth status (call this first) |
| `reauthenticate` | Reset in-process auth clients |

</details>

## How it pairs with `gsc-seo-mcp`

If you already use the [`gsc-seo-mcp`](https://github.com/mario-hernandez/google-search-console-mcp-claude-code) sister project, the `gsc_to_ga4_journey` tool closes the loop:

1. **In GSC**: `quick_wins` finds queries ranking 4-15 with high impression volume.
2. **Pick a page**. Pass its path to `gsc_to_ga4_journey`.
3. **In GA4**: see whether the organic traffic that *did* arrive engaged, converted, generated revenue.

This is the single workflow no other MCP delivers natively.

## Compared to other Google Analytics MCP servers

| You should use… | If you want… |
|-----------------|--------------|
| [**`googleanalytics/google-analytics-mcp`**](https://github.com/googleanalytics/google-analytics-mcp) (official, Python) | The most polished raw API bridge maintained by Google. Pick if you only need data fetching and you'll build your own diagnostic logic on top. Cobertura wider on Admin API surface (annotations, ads links). |
| [**`surendranb/google-analytics-mcp`**](https://github.com/surendranb/google-analytics-mcp) (Python, 200+ stars) | A clever schema-discovery + row-count-probe wrapper for `runReport`. Pick if you only need raw data with anti-context-blowup protection. Single-property only. |
| [**`saurabhsharma2u/search-console-mcp`**](https://github.com/saurabhsharma2u/search-console-mcp) (TypeScript, 100+ stars) | The biggest tool surface (90+ tools across GSC + GA4 + Bing). Pick if you need Bing Webmaster integration or you live in TypeScript. |
| **This MCP** | **Diagnostic GA4 logic in Python with anti-hallucination guardrails, rigorous statistics (rolling Z with leave-one-out, real funnel via runFunnelReport, true Pearson correlation in pagespeed), multi-property dynamic, and the unique `gsc_to_ga4_journey` cross-source tool.** Pick if your agent reports to clients and you can't afford a hallucinated CTR/conversion-rate. |

This MCP started as a security-audited synthesis of the four above — credit at the bottom of this README. The diagnostic ideas are inspired by Saurabh's TypeScript implementation but improved (his Z-score baseline contamination, fake funnel, and unranked pagespeed correlation are all fixed here).

## Authentication

### Default — Application Default Credentials (recommended)

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/analytics.readonly
```

The authenticated Google account must have at least **Viewer** access in GA4 → Admin → Property → Property Access Management for each property you want to query.

<details>
<summary><b>Advanced auth methods</b></summary>

### Service account (headless servers)

```bash
export GA4_SERVICE_ACCOUNT_FILE=/path/to/sa-key.json
```

The service account email must be added as a user in GA4 Admin for each property.

### OAuth user flow (interactive)

Create a Desktop OAuth client in your Google Cloud project, then:

```bash
export GA4_OAUTH_CLIENT_FILE=/path/to/client_secret.json
```

The first call opens a browser; the token is cached at `~/Library/Application Support/ga4-seo-mcp/token.json` (macOS) or the equivalent `XDG_CONFIG_HOME` location.

</details>

## Configure with your client

<details open>
<summary><b>Claude Code</b></summary>

```bash
claude mcp add ga4-seo-mcp -- $(which ga4-seo-mcp)
```

Or manually in `~/.claude.json`:

```json
{
  "mcpServers": {
    "ga4-seo-mcp": {
      "type": "stdio",
      "command": "ga4-seo-mcp"
    }
  }
}
```

</details>

<details>
<summary><b>Claude Desktop</b></summary>

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ga4-seo-mcp": {
      "command": "ga4-seo-mcp"
    }
  }
}
```

</details>

<details>
<summary><b>Cursor / Windsurf / Zed</b></summary>

```json
{
  "ga4-seo-mcp": { "command": "ga4-seo-mcp" }
}
```

</details>

## Environment variables

| Var | Default | Purpose |
|-----|---------|---------|
| `GOOGLE_APPLICATION_CREDENTIALS` | gcloud ADC default | ADC file path |
| `GA4_SERVICE_ACCOUNT_FILE` | — | Service account key path |
| `GA4_OAUTH_CLIENT_FILE` | — | Desktop OAuth client JSON |
| `GA4_LOG_LEVEL` | `INFO` | Python log level |

## Design principles

- **Read-only.** Only `analytics.readonly` scope is requested. No write APIs are exposed.
- **Provenance always included.** Every response is wrapped in `{"data": ..., "_meta": {source, property, period, fetched_at}}`. The LLM can cite where each number came from — and you can audit later.
- **Diagnoses, not data dumps.** Intelligence tools classify findings (`volume_loss` vs `engagement_decay`, `assister` vs `closer`) rather than handing the LLM thousands of rows to summarize.
- **Anti-context-blowup.** `estimate_query_size` and `search_ga4_schema` exist so the LLM can size queries cheaply before committing to fetches that would overflow context.
- **Multi-property by parameter, not by env.** Pass any `property_id` to any tool — no need to restart with a different env var.
- **Statistical rigor.** Leave-one-out Z-score baselines, monotonic-window decay detection, true Pearson correlation in pagespeed. No ad-hoc thresholds without justification.

## Credits & inspiration

Independent implementation that synthesizes the strongest ideas from four open-source projects, all of which were security-audited and found clean before being studied:

- [`googleanalytics/google-analytics-mcp`](https://github.com/googleanalytics/google-analytics-mcp) — official Google MCP. Inspired the proto-serialized examples in tool docstrings and the `inputSchema` sanitization for Claude Desktop compatibility.
- [`surendranb/google-analytics-mcp`](https://github.com/surendranb/google-analytics-mcp) — schema cache, TF-IDF keyword search, row-count probe before fetch.
- [`saurabhsharma2u/search-console-mcp`](https://github.com/saurabhsharma2u/search-console-mcp) — the diagnostic philosophy (anomalies, drop attribution, funnel, opportunity matrix). His algorithms are reimplemented in Python with the statistical rigor improvements documented above.
- [`gomarble-ai/google-analytics-mcp-server`](https://github.com/gomarble-ai/google-analytics-mcp-server) — `runReport` docstring patterns with valid metrics/dimensions hints.

If those projects fit your workflow better, use them — they're solid in their own right.

## Security notes

- **No telemetry.** Zero outbound traffic to anything other than `googleapis.com` / `accounts.google.com` / `oauth2.googleapis.com`.
- **No credentials in the repo.** `.gitignore` excludes `*.json` by default.
- **Read-only OAuth scope** — only `analytics.readonly`.

## License

MIT — see [LICENSE](LICENSE).
