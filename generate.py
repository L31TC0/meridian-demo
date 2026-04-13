"""
Meridian Brand Partners — mock dataset generator
Produces realistic HubSpot-style CSVs for three demo environments:
  1. Account Brief Generator
  2. Pipeline Health Analyzer
  3. ICP Account Scorer

Deterministic (seeded). Data is neutral — no planted narrative hooks.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)
BASE = Path("/home/claude/meridian")
TODAY = datetime(2026, 4, 13)

# ---------- shared vocab ----------
INDUSTRIES = [
    "B2B SaaS", "FinTech", "HealthTech", "PropTech", "Logistics",
    "Cybersecurity", "MarTech", "HR Tech", "Legal Tech", "E-commerce Platform",
    "Dev Tools", "Data & Analytics", "Insurance Tech", "EdTech"
]
SIZE_BANDS = ["11-50", "51-200", "201-500", "501-1000", "1001-5000"]
LIFECYCLE_STAGES = ["lead", "marketing qualified lead", "sales qualified lead",
                    "opportunity", "customer", "evangelist"]
DEAL_STAGES = ["Discovery", "Scoping", "Proposal Sent", "Negotiation",
               "Closed Won", "Closed Lost"]
LOSS_REASONS = ["Budget", "Timing", "Went with competitor", "No decision",
                "Internal resource", "Lost to in-house team", "Unresponsive"]
CALL_OUTCOMES = ["Connected", "Voicemail", "No answer", "Busy", "Gatekeeper"]

FIRST_NAMES = ["Aisha", "Marcus", "Priya", "Daniel", "Sofia", "Ethan", "Yuki",
               "Jamal", "Chloe", "Ravi", "Maya", "Owen", "Leila", "Hiro",
               "Nadia", "Felix", "Zara", "Theo", "Iris", "Kai", "Amara",
               "Victor", "Noor", "Silas", "Elena", "Darius", "Anya", "Cyrus"]
LAST_NAMES = ["Chen", "Okonkwo", "Patel", "Ferreira", "Nakamura", "Dubois",
              "Reyes", "Hassan", "Walsh", "Kowalski", "Bergman", "Abadi",
              "Jensen", "Romano", "Singh", "Johansson", "Kapoor", "O'Brien",
              "Petrov", "Tanaka", "Mbeki", "Costa", "Varga", "Lindqvist"]
COMPANY_STEMS = ["Northwind", "Brightlane", "Kestrel", "Parallax", "Vantage",
                 "Cinder", "Foxglove", "Harbor", "Ironwood", "Luma", "Monarch",
                 "Nimbus", "Oakline", "Pioneer", "Quill", "Redshore",
                 "Silverleaf", "Terrace", "Umbra", "Verdant", "Willowrun",
                 "Axiom", "Beacon", "Covalent", "Drift", "Ember", "Flint",
                 "Garnet", "Helix", "Indigo", "Juniper", "Kiln", "Lattice",
                 "Meridian Peak", "Norton", "Opal", "Plume", "Quest",
                 "Riverbend", "Solstice", "Thornbury", "Upland", "Valence"]
COMPANY_SUFFIX = ["", " Labs", " Systems", " Technologies", " AI", " Digital",
                  " Platforms", " Networks", " Analytics", " Cloud", " Group",
                  " Software", " Health", " Logistics", " Financial"]
TITLES = ["CMO", "VP Marketing", "Head of Marketing", "Director of Marketing",
          "Head of Brand", "Director of Brand", "CEO", "Founder",
          "Co-Founder", "VP Growth", "Head of Growth", "COO",
          "Director of Demand Gen", "Head of Content", "CRO"]
SENIORITY_MAP = {
    "CEO": "C-Suite", "Founder": "C-Suite", "Co-Founder": "C-Suite",
    "CMO": "C-Suite", "COO": "C-Suite", "CRO": "C-Suite",
    "VP Marketing": "VP", "VP Growth": "VP",
    "Head of Marketing": "Director", "Head of Brand": "Director",
    "Head of Growth": "Director", "Head of Content": "Director",
    "Director of Marketing": "Director", "Director of Brand": "Director",
    "Director of Demand Gen": "Director",
}

AE_NAMES = ["Ava Morgenstern", "Theo Blackwood", "Priya Raman",
            "Samuel Okafor", "Clara Voss", "Dmitri Lazarev",
            "Naomi Fielding", "Jordan Ellis"]
SEGMENTS = ["SMB Tech", "Mid-Market Tech", "PE-Backed"]

# ---------- helpers ----------
def rand_date(start_days_ago, end_days_ago=0):
    delta = random.randint(end_days_ago, start_days_ago)
    return TODAY - timedelta(days=delta)

def fmt(d):
    return d.strftime("%Y-%m-%d")

def fmt_ts(d):
    return d.strftime("%Y-%m-%d %H:%M:%S")

def company_name():
    stem = random.choice(COMPANY_STEMS)
    suf = random.choice(COMPANY_SUFFIX)
    return f"{stem}{suf}".strip()

def person_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def email_from(name, domain):
    first, last = name.split(" ", 1)
    return f"{first.lower()}.{last.lower().replace(' ', '').replace(chr(39), '')}@{domain}"

def domain_from(company):
    base = company.lower().replace(" ", "").replace("'", "")
    tld = random.choice([".com", ".io", ".co", ".ai"])
    return base + tld

def write_csv(path, headers, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  wrote {path}  ({len(rows)} rows)")

# =========================================================
# DATASET 1 — Account Brief Generator
# =========================================================
print("\n[1/3] Account Brief Generator")

accounts = []
used_names = set()
while len(accounts) < 250:
    name = company_name()
    if name in used_names:
        continue
    used_names.add(name)
    accounts.append({
        "account_id": f"ACC-{1000 + len(accounts)}",
        "company_name": name,
        "domain": domain_from(name),
        "industry": random.choice(INDUSTRIES),
        "employee_count_band": random.choice(SIZE_BANDS),
        "estimated_arr_usd": random.choice([5_000_000, 10_000_000, 25_000_000,
                                            50_000_000, 100_000_000, 250_000_000]),
        "hq_city": random.choice(["Toronto", "New York", "San Francisco",
                                  "Austin", "Chicago", "Boston", "Vancouver",
                                  "Denver", "Atlanta", "Seattle"]),
        "lifecycle_stage": random.choices(
            LIFECYCLE_STAGES,
            weights=[25, 20, 18, 15, 18, 4]
        )[0],
        "hubspot_owner": random.choice(AE_NAMES),
        "first_touch_date": fmt(rand_date(540, 60)),
        "last_activity_date": fmt(rand_date(120, 1)),
        "lead_source": random.choice(["Inbound - Website", "Outbound - Email",
                                      "Outbound - LinkedIn", "Referral",
                                      "Event", "Partner"]),
    })

write_csv(
    BASE / "01_account_brief" / "accounts.csv",
    list(accounts[0].keys()),
    [list(a.values()) for a in accounts],
)

# contacts (2-4 per account on average, 600 total)
contacts = []
for _ in range(600):
    acc = random.choice(accounts)
    name = person_name()
    title = random.choice(TITLES)
    contacts.append({
        "contact_id": f"CON-{5000 + len(contacts)}",
        "account_id": acc["account_id"],
        "full_name": name,
        "title": title,
        "seniority": SENIORITY_MAP.get(title, "Manager"),
        "email": email_from(name, acc["domain"]),
        "email_opens_last_90d": random.randint(0, 28),
        "email_clicks_last_90d": random.randint(0, 9),
        "last_meeting_date": fmt(rand_date(240, 1)) if random.random() < 0.55 else "",
    })
write_csv(
    BASE / "01_account_brief" / "contacts.csv",
    list(contacts[0].keys()),
    [list(c.values()) for c in contacts],
)

# deals (180)
deals = []
for i in range(180):
    acc = random.choice(accounts)
    stage = random.choices(
        DEAL_STAGES,
        weights=[22, 18, 20, 15, 15, 10]
    )[0]
    amount = random.choice([75_000, 120_000, 180_000, 240_000, 320_000, 400_000])
    created = rand_date(300, 30)
    close_offset = random.randint(30, 120)
    deals.append({
        "deal_id": f"DEAL-{2000 + i}",
        "account_id": acc["account_id"],
        "deal_name": f"{acc['company_name']} - "
                     f"{random.choice(['Brand System', 'Website Rebuild', 'Campaign', 'Rebrand', 'Content Engine'])}",
        "stage": stage,
        "amount_usd": amount,
        "created_date": fmt(created),
        "expected_close_date": fmt(created + timedelta(days=close_offset)),
        "deal_owner": acc["hubspot_owner"],
        "next_step": random.choice([
            "Awaiting proposal feedback",
            "Follow-up call scheduled",
            "Intro to procurement pending",
            "Reviewing scope with exec sponsor",
            "Contract redlines in progress",
            "Waiting on budget confirmation",
            "Re-engaging after summer pause",
        ]),
        "loss_reason": random.choice(LOSS_REASONS) if stage == "Closed Lost" else "",
    })
write_csv(
    BASE / "01_account_brief" / "deals.csv",
    list(deals[0].keys()),
    [list(d.values()) for d in deals],
)

# call notes (400) — Gong-style summaries, 2-3 sentences
CALL_TEMPLATES = [
    "Kickoff call with {contact} ({title}). Discussed current brand perception issues and timeline pressure from upcoming {event}. {contact} flagged that the board wants a refreshed identity before Q{q}. Next step: send scoping doc.",
    "Working session with {contact}. Reviewed three moodboard directions — they're leaning toward Direction B but want to socialize internally. Budget not yet confirmed but {contact} estimates {range}. Follow-up in two weeks.",
    "Discovery with {contact} and one additional stakeholder. Current agency relationship is ending; they've had two failed rebrand attempts. Pain points: inconsistent application across channels, no design system. Strong fit signals.",
    "Check-in call. {contact} is under hiring freeze and the project is on hold until Q{q}. Suggested we stay in touch monthly. Not dead but paused.",
    "Proposal review. {contact} pushed back on timeline (wants 8 weeks instead of 12) and asked about phased pricing. Competitor mentioned: one other agency in final consideration. Decision expected in ~10 days.",
    "Intro call. Referred by an existing client. {contact} is newly in seat (6 weeks) and evaluating vendors as part of a broader GTM overhaul. Wants to see case studies in their vertical.",
    "Quarterly check-in with {contact}. Current engagement going well — brand system rollout is 70% complete. Opportunity to expand into campaign work discussed.",
    "Objection call. {contact} cited internal resource as the hesitation — their design lead thinks they can do it in-house. Agreed to a diagnostic workshop to compare approaches.",
    "Scoping conversation. Walked through deliverables and dependencies. {contact} asked about our process for cross-team alignment. Their marketing and product teams are currently siloed.",
    "Negotiation call. Price is acceptable but payment terms are a sticking point — they want net-60 and we offered net-30. Legal is involved. Close probability now 60%.",
]

call_notes = []
active_accounts = [a for a in accounts
                   if a["lifecycle_stage"] in ("opportunity", "sales qualified lead", "customer")]
for i in range(400):
    acc = random.choice(active_accounts or accounts)
    acc_contacts = [c for c in contacts if c["account_id"] == acc["account_id"]]
    if not acc_contacts:
        continue
    contact = random.choice(acc_contacts)
    template = random.choice(CALL_TEMPLATES)
    summary = template.format(
        contact=contact["full_name"].split()[0],
        title=contact["title"],
        event=random.choice(["investor update", "customer summit",
                             "product launch", "sales kickoff"]),
        q=random.choice([1, 2, 3, 4]),
        range=random.choice(["$150K-200K", "$200K-300K", "$100K-150K", "$300K-400K"]),
    )
    call_notes.append({
        "call_id": f"CALL-{7000 + i}",
        "account_id": acc["account_id"],
        "contact_id": contact["contact_id"],
        "call_date": fmt_ts(rand_date(180, 1)),
        "duration_minutes": random.randint(18, 55),
        "attendees": f"{contact['full_name']}, {acc['hubspot_owner']}"
                     + (f", {person_name()}" if random.random() < 0.3 else ""),
        "recorded_by": "Gong",
        "summary": summary,
    })
write_csv(
    BASE / "01_account_brief" / "call_notes.csv",
    list(call_notes[0].keys()),
    [list(c.values()) for c in call_notes],
)

# email threads (500)
EMAIL_SUBJECTS = [
    "Following up on our conversation",
    "Proposal - {company}",
    "Quick question re: timeline",
    "Case study you asked about",
    "Re: scoping doc",
    "Next steps",
    "Intro - {company} x Meridian",
    "Checking in",
    "Revised SOW attached",
    "Board deck feedback",
]
EMAIL_SNIPPETS = [
    "Hi {first} — circling back on the proposal we sent last week. Happy to walk through any questions with your team...",
    "{first}, attaching the revised scope reflecting the phased approach we discussed. Let me know if the pricing structure works...",
    "Thanks for the intro call yesterday. As promised, here are two case studies from similar-stage companies in your space...",
    "Following up — I know you mentioned the board review was this week. Any updates on the decision timeline?",
    "{first}, the design team has a couple of clarifying questions before we finalize the creative brief. Can we grab 15 min Thursday?",
    "Wanted to share something relevant — one of our other clients just launched their rebrand and the early metrics are strong...",
    "Got it, understood on the pause. I'll check back in early {month}. In the meantime if anything shifts, just ping me.",
    "Per your note on procurement — we've worked with their process before and have a template MSA ready to share...",
]

email_threads = []
for i in range(500):
    deal = random.choice(deals)
    acc = next(a for a in accounts if a["account_id"] == deal["account_id"])
    acc_contacts = [c for c in contacts if c["account_id"] == acc["account_id"]]
    if not acc_contacts:
        continue
    contact = random.choice(acc_contacts)
    subj = random.choice(EMAIL_SUBJECTS).format(company=acc["company_name"])
    snippet = random.choice(EMAIL_SNIPPETS).format(
        first=contact["full_name"].split()[0],
        month=random.choice(["January", "March", "June", "September"])
    )
    email_threads.append({
        "email_id": f"EML-{9000 + i}",
        "deal_id": deal["deal_id"],
        "account_id": acc["account_id"],
        "from": "meridian_ae",
        "to": contact["email"],
        "subject": subj,
        "sent_date": fmt_ts(rand_date(200, 1)),
        "snippet": snippet,
        "direction": random.choices(["outbound", "inbound"], weights=[70, 30])[0],
    })
write_csv(
    BASE / "01_account_brief" / "email_threads.csv",
    list(email_threads[0].keys()),
    [list(e.values()) for e in email_threads],
)

# =========================================================
# DATASET 2 — Pipeline Health Analyzer
# =========================================================
print("\n[2/3] Pipeline Health Analyzer")

reps = []
for i, name in enumerate(AE_NAMES):
    reps.append({
        "rep_id": f"REP-{100 + i}",
        "rep_name": name,
        "tenure_months": random.randint(4, 48),
        "annual_quota_usd": random.choice([800_000, 1_000_000, 1_200_000, 1_500_000]),
        "segment": random.choice(SEGMENTS),
        "manager": random.choice(["Elena Carter", "Rohan Mehta"]),
    })
write_csv(
    BASE / "02_pipeline_health" / "reps.csv",
    list(reps[0].keys()),
    [list(r.values()) for r in reps],
)

# activities: 5000 records across reps, last 180 days
ACTIVITY_TYPES = ["Call", "Email", "LinkedIn", "Meeting", "Demo"]
activities = []
for i in range(5000):
    rep = random.choice(reps)
    atype = random.choices(
        ACTIVITY_TYPES,
        weights=[35, 40, 10, 10, 5]
    )[0]
    outcome = (random.choice(CALL_OUTCOMES) if atype == "Call"
               else ("Sent" if atype in ("Email", "LinkedIn")
                     else "Completed"))
    duration = (random.randint(2, 12) if atype == "Call"
                else random.randint(25, 60) if atype in ("Meeting", "Demo")
                else 0)
    activities.append({
        "activity_id": f"ACT-{20000 + i}",
        "rep_id": rep["rep_id"],
        "rep_name": rep["rep_name"],
        "activity_type": atype,
        "activity_date": fmt_ts(rand_date(180, 0)),
        "outcome": outcome,
        "duration_minutes": duration,
        "account_id": f"ACC-{random.randint(1000, 1249)}",
    })
write_csv(
    BASE / "02_pipeline_health" / "activities.csv",
    list(activities[0].keys()),
    [list(a.values()) for a in activities],
)

# weekly pipeline snapshots: ~26 weeks x 8 reps = ~208 rows
snapshots = []
snap_id = 0
for week in range(26, 0, -1):
    snap_date = TODAY - timedelta(weeks=week)
    for rep in reps:
        open_deals = random.randint(6, 22)
        snapshots.append({
            "snapshot_id": f"SNAP-{30000 + snap_id}",
            "snapshot_date": fmt(snap_date),
            "rep_id": rep["rep_id"],
            "rep_name": rep["rep_name"],
            "open_deals_count": open_deals,
            "pipeline_value_usd": open_deals * random.randint(140_000, 260_000),
            "deals_in_discovery": random.randint(1, 8),
            "deals_in_scoping": random.randint(1, 6),
            "deals_in_proposal": random.randint(0, 5),
            "deals_in_negotiation": random.randint(0, 4),
            "avg_days_in_stage": random.randint(14, 55),
        })
        snap_id += 1
write_csv(
    BASE / "02_pipeline_health" / "pipeline_snapshots.csv",
    list(snapshots[0].keys()),
    [list(s.values()) for s in snapshots],
)

# closed deals (120)
closed = []
for i in range(120):
    rep = random.choice(reps)
    won = random.random() < 0.35
    amount = random.choice([75_000, 120_000, 180_000, 240_000, 320_000, 400_000])
    cycle = random.randint(35, 140)
    closed.append({
        "deal_id": f"CLOSED-{40000 + i}",
        "rep_id": rep["rep_id"],
        "rep_name": rep["rep_name"],
        "segment": rep["segment"],
        "amount_usd": amount,
        "outcome": "Won" if won else "Lost",
        "cycle_length_days": cycle,
        "close_date": fmt(rand_date(240, 1)),
        "loss_reason": "" if won else random.choice(LOSS_REASONS),
        "industry": random.choice(INDUSTRIES),
    })
write_csv(
    BASE / "02_pipeline_health" / "closed_deals.csv",
    list(closed[0].keys()),
    [list(c.values()) for c in closed],
)

# =========================================================
# DATASET 3 — ICP Account Scorer
# =========================================================
print("\n[3/3] ICP Account Scorer")

# ICP definition markdown
icp_md = """# Meridian Brand Partners — Ideal Customer Profile

