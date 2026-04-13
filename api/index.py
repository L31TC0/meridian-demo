"""
Vercel Python API — Account Brief Generator

GET  /api/          → account list + scenario classifications
POST /api/          → generate brief for a given account_id
POST /api/generate  → same (alias)
"""

import json
import sys
import os

from flask import Flask, request, jsonify

# Add the brief generator to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "01_account_brief"))
import brief_generator  # noqa: E402

OPEN_STAGES = brief_generator.OPEN_STAGES

app = Flask(__name__)


def _classify_accounts(accounts, contacts, deals, calls, emails):
    """Bucket accounts into scenario filters."""
    open_deals = deals[deals["stage"].isin(OPEN_STAGES)]
    open_deal_accts = set(open_deals["account_id"].unique())
    customer_ids = set(
        accounts[accounts["lifecycle_stage"] == "customer"]["account_id"]
    )

    deal_counts = deals.groupby("account_id").size()
    contact_counts = contacts.groupby("account_id").size()
    call_counts = calls.groupby("account_id").size()
    email_counts = emails.groupby("account_id").size()

    complex_ids = set()
    for aid in accounts["account_id"]:
        nd = deal_counts.get(aid, 0)
        nc = contact_counts.get(aid, 0)
        nca = call_counts.get(aid, 0)
        ne = email_counts.get(aid, 0)
        if nd >= 2 or (nc >= 3 and nca >= 1 and ne >= 1):
            complex_ids.add(aid)

    return {
        "upsell": sorted(open_deal_accts & customer_ids),
        "active_deal": sorted(open_deal_accts),
        "complex": sorted(complex_ids),
    }


@app.route("/api/", methods=["GET"])
@app.route("/api", methods=["GET"])
def get_accounts():
    """Return account list and scenario classifications."""
    accounts, contacts, deals, calls, emails = brief_generator.load_data()

    account_list = [
        {"account_id": row["account_id"], "company_name": row["company_name"]}
        for _, row in accounts.sort_values("company_name").iterrows()
    ]

    scenarios = _classify_accounts(accounts, contacts, deals, calls, emails)

    return jsonify({"accounts": account_list, "scenarios": scenarios})


@app.route("/api/", methods=["POST"])
@app.route("/api", methods=["POST"])
@app.route("/api/generate", methods=["POST"])
def generate():
    """Generate a brief for the given account_id."""
    body = request.get_json(force=True)
    account_id = body.get("account_id", "").strip()

    if not account_id:
        return jsonify({"error": "account_id required"}), 400

    try:
        accounts, contacts, deals, calls, emails = brief_generator.load_data()
        acct = brief_generator.find_account(accounts, account_id)
        aid = acct["account_id"]

        n_contacts = len(contacts[contacts["account_id"] == aid])
        n_deals = len(deals[deals["account_id"] == aid])
        n_calls = len(calls[calls["account_id"] == aid])
        n_emails = len(emails[emails["account_id"] == aid])
        total_points = n_contacts + n_deals + n_calls + n_emails

        brief_md = brief_generator.generate_brief(account_id)

        return jsonify({
            "brief_md": brief_md,
            "total_points": total_points,
            "account_name": acct["company_name"],
        })
    except SystemExit:
        return jsonify({"error": "Account not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
