"""
Foundations brand constants — single source of truth for the Streamlit app.

All hex colors, font stacks, and brand copy live here so you can tweak
the look without hunting through app.py or CSS blocks.
"""

# ---------------------------------------------------------------------------
# Colors — from brand/brand_spec.md
# ---------------------------------------------------------------------------

ION_VIOLET = "#7C56FE"
IGNITE = "#FF582A"
ARCTIC_STEEL = "#A2C1C4"
ICE_BLUE = "#CFE7FF"
AZURE = "#B6BBFF"
PULSE = "#57FF60"
OBSIDIAN_BLACK = "#090D19"
ALLOY_SILVER = "#EFEFEF"

# Derived / UI-specific
SURFACE = "#111827"          # Slightly lighter than Obsidian for cards
SURFACE_BORDER = "#1E293B"   # Subtle border for elevated elements
MUTED_TEXT = "#8896A7"       # De-emphasized labels and metadata

# ---------------------------------------------------------------------------
# Typography — Inter via Google Fonts (PP Valve substitute)
# ---------------------------------------------------------------------------

FONT_FAMILY = "'Inter', 'IBM Plex Sans', Helvetica, Arial, sans-serif"
GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Inter:wght@300;400;500;700&display=swap"
)

# ---------------------------------------------------------------------------
# Brand copy
# ---------------------------------------------------------------------------

APP_TITLE = "Account Brief Generator"
APP_SUBTITLE = (
    "Pre-meeting intelligence across your CRM, calls, and email — in seconds."
)
FOOTER_TEXT = "Built by Foundations \u00b7 GTM Engineering for B2B Tech"
FOOTER_URL = "https://sellwithfoundations.com"
LOGO_PATH = "brand/foundations_logo_primary_reversed.png"

# ---------------------------------------------------------------------------
# Scenario filters — classify accounts into demo-ready buckets
# ---------------------------------------------------------------------------

SCENARIOS = [
    {
        "key": "upsell",
        "label": "Upsell / Cross-Sell",
        "description": "Existing customers with open expansion deals",
    },
    {
        "key": "active_deal",
        "label": "Active Deal",
        "description": "Accounts with deals currently in pipeline",
    },
    {
        "key": "complex",
        "label": "Complex Pipeline",
        "description": "Accounts with 2+ deals or high cross-file activity",
    },
]
