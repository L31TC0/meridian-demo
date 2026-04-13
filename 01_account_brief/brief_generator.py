#!/usr/bin/env python3
"""
Account Brief Generator — Meridian Brand Partners

Generates a one-page pre-meeting brief for any account by pulling across
five HubSpot-style CSVs: accounts, contacts, deals, call notes, and email
threads. Designed as a live-demo artifact for Foundations GTM sales calls.

Usage:
    python3 brief_generator.py "Vantage Analytics"
    python3 brief_generator.py ACC-1171
"""

import sys
import os
from datetime import datetime, timedelta

import pandas as pd

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TODAY = datetime(2026, 4, 13)
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

SENIORITY_RANK = {"C-Suite": 1, "VP": 2, "Director": 3}
OPEN_STAGES = {"Discovery", "Scoping", "Proposal Sent", "Negotiation"}

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data():
    """Read all five CSVs and parse date columns."""
    accounts = pd.read_csv(os.path.join(DATA_DIR, "accounts.csv"))
    contacts = pd.read_csv(os.path.join(DATA_DIR, "contacts.csv"))
    deals = pd.read_csv(os.path.join(DATA_DIR, "deals.csv"))
    calls = pd.read_csv(os.path.join(DATA_DIR, "call_notes.csv"))
    emails = pd.read_csv(os.path.join(DATA_DIR, "email_threads.csv"))

    # Parse dates so we can sort and compare
    accounts["last_activity_date"] = pd.to_datetime(accounts["last_activity_date"])
    contacts["last_meeting_date"] = pd.to_datetime(contacts["last_meeting_date"])
    deals["expected_close_date"] = pd.to_datetime(deals["expected_close_date"])
    deals["created_date"] = pd.to_datetime(deals["created_date"])
    calls["call_date"] = pd.to_datetime(calls["call_date"])
    emails["sent_date"] = pd.to_datetime(emails["sent_date"])

    return accounts, contacts, deals, calls, emails


