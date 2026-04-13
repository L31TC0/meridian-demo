"""
Foundations — Account Brief Generator (Streamlit app)

Wraps 01_account_brief/brief_generator.py in a branded, demo-ready UI.
Run: streamlit run app.py
"""

import sys
import os
import time

import streamlit as st
import pandas as pd

# Ensure the brief generator module is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "01_account_brief"))
import brief_generator  # noqa: E402

import theme  # noqa: E402

# ---------------------------------------------------------------------------
# Page config — must be the first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title=f"Foundations — {theme.APP_TITLE}",
    page_icon=theme.LOGO_PATH,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS — override Streamlit defaults with Foundations brand
# ---------------------------------------------------------------------------

st.markdown(f"""
<style>
    /* ---- Google Fonts ---- */
    @import url('{theme.GOOGLE_FONTS_URL}');

    /* ---- Global reset ---- */
    html, body, [class*="st-"] {{
        font-family: {theme.FONT_FAMILY};
    }}
    .stApp {{
        background-color: {theme.OBSIDIAN_BLACK};
    }}

    /* ---- Hide Streamlit chrome ---- */
    #MainMenu, footer, header {{
        visibility: hidden;
    }}

    /* ---- Typography ---- */
    h1 {{
        font-family: {theme.FONT_FAMILY};
        font-weight: 700;
        color: {theme.ALLOY_SILVER};
        font-size: 2rem;
        margin-bottom: 0;
    }}
    .subtitle {{
        font-family: {theme.FONT_FAMILY};
        font-weight: 300;
        color: {theme.MUTED_TEXT};
        font-size: 1.05rem;
        margin-top: 0.25rem;
        margin-bottom: 2rem;
    }}

    /* ---- Quick-select buttons ---- */
    .demo-btn-row {{
        display: flex;
        gap: 0.75rem;
        margin: 1rem 0 1.5rem 0;
    }}
    .demo-btn {{
        background: transparent;
        border: 1px solid {theme.ION_VIOLET};
        color: {theme.ION_VIOLET};
        padding: 0.5rem 1.1rem;
        border-radius: 6px;
        font-family: {theme.FONT_FAMILY};
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.2s, color 0.2s;
        text-align: left;
        line-height: 1.4;
    }}
    .demo-btn:hover {{
        background: {theme.ION_VIOLET};
        color: {theme.ALLOY_SILVER};
    }}
    .demo-btn .tag {{
        display: block;
        font-size: 0.7rem;
        font-weight: 300;
        color: {theme.MUTED_TEXT};
        margin-top: 2px;
    }}
    .demo-btn:hover .tag {{
        color: {theme.ALLOY_SILVER};
    }}

    /* ---- Generate button ---- */
    .stButton > button {{
        background-color: {theme.ION_VIOLET};
        color: {theme.ALLOY_SILVER};
        font-family: {theme.FONT_FAMILY};
        font-weight: 700;
        font-size: 1rem;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 2rem;
        transition: opacity 0.2s;
    }}
    .stButton > button:hover {{
        background-color: {theme.ION_VIOLET};
        color: {theme.ALLOY_SILVER};
        opacity: 0.85;
        border: none;
    }}
    .stButton > button:active, .stButton > button:focus {{
        background-color: {theme.ION_VIOLET};
        color: {theme.ALLOY_SILVER};
        border: none;
    }}

    /* ---- Metadata strip ---- */
    .meta-strip {{
        font-family: {theme.FONT_FAMILY};
        font-size: 0.8rem;
        font-weight: 400;
        color: {theme.ARCTIC_STEEL};
        padding: 0.6rem 0;
        margin-bottom: 0.5rem;
        letter-spacing: 0.02em;
    }}

    /* ---- Brief card ---- */
    .brief-card {{
        background: {theme.SURFACE};
        border: 1px solid {theme.SURFACE_BORDER};
        border-radius: 10px;
        padding: 2rem 2.25rem;
        margin: 0.5rem 0 2.5rem 0;
    }}
    .brief-card h1 {{
        font-size: 1.6rem;
        margin-bottom: 0.25rem;
        color: {theme.ALLOY_SILVER};
    }}
    .brief-card h2 {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {theme.ION_VIOLET};
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        letter-spacing: 0.01em;
    }}
    .brief-card p, .brief-card li {{
        font-size: 0.92rem;
        color: {theme.ALLOY_SILVER};
        line-height: 1.65;
    }}
    .brief-card strong {{
        color: {theme.ALLOY_SILVER};
        font-weight: 700;
    }}
    .brief-card em {{
        color: {theme.MUTED_TEXT};
    }}
    .brief-card hr {{
        border: none;
        border-top: 1px solid {theme.SURFACE_BORDER};
        margin: 1.5rem 0;
    }}

    /* ---- Footer ---- */
    .app-footer {{
        text-align: left;
        padding: 2rem 0 1.5rem 0;
        border-top: 1px solid {theme.SURFACE_BORDER};
        margin-top: 2rem;
    }}
    .app-footer p {{
        font-family: {theme.FONT_FAMILY};
        font-size: 0.8rem;
        font-weight: 400;
        color: {theme.MUTED_TEXT};
    }}
    .app-footer a {{
        color: {theme.ION_VIOLET};
        text-decoration: none;
    }}
    .app-footer a:hover {{
        text-decoration: underline;
    }}

    /* ---- Selectbox tweaks ---- */
    .stSelectbox label {{
        font-family: {theme.FONT_FAMILY};
        font-weight: 500;
        color: {theme.ALLOY_SILVER};
    }}
    .stSelectbox [data-baseweb="select"] {{
        background-color: {theme.SURFACE};
        border-color: {theme.SURFACE_BORDER};
    }}

    /* ---- Spinner / loading text ---- */
    .loading-msg {{
        font-family: {theme.FONT_FAMILY};
        font-weight: 300;
        font-size: 0.95rem;
        color: {theme.ARCTIC_STEEL};
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data — cached so we only read CSVs once per session
# ---------------------------------------------------------------------------

@st.cache_data
def load_all_data():
    """Load all five CSVs once — used for both filtering and brief generation."""
    return brief_generator.load_data()


@st.cache_data
def load_accounts():
    """Load the account list for the dropdown."""
    accounts = pd.read_csv(
        os.path.join(os.path.dirname(__file__), "01_account_brief", "accounts.csv")
    )
    return accounts.sort_values("company_name")


@st.cache_data
def classify_accounts():
    """Bucket every account into scenario filters.

    Returns a dict: scenario_key -> list of account_ids.
    - upsell:       lifecycle_stage == 'customer' AND has an open deal
    - active_deal:  has any open deal (regardless of lifecycle stage)
    - complex:      2+ total deals OR (3+ contacts AND 1+ call AND 1+ email)
    """
    accounts, contacts, deals, calls, emails = load_all_data()

    open_deals = deals[deals["stage"].isin(brief_generator.OPEN_STAGES)]
    open_deal_accounts = set(open_deals["account_id"].unique())
    customer_ids = set(
        accounts[accounts["lifecycle_stage"] == "customer"]["account_id"]
    )

    # Per-account counts for complexity check
    deal_counts = deals.groupby("account_id").size()
    contact_counts = contacts.groupby("account_id").size()
    call_counts = calls.groupby("account_id").size()
    email_counts = emails.groupby("account_id").size()

    upsell = sorted(open_deal_accounts & customer_ids)
    active_deal = sorted(open_deal_accounts)

    complex_ids = set()
    for aid in accounts["account_id"]:
        n_deals = deal_counts.get(aid, 0)
        n_contacts = contact_counts.get(aid, 0)
        n_calls = call_counts.get(aid, 0)
        n_emails = email_counts.get(aid, 0)
        if n_deals >= 2 or (n_contacts >= 3 and n_calls >= 1 and n_emails >= 1):
            complex_ids.add(aid)
    complex_list = sorted(complex_ids)

    return {"upsell": upsell, "active_deal": active_deal, "complex": complex_list}


@st.cache_data
def get_brief_and_stats(account_id):
    """Generate the brief and count data points touched."""
    accounts, contacts, deals, calls, emails = load_all_data()
    acct = brief_generator.find_account(accounts, account_id)
    aid = acct["account_id"]

    # Count data points pulled for this account
    n_contacts = len(contacts[contacts["account_id"] == aid])
    n_deals = len(deals[deals["account_id"] == aid])
    n_calls = len(calls[calls["account_id"] == aid])
    n_emails = len(emails[emails["account_id"] == aid])
    total_points = n_contacts + n_deals + n_calls + n_emails

    brief_md = brief_generator.generate_brief(account_id)

    return brief_md, total_points

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

logo_path = os.path.join(os.path.dirname(__file__), theme.LOGO_PATH)
if os.path.exists(logo_path):
    st.image(logo_path, width=140)

st.markdown(f"# {theme.APP_TITLE}")
st.markdown(f'<p class="subtitle">{theme.APP_SUBTITLE}</p>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Account selector — scenario filters narrow the dropdown
# ---------------------------------------------------------------------------

accounts_df = load_accounts()
scenario_map = classify_accounts()

# Build a lookup: account_id -> company_name for filtered lists
id_to_name = dict(zip(accounts_df["account_id"], accounts_df["company_name"]))

# Scenario filter buttons
st.markdown(
    '<p style="font-size:0.85rem; font-weight:500; color:{}; '
    'margin-bottom:0.25rem;">Filter by scenario</p>'.format(theme.MUTED_TEXT),
    unsafe_allow_html=True,
)

btn_cols = st.columns(len(theme.SCENARIOS))
for i, scenario in enumerate(theme.SCENARIOS):
    with btn_cols[i]:
        if st.button(
            f"{scenario['label']}\n{scenario['description']}",
            key=f"scenario_{scenario['key']}",
        ):
            st.session_state["active_scenario"] = scenario["key"]

# Determine which accounts to show in the dropdown
active_scenario = st.session_state.get("active_scenario")
if active_scenario and active_scenario in scenario_map:
    filtered_ids = scenario_map[active_scenario]
    scenario_label = next(
        s["label"] for s in theme.SCENARIOS if s["key"] == active_scenario
    )
    # Clear filter link
    if st.button("Clear filter", key="clear_filter", type="secondary"):
        st.session_state.pop("active_scenario", None)
        st.rerun()

    st.markdown(
        f'<p style="font-size:0.8rem; color:{theme.ARCTIC_STEEL};">'
        f"Showing <strong>{len(filtered_ids)}</strong> accounts matching "
        f"<strong>{scenario_label}</strong></p>",
        unsafe_allow_html=True,
    )
    options = [""] + [
        f"{id_to_name[aid]}  \u00b7  {aid}"
        for aid in filtered_ids if aid in id_to_name
    ]
else:
    options = [""] + [
        f"{row['company_name']}  \u00b7  {row['account_id']}"
        for _, row in accounts_df.iterrows()
    ]

selected = st.selectbox(
    "Select an account",
    options,
    format_func=lambda x: "Type to search..." if x == "" else x,
)

# Resolve which account to generate for
target_account_id = None
if selected:
    target_account_id = selected.split("\u00b7")[-1].strip()

# ---------------------------------------------------------------------------
# Generate button + output
# ---------------------------------------------------------------------------

generate = st.button("Generate Brief")

if generate and target_account_id:
    start = time.time()

    # Animated loading state
    placeholder = st.empty()
    placeholder.markdown(
        '<p class="loading-msg">Reading 5 data sources...</p>',
        unsafe_allow_html=True,
    )
    time.sleep(0.8)
    placeholder.markdown(
        '<p class="loading-msg">Synthesizing account brief...</p>',
        unsafe_allow_html=True,
    )
    time.sleep(0.6)

    brief_md, total_points = get_brief_and_stats(target_account_id)
    elapsed = time.time() - start

    placeholder.empty()

    # Metadata strip
    st.markdown(
        f'<div class="meta-strip">'
        f"Generated in {elapsed:.1f}s &nbsp;&middot;&nbsp; "
        f"5 sources &nbsp;&middot;&nbsp; "
        f"{total_points} data points synthesized"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Render brief inside a styled card
    st.markdown(
        f'<div class="brief-card">\n\n{brief_md}\n\n</div>',
        unsafe_allow_html=True,
    )

elif generate and not target_account_id:
    st.warning("Select an account first.")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown(
    f'<div class="app-footer">'
    f'<p>{theme.FOOTER_TEXT} &nbsp;&middot;&nbsp; '
    f'<a href="{theme.FOOTER_URL}" target="_blank">sellwithfoundations.com</a></p>'
    f"</div>",
    unsafe_allow_html=True,
)
