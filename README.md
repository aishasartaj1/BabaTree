# 🌳 BabaTree

**Prayer, made visible.** A gamified prayer-consistency app: every on-time prayer grows a virtual tree, and enough of them (in a future phase) plants a real one in your name.

Built for the Kaggle *AI Agents: Intensive Vibe Coding Capstone* — **Agents for Good** track.

[Video Demo](https://www.youtube.com/watch?v=N0FD6s07qj0)
---

### The Origin

> Someone close to me would nudge me toward prayer — a quiet, consistent push I could always count on. BabaTree bottles that nudge, and gives it to every Muslim who wants to pray on time but sometimes struggles to find the internal push.
>
> This isn't just a habit tracker — it's an attempt to digitise a feeling, the feeling of being nudged by someone who cares, and turn it into something that grows, literally, in the world.

BabaTree pairs two kinds of good in one habit loop: **prayer consistency** (spiritual wellbeing) today, and — once real trees start getting planted — **reforestation** (environmental impact) at scale.

---

## 1. The Problem

Muslims are obligated to pray five daily prayers — Fajr, Dhuhr, Asr, Maghrib, and Isha — each within a specific time window determined by the position of the sun. These windows are not arbitrary; they are fixed, meaningful, and relatively short.

Yet many Muslims struggle with consistency. The reasons are psychological, not theological:

- Modern life is engineered for distraction. Social media and notifications deliver instant dopamine hits.
- Prayer, by contrast, offers a delayed and spiritual reward — one that does not register on the brain's immediate gratification circuits.
- Without an immediate feedback loop, the motivation to pray on time weakens — especially for younger generations raised on instant digital feedback.

BabaTree closes that gap with a two-layer motivation model:

| Layer | Motivation | Trigger | Timescale |
|---|---|---|---|
| 1 | Instant gratification *(the same instant dopamine hit that makes social media addictive, redirected here for good)* | A **virtual tree** grows the moment you tick an on-time prayer | Seconds |
| 2 | Delayed, compounding gratification | A **real tree** planted in your name at a cumulative milestone (Phase 2) — and unlike a one-time delayed reward, ongoing charity (Sadaqa Jariya) keeps compounding indefinitely once it arrives | Permanent |

## 2. What Phase 1 (this repo) actually does

- User enters their name and city once.
- The app fetches the next 7 days of prayer times for that city via a **real MCP server** wrapping the Aladhan API, and caches them for the week.
- Each prayer has a checkbox. Ticking it triggers a two-agent pipeline (Google ADK):
  - **PrayerValidatorAgent** checks whether the tick falls within the prayer's 20-minute on-time window.
  - **TreeGrowthAgent** recomputes the tree's growth stage and checks the Phase 2 milestone.
- Only on-time prayers grow the tree. Late prayers are logged but shown in a different colour (🟢 on-time / 🟡 late / ⬜ not yet prayed).

## 3. Architecture

```
                     ┌─────────────────────────┐
  Login (name, city) │   Streamlit UI (app/)   │  Dashboard (tree, table)
        ─────────────▶                          ◀─────────────
                     └───────────┬─────────────┘
                                 │ once, at login
                                 ▼
                     ┌─────────────────────────┐
                     │  mcp_server/            │  MCP server (FastMCP)
                     │  aladhan_client.py  ────▶│  aladhan_server.py
                     │  (spawns over stdio)     │  → Aladhan REST API
                     └─────────────────────────┘
                                 │ 7 days of prayer times, cached
                                 ▼ in Streamlit session_state
                     ┌─────────────────────────┐
       per checkbox  │  agents/orchestrator.py │  SequentialAgent
       tick   ───────▶  (ADK multi-agent turn) │
                     └───────────┬─────────────┘
                                 │
                  ┌──────────────┴───────────────┐
                  ▼                               ▼
      ┌───────────────────────┐     ┌───────────────────────┐
      │ PrayerValidatorAgent  │ ──▶ │   TreeGrowthAgent      │
      │ (agents/prayer_       │     │ (agents/tree_growth/)  │
      │  validator/)          │     │                        │
      │ tools → core/         │     │ tools → core/          │
      │ prayer_rules.py       │     │ tree_stages.py         │
      └───────────────────────┘     └───────────────────────┘
```

**Design principle:** `core/` holds all the deterministic business logic (the 20-minute window rule, tree-stage thresholds) as plain, framework-free Python. `agents/` is a thin ADK orchestration layer whose *tools* delegate to `core/` — the agents decide *when* to call which tool, but the actual on-time/late arithmetic is never left to LLM reasoning. This keeps the correctness-critical logic deterministic and cheaply testable, while still giving genuine multi-agent orchestration (a `SequentialAgent` handoff between the two agents, sharing session state) for the ADK evaluation criterion.

### Component table

| Component | Technology | Role |
|---|---|---|
| Frontend | Streamlit (`app/`) | Login, dashboard, tree visual, prayer table |
| MCP Server | `mcp` SDK + Aladhan API (`mcp_server/`) | Fetches a city's weekly prayer times — called once at login |
| PrayerValidatorAgent | Google ADK (`agents/prayer_validator/`) | Decides VALID vs LATE for a logged prayer |
| TreeGrowthAgent | Google ADK (`agents/tree_growth/`) | Updates tree stage, checks the Phase 2 milestone |
| Guardrails | `agents/guardrails.py` | Sanitizes name/city input before it reaches any agent or API |
| Session State | Streamlit `session_state` | Caches prayer times, prayer log, tree stage for the browser session |

## 4. Kaggle evaluation coverage

| Key Concept | Covered? | Where |
|---|---|---|
| Agent / Multi-agent (ADK) | ✅ Yes | `agents/orchestrator.py` — `SequentialAgent` composing `PrayerValidatorAgent` + `TreeGrowthAgent`, sharing session state across the handoff |
| MCP Server | ✅ Yes | `mcp_server/aladhan_server.py` — real `FastMCP` server, called once per session by `mcp_server/aladhan_client.py` |
| Security features | ✅ Yes | `agents/guardrails.py` (input sanitization), `.env`/`.gitignore` (no API keys in code), Streamlit `session_state` (session-scoped, no shared/global state) |
| Deployability | ✅ Yes | Runs via `streamlit run app/main.py`; deployable as-is to Streamlit Community Cloud |
| Antigravity | — Skipped | Not applicable to this project |
| Agent Skills (CLI) | — Skipped | Not applicable to this project |

4 of 6 key concepts, meaningfully implemented (not superficial): the validator/growth agent handoff is a real multi-agent flow with tool use, and the MCP server does real work (live-tested against the Aladhan API during development).

## 5. Setup

```bash
git clone <this-repo>
cd BabaTree

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -e ".[dev]"

cp .env.example .env
# edit .env and add your GOOGLE_API_KEY (free at https://aistudio.google.com/apikey)
# Aladhan's API needs no key.

streamlit run app/main.py
```

Then open the local URL Streamlit prints, enter a name and city, and start ticking prayers.

**Note on rate limits:** the free Gemini tier allows 5 requests/minute for `gemini-2.5-flash`. Each prayer tick uses 2 of those (validator + growth agent), so ticking prayers in rapid succession during a demo may hit a `429` — the UI surfaces this as a friendly error rather than crashing.

## 6. Known Phase 1 simplifications

- The Phase 2 "cumulative milestone" is tracked per-browser-session, not truly persisted across weeks — there's no database yet. Phase 2 needs storage before the milestone can be genuinely long-running.
- `trigger_tree_planting` in `agents/tree_growth/tools.py` is a stub — Phase 2 will wire it to a real reforestation partner API (One Tree Planted / Digital Humani).

## 7. Roadmap

**Near-term UX enhancements**:
- **Reduce prayer-log latency** — each tick currently runs 2 sequential Gemini calls (validator + growth agent); explore merging into a single agent turn, streaming partial results, or a faster/cheaper model to make logging feel snappier.
- **Redesign the tree-stage art** — Seed/Sprout/Sapling/Young Tree/Mature Tree currently use plain emoji; replace with custom illustrated stages (in the style of focus/habit apps like Forest) for a more polished, on-brand growth animation between stages.

**Phase 2** — real tree planting: persistent cumulative milestone tracking, reforestation partner API integration, personalised certificate (name + GPS + photo).

**Phase 3** — native mobile app, community trees, optional Sadaqah donation model.

**Production hardening** (deliberately out of scope for this capstone POC, but scaffolded for): once this moves beyond a single-user demo toward something many people rely on daily, it needs:
- **Observability** — structured tracing/logging per agent turn (e.g. Langfuse or Arize Phoenix), so agent decisions are debuggable in production, not just in a terminal.
- **Evals** — golden-case test sets for `PrayerValidatorAgent` and `TreeGrowthAgent` (adhan_time + tick_time → expected status; on-time count → expected stage), run in CI to catch regressions before they reach users.
- **Automated tests** — unit tests against `core/` (fast, no LLM calls) plus integration tests exercising the full MCP + agent flow.
- **CI/CD** — lint + test + eval gates on every change.
- **Persistent storage** — a real database for the cumulative milestone and multi-week history, replacing the current session-only state.

These were consciously deferred to prioritize a working, judged submission within the capstone deadline — not because they're unimportant.