def find_account(accounts, query):
    """Look up an account by ID or company name (case-insensitive)."""
    # Try exact account_id match first
    match = accounts[accounts["account_id"] == query]
    if not match.empty:
        return match.iloc[0]

    # Fall back to case-insensitive name search
    match = accounts[accounts["company_name"].str.lower() == query.lower()]
    if not match.empty:
        return match.iloc[0]

    # Partial name match as last resort
    match = accounts[accounts["company_name"].str.lower().str.contains(query.lower())]
    if len(match) == 1:
        return match.iloc[0]
    if len(match) > 1:
        names = match["company_name"].tolist()
        print(f"Ambiguous — multiple matches: {', '.join(names)}", file=sys.stderr)
        sys.exit(1)

    print(f"No account found for '{query}'", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Brief sections
# ---------------------------------------------------------------------------

def section_header(acct):
    """Company name, firmographics, owner, lifecycle stage."""
    arr = int(acct["estimated_arr_usd"])
    arr_str = f"${arr // 1_000_000}M" if arr >= 1_000_000 else f"${arr // 1_000}K"
    return (
        f"# {acct['company_name']}\n\n"
        f"**Industry:** {acct['industry']}  \n"
        f"**Size:** {acct['employee_count_band']} employees · {arr_str} est. ARR  \n"
        f"**HQ:** {acct['hq_city']}  \n"
        f"**Lifecycle stage:** {acct['lifecycle_stage']}  \n"
        f"**Owner:** {acct['hubspot_owner']}  \n"
    )


def section_deals(deals_df, acct_id):
    """Open deals with stage, amount, close date, next step. Notes closed-lost history."""
    acct_deals = deals_df[deals_df["account_id"] == acct_id].copy()
    open_deals = acct_deals[acct_deals["stage"].isin(OPEN_STAGES)].sort_values(
        "expected_close_date"
    )
    closed_lost = acct_deals[acct_deals["stage"] == "Closed Lost"]

    lines = ["## Deal Status\n"]

    if open_deals.empty:
        lines.append("No open deals.\n")
    else:
        for _, d in open_deals.iterrows():
            close_str = d["expected_close_date"].strftime("%Y-%m-%d")
            amt = f"${int(d['amount_usd']):,}"
            lines.append(
                f"- **{d['deal_name']}** — {d['stage']}, {amt}, "
                f"expected close {close_str}  \n"
                f"  Next step: {d['next_step']}\n"
            )

    if not closed_lost.empty:
        for _, d in closed_lost.iterrows():
            lines.append(
                f"- *{d['deal_name']}* — Closed Lost "
                f"({d['expected_close_date'].strftime('%Y-%m-%d')})"
                f" · Reason: {d['loss_reason']}\n"
            )

    return "\n".join(lines)


def section_stakeholders(contacts_df, calls_df, acct_id):
    """Top 3 contacts ranked by seniority, then engagement (opens + clicks)."""
    acct_contacts = contacts_df[contacts_df["account_id"] == acct_id].copy()
    if acct_contacts.empty:
        return "## Key Stakeholders\n\nNo contacts on file.\n"

    # Engagement score: email opens + clicks, used as tiebreaker after seniority
    acct_contacts["engagement"] = (
        acct_contacts["email_opens_last_90d"] + acct_contacts["email_clicks_last_90d"]
    )
    acct_contacts["seniority_rank"] = acct_contacts["seniority"].map(SENIORITY_RANK)

    top = acct_contacts.sort_values(
        ["seniority_rank", "engagement"], ascending=[True, False]
    ).head(3)

    # Pull last call per contact for a recent-activity note
    acct_calls = calls_df[calls_df["account_id"] == acct_id]
    last_call_by_contact = (
        acct_calls.sort_values("call_date").groupby("contact_id").last()
    )

    lines = ["## Key Stakeholders\n"]
    for _, c in top.iterrows():
        last_mtg = c["last_meeting_date"]
        mtg_str = last_mtg.strftime("%Y-%m-%d") if pd.notna(last_mtg) else "none"

        # Check if this contact has call notes for a richer description
        activity_note = ""
        if c["contact_id"] in last_call_by_contact.index:
            last = last_call_by_contact.loc[c["contact_id"]]
            summary_snippet = last["summary"][:80].rsplit(" ", 1)[0] + "…"
            activity_note = f" · Last call {last['call_date'].strftime('%Y-%m-%d')}: {summary_snippet}"

        lines.append(
            f"- **{c['full_name']}**, {c['title']} ({c['seniority']})  \n"
            f"  Email engagement: {c['email_opens_last_90d']} opens / "
            f"{c['email_clicks_last_90d']} clicks (90d) · Last meeting: {mtg_str}"
            f"{activity_note}\n"
        )

    return "\n".join(lines)


def section_timeline(calls_df, emails_df, acct_id):
    """Last 5 touches across calls and emails, chronological, one-line each."""
    acct_calls = calls_df[calls_df["account_id"] == acct_id][
        ["call_date", "summary", "contact_id"]
    ].copy()
    acct_calls["type"] = "Call"
    acct_calls.rename(columns={"call_date": "date", "summary": "detail"}, inplace=True)

    acct_emails = emails_df[emails_df["account_id"] == acct_id][
        ["sent_date", "subject", "snippet", "direction"]
    ].copy()
    acct_emails["type"] = "Email"
    # Combine subject + direction into a readable one-liner
    acct_emails["detail"] = (
        acct_emails["direction"] + " — " + acct_emails["subject"]
        + ": " + acct_emails["snippet"]
    )
    acct_emails.rename(columns={"sent_date": "date"}, inplace=True)

    combined = pd.concat(
        [acct_calls[["date", "type", "detail"]], acct_emails[["date", "type", "detail"]]]
    ).sort_values("date", ascending=False)

    last_5 = combined.head(5).iloc[::-1]  # chronological order (oldest first)

    lines = ["## Recent Activity Timeline\n"]
    if last_5.empty:
        lines.append("No recent activity.\n")
    else:
        for _, row in last_5.iterrows():
            date_str = row["date"].strftime("%Y-%m-%d")
            # Truncate detail to keep it scannable
            detail = row["detail"][:120].rsplit(" ", 1)[0]
            if len(row["detail"]) > 120:
                detail += "…"
            lines.append(f"- **{date_str}** [{row['type']}] {detail}\n")

    return "\n".join(lines)


def section_risks(acct, deals_df, calls_df, emails_df, contacts_df, acct_id):
    """Surface concrete risk signals from the data — don't fabricate.

    Signals are bucketed into three priority tiers, then capped at 3 bullets.
    Tier 1 (deal-level): overdue close dates, stalled deals, closed-lost history
    Tier 2 (senior stakeholders): C-Suite/VP contacts gone quiet (60+ days)
    Tier 3 (everything else): lower-seniority disengagement, general patterns
    """
    # Each signal is a (tier, text) tuple so we can sort before capping
    TIER_DEAL = 1
    TIER_SENIOR_CONTACT = 2
    TIER_OTHER = 3

    signals = []
    acct_deals = deals_df[deals_df["account_id"] == acct_id]
    open_deals = acct_deals[acct_deals["stage"].isin(OPEN_STAGES)]

    # --- Tier 1: deal-level risks ---

    # Overdue expected close date
    for _, d in open_deals.iterrows():
        if pd.notna(d["expected_close_date"]) and d["expected_close_date"] < TODAY:
            days_over = (TODAY - d["expected_close_date"]).days
            signals.append((TIER_DEAL,
                f"**Overdue deal** — \"{d['deal_name']}\" expected to close "
                f"{d['expected_close_date'].strftime('%Y-%m-%d')} ({days_over} days ago), "
                f"still in {d['stage']}."
            ))

    # No activity in 30+ days with an open deal on the table
    acct_calls = calls_df[calls_df["account_id"] == acct_id]
    acct_emails = emails_df[emails_df["account_id"] == acct_id]
    all_dates = pd.concat([acct_calls["call_date"], acct_emails["sent_date"]])
    if not all_dates.empty and not open_deals.empty:
        last_touch = all_dates.max()
        gap_days = (TODAY - last_touch).days
        if gap_days > 30:
            signals.append((TIER_DEAL,
                f"**Engagement gap** — last touch was {gap_days} days ago "
                f"({last_touch.strftime('%Y-%m-%d')}) with an open deal on the table."
            ))

    # Closed-lost history on this account
    closed_lost = acct_deals[acct_deals["stage"] == "Closed Lost"]
    if not closed_lost.empty:
        reasons = closed_lost["loss_reason"].dropna().unique()
        signals.append((TIER_DEAL,
            f"**Prior closed-lost deal(s)** on this account — "
            f"reason(s): {', '.join(reasons)}. Worth addressing head-on."
        ))

    # --- Tier 2: senior stakeholder disengagement (C-Suite / VP) ---

    acct_contacts = contacts_df[contacts_df["account_id"] == acct_id]
    for _, c in acct_contacts.iterrows():
        if c["seniority"] in ("C-Suite", "VP"):
            last_mtg = c["last_meeting_date"]
            if pd.isna(last_mtg):
                signals.append((TIER_SENIOR_CONTACT,
                    f"**Quiet stakeholder** — {c['full_name']} ({c['title']}) "
                    f"has no meeting on record."
                ))
            elif (TODAY - last_mtg).days > 60:
                signals.append((TIER_SENIOR_CONTACT,
                    f"**Quiet stakeholder** — {c['full_name']} ({c['title']}) "
                    f"last met {last_mtg.strftime('%Y-%m-%d')} "
                    f"({(TODAY - last_mtg).days} days ago)."
                ))

    # Sort by tier (deal risks first, then senior contacts, then other)
    signals.sort(key=lambda x: x[0])

    # Cap at 3 and note any overflow
    lines = ["## Risk Signals\n"]
    if not signals:
        lines.append("No material risks flagged — account is tracking normally.\n")
    else:
        shown = signals[:3]
        overflow = len(signals) - 3

        for _, text in shown:
            lines.append(f"- {text}\n")

        if overflow > 0:
            lines.append(
                f"\n_+ {overflow} additional lower-priority signal"
                f"{'s' if overflow != 1 else ''}_\n"
            )

    return "\n".join(lines)


def section_talking_points(acct, deals_df, calls_df, contacts_df, acct_id):
    """3–4 talking points grounded in specific account data."""
    points = []
    acct_deals = deals_df[deals_df["account_id"] == acct_id]
    open_deals = acct_deals[acct_deals["stage"].isin(OPEN_STAGES)]
    closed_lost = acct_deals[acct_deals["stage"] == "Closed Lost"]
    acct_calls = calls_df[calls_df["account_id"] == acct_id].sort_values("call_date")
    acct_contacts = contacts_df[contacts_df["account_id"] == acct_id]

    # Point 1: address the open deal status
    if not open_deals.empty:
        d = open_deals.iloc[0]
        if pd.notna(d["expected_close_date"]) and d["expected_close_date"] < TODAY:
            points.append(
                f"Address the timeline on **{d['deal_name']}** — expected close was "
                f"{d['expected_close_date'].strftime('%Y-%m-%d')}. Ask what's blocking "
                f"the move from {d['stage']} to close."
            )
        else:
            points.append(
                f"Drive **{d['deal_name']}** forward — currently in {d['stage']}. "
                f"Next step: {d['next_step']}."
            )

    # Point 2: reference the most recent call topic
    if not acct_calls.empty:
        last_call = acct_calls.iloc[-1]
        snippet = last_call["summary"][:100].rsplit(" ", 1)[0]
        points.append(
            f"Pick up the thread from the {last_call['call_date'].strftime('%Y-%m-%d')} "
            f"call — {snippet}…"
        )

    # Point 3: if there's a closed-lost deal, name it
    if not closed_lost.empty:
        d = closed_lost.iloc[0]
        points.append(
            f"Acknowledge the prior loss on *{d['deal_name']}* (reason: {d['loss_reason']}). "
            f"Proactively address what's different this time."
        )

    # Point 4: stakeholder-specific angle — engage the highest-seniority contact
    if not acct_contacts.empty:
        ranked = acct_contacts.copy()
        ranked["_rank"] = ranked["seniority"].map(SENIORITY_RANK)
        top_contact = ranked.sort_values("_rank").iloc[0]
    else:
        top_contact = None

    if top_contact is not None and len(points) < 4:
        points.append(
            f"Ensure **{top_contact['full_name']}** ({top_contact['title']}) is looped "
            f"in — they're the most senior contact and any deal will need their buy-in."
        )

    lines = ["## Recommended Talking Points\n"]
    for i, p in enumerate(points, 1):
        lines.append(f"{i}. {p}\n")

    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_brief(query):
    """Build the full markdown brief for a given account name or ID."""
    accounts, contacts, deals, calls, emails = load_data()
    acct = find_account(accounts, query)
    acct_id = acct["account_id"]

    sections = [
        section_header(acct),
        section_deals(deals, acct_id),
        section_stakeholders(contacts, calls, acct_id),
        section_timeline(calls, emails, acct_id),
        section_risks(acct, deals, calls, emails, contacts, acct_id),
        section_talking_points(acct, deals, calls, contacts, acct_id),
    ]

    return "\n---\n\n".join(sections)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 brief_generator.py <company_name_or_account_id>",
              file=sys.stderr)
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(generate_brief(query))
