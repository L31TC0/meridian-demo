# Meridian Brand Partners — Demo Environments

Three self-contained mock datasets for Foundations sales demos. Built around a fictional B2B branding agency (Meridian Brand Partners) selling $75K–$400K engagements to growth-stage B2B tech companies.

Schema mimics HubSpot conventions. Data is deterministically seeded (random seed 42), neutral (no planted narrative hooks), and dated relative to April 13, 2026.

---

## Dataset 1 — Account Brief Generator
**Pitch:** "My AEs get 3 hours back per week before every QBR or renewal call."

**Location:** `01_account_brief/`

| File | Rows | What it is |
|---|---|---|
| `accounts.csv` | 250 | Company records with firmographics, lifecycle stage, owner |
| `contacts.csv` | 600 | People tied to accounts with titles, seniority, engagement |
| `deals.csv` | 180 | Open and closed deals with stage, amount, next step |
| `call_notes.csv` | ~370 | Gong-style 2–3 sentence call summaries |
| `email_threads.csv` | ~470 | Email subject + snippet per touch |

**Demo flow:** "Give me a pre-meeting brief on `{company_name}`." → Claude pulls across all 5 files and produces a one-page brief: deal status, key stakeholders, last 3 touches, open risks, recommended talking points.

**Good test accounts** (ones with plenty of activity): run `ACC-1000` through `ACC-1020` and pick whichever has the most call notes and emails.

---

## Dataset 2 — Pipeline Health Analyzer
**Pitch:** "See exactly where the revenue formula is breaking — by rep, segment, or stage."

**Location:** `02_pipeline_health/`

| File | Rows | What it is |
|---|---|---|
| `reps.csv` | 8 | AEs with tenure, quota, segment |
| `activities.csv` | 5,000 | Calls, emails, meetings across last 180 days |
| `pipeline_snapshots.csv` | 208 | Weekly pipeline state per rep, last 26 weeks |
| `closed_deals.csv` | 120 | Won/lost deals with cycle length and loss reason |

**Demo flow:** "Show me pipeline health across the team." → Claude renders an interactive artifact: rep leaderboard, activity-to-conversion funnel, stage velocity heatmap, loss reason breakdown. Business coach / RevOps leader can drill down per rep.

---

## Dataset 3 — ICP Account Scorer
**Pitch:** "Upload a target list. Get a tiered, scored, enriched account plan with outreach angles — in minutes."

**Location:** `03_icp_scorer/`

| File | Rows | What it is |
|---|---|---|
| `icp_definition.md` | — | Meridian's written ICP (firmographic + behavioral + anti-patterns) |
| `target_accounts.csv` | 300 | Raw prospect list — mixed quality, some great fits, some clear disqualifies |
| `enrichment_data.csv` | 300 | Clay-style layer: intent, job postings, news, exec changes |
| `historical_wins.csv` | 40 | Past closed-won deals as "what good looks like" examples |

**Demo flow:** "Score these 300 accounts against our ICP and enrichment signals, benchmarked against what's worked historically." → Claude produces:
1. A/B/C tier assignment per account with reasoning
2. Top 25 accounts with specific trigger events and recommended outreach angle
3. Pattern callouts (e.g., "12 accounts show a 'new CMO + recent funding' combo — your highest-converting historical trigger")

---

## Conventions across all datasets

- **Dates:** all relative to "today" = 2026-04-13
- **Currency:** USD throughout
- **IDs:** prefixed per entity (`ACC-`, `CON-`, `DEAL-`, `CALL-`, `EML-`, `REP-`, `ACT-`, `SNAP-`, `CLOSED-`, `TGT-`, `WON-`)
- **Owners / reps:** 8 AE names reused across datasets 1 and 2 so narratives can cross-reference
- **Industries, deal sizes, segments:** shared vocabulary so the same "Meridian" identity is coherent across demos

## Regenerating

```bash
python3 generate.py
```

Deterministic — same output every run unless you change the seed.