## Firmographic criteria

**Company size:** 50–750 employees
**Revenue:** $10M–$150M ARR
**HQ:** North America (Canada, US) preferred; UK/EU acceptable
**Industries (strong fit):**
- B2B SaaS (especially vertical SaaS)
- FinTech, HealthTech, PropTech
- Dev tools & data platforms
- PE-backed tech portfolio companies

**Industries (weak fit):**
- Pure consumer brands (B2C)
- Heavy manufacturing, oil & gas
- Government / public sector

## Behavioral & intent signals (positive)

- Recent funding round (Series B or later within last 18 months)
- Recent hire: CMO, Head of Brand, or VP Marketing in last 6 months
- Website/brand visibly outdated relative to stage
- Expanding into a new market or launching a new product line
- Recent acquisition or merger (rebrand opportunity)
- Active job postings for brand, design, or marketing leadership
- Board-level pressure around positioning or category creation

## Anti-patterns (disqualify or deprioritize)

- Has an in-house creative team of 8+
- Just completed a rebrand within last 12 months
- Revenue under $5M (usually can't afford our ACV)
- Agency-of-record relationship with a top-10 global firm
- Pre-seed or seed-stage with no confirmed Series A

## Ideal buyer personas

- CMO (primary economic buyer)
- VP Marketing / Head of Brand (primary champion)
- CEO/Founder (in companies under 200 employees)
- Head of Product Marketing (secondary influencer)

## Deal size expectations

- SMB tier (50–200 employees): $75K–$150K
- Mid-market (201–750 employees): $150K–$400K
- Strategic / PE-backed: $250K–$500K+
"""
(BASE / "03_icp_scorer" / "icp_definition.md").write_text(icp_md)
print(f"  wrote {BASE / '03_icp_scorer' / 'icp_definition.md'}")

# target accounts (300) — raw prospect list, mixed quality
TECH_STACKS = [
    "HubSpot, Webflow, Notion",
    "Salesforce, Marketo, WordPress",
    "HubSpot, Figma, Intercom",
    "Pipedrive, Mailchimp, Squarespace",
    "Salesforce, Pardot, Drupal",
    "HubSpot, Webflow, Segment, Gong",
    "Zoho, Sendinblue, WordPress",
    "Salesforce, Marketo, Contentful, Figma",
]
FUNDING_STAGES = ["Bootstrapped", "Seed", "Series A", "Series B", "Series C",
                  "Series D+", "PE-Backed", "Public"]

targets = []
for i in range(300):
    name = company_name()
    emp_count = random.choice([
        random.randint(10, 49),
        random.randint(50, 200),
        random.randint(201, 750),
        random.randint(751, 2000),
    ])
    revenue = random.choice([
        random.randint(1, 4) * 1_000_000,
        random.randint(10, 40) * 1_000_000,
        random.randint(50, 150) * 1_000_000,
        random.randint(200, 500) * 1_000_000,
    ])
    funding = random.choice(FUNDING_STAGES)
    funding_recent = random.random() < 0.35
    recent_cmo_hire = random.random() < 0.15
    recent_rebrand = random.random() < 0.12
    in_house_team = random.random() < 0.20

    targets.append({
        "target_id": f"TGT-{50000 + i}",
        "company_name": name,
        "website": f"https://{domain_from(name)}",
        "industry": random.choice(INDUSTRIES + ["Consumer Goods",
                                                 "Manufacturing",
                                                 "Government"]),
        "employee_count": emp_count,
        "estimated_revenue_usd": revenue,
        "hq_country": random.choices(
            ["USA", "Canada", "UK", "Germany", "Australia"],
            weights=[55, 20, 10, 8, 7]
        )[0],
        "funding_stage": funding,
        "last_funding_date": fmt(rand_date(900, 30)) if funding not in ("Bootstrapped", "Public") else "",
        "recent_funding_18mo": "Yes" if funding_recent else "No",
        "recent_leadership_hire_marketing": "Yes" if recent_cmo_hire else "No",
        "recent_rebrand_12mo": "Yes" if recent_rebrand else "No",
        "in_house_creative_team_size": random.randint(8, 20) if in_house_team else random.randint(0, 5),
        "tech_stack": random.choice(TECH_STACKS),
        "linkedin_followers": random.randint(800, 85000),
    })
write_csv(
    BASE / "03_icp_scorer" / "target_accounts.csv",
    list(targets[0].keys()),
    [list(t.values()) for t in targets],
)

# enrichment data (Clay-style) — one row per target, additional signals
INTENT_TOPICS = [
    "brand strategy", "rebrand", "website redesign", "category creation",
    "positioning", "go-to-market", "design system", "creative agency",
    "", "", ""  # often empty
]
enrichment = []
for t in targets:
    enrichment.append({
        "target_id": t["target_id"],
        "company_name": t["company_name"],
        "intent_topic_spike": random.choice(INTENT_TOPICS),
        "intent_score_0_100": random.randint(0, 100),
        "job_postings_marketing_design": random.randint(0, 12),
        "recent_news_headline": random.choice([
            f"{t['company_name']} raises new round to expand product line",
            f"{t['company_name']} names new Chief Marketing Officer",
            f"{t['company_name']} announces acquisition of regional competitor",
            f"{t['company_name']} launches new enterprise tier",
            "",
            "",
        ]),
        "exec_change_last_90d": random.choices(["Yes", "No"], weights=[25, 75])[0],
        "g2_reviews_count": random.randint(0, 450),
        "employees_added_last_90d": random.randint(-15, 80),
    })
write_csv(
    BASE / "03_icp_scorer" / "enrichment_data.csv",
    list(enrichment[0].keys()),
    [list(e.values()) for e in enrichment],
)

# historical wins (40) — for "what good looks like" reference
wins = []
for i in range(40):
    name = company_name()
    wins.append({
        "deal_id": f"WON-{60000 + i}",
        "company_name": name,
        "industry": random.choice(["B2B SaaS", "FinTech", "HealthTech",
                                   "PropTech", "Dev Tools", "Data & Analytics"]),
        "employee_count_at_signing": random.randint(60, 650),
        "funding_stage_at_signing": random.choice(["Series B", "Series C",
                                                    "Series D+", "PE-Backed"]),
        "deal_amount_usd": random.choice([95_000, 140_000, 210_000,
                                          280_000, 350_000, 420_000]),
        "engagement_type": random.choice(["Full Rebrand", "Brand System",
                                          "Website + Brand", "Campaign",
                                          "Category Positioning"]),
        "close_date": fmt(rand_date(730, 60)),
        "cycle_length_days": random.randint(45, 130),
        "primary_champion_title": random.choice(["CMO", "VP Marketing",
                                                  "Head of Brand", "CEO",
                                                  "Founder"]),
        "trigger_event": random.choice([
            "New CMO in seat",
            "Recent Series B close",
            "Product expansion",
            "M&A integration",
            "Board pressure on positioning",
            "Outgrew in-house team",
        ]),
    })
write_csv(
    BASE / "03_icp_scorer" / "historical_wins.csv",
    list(wins[0].keys()),
    [list(w.values()) for w in wins],
)

print("\nDone.")
