"""
Vercel serverless function — Account Brief Generator

POST /api/generate
Body: { "account_id": "ACC-1171" }
Returns: { "brief_md": "...", "total_points": 23, "account_name": "..." }
"""

import json
import sys
import os
from http.server import BaseHTTPRequestHandler

# Add the brief generator to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "01_account_brief"))
import brief_generator  # noqa: E402

# Shared open-stages constant from brief_generator
OPEN_STAGES = brief_generator.OPEN_STAGES


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


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """GET /api/generate — returns account list + scenario classifications."""
        try:
            accounts, contacts, deals, calls, emails = brief_generator.load_data()

            account_list = [
                {"account_id": row["account_id"], "company_name": row["company_name"]}
                for _, row in accounts.sort_values("company_name").iterrows()
            ]

            scenarios = _classify_accounts(accounts, contacts, deals, calls, emails)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "accounts": account_list,
                "scenarios": scenarios,
            }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_POST(self):
        """POST /api/generate — generates a brief for the given account."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length))
            account_id = body.get("account_id", "").strip()

            if not account_id:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "account_id required"}).encode())
                return

            accounts, contacts, deals, calls, emails = brief_generator.load_data()
            acct = brief_generator.find_account(accounts, account_id)
            aid = acct["account_id"]

            # Count data points
            n_contacts = len(contacts[contacts["account_id"] == aid])
            n_deals = len(deals[deals["account_id"] == aid])
            n_calls = len(calls[calls["account_id"] == aid])
            n_emails = len(emails[emails["account_id"] == aid])
            total_points = n_contacts + n_deals + n_calls + n_emails

            brief_md = brief_generator.generate_brief(account_id)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "brief_md": brief_md,
                "total_points": total_points,
                "account_name": acct["company_name"],
            }).encode())
        except SystemExit:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Account not found"}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
