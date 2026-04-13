# Account Brief Generator — Streamlit App

Demo-ready web app that generates pre-meeting account briefs by pulling across 5 CRM data sources (accounts, contacts, deals, call notes, email threads).

Built for live sales demos by [Foundations](https://sellwithfoundations.com).

## Local setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Opens at `http://localhost:8501`.

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), connect the repo.
3. Set **Main file path** to `app.py`.
4. No secrets or env vars needed — the app runs entirely off the CSVs in `01_account_brief/`.

## Deploy to Railway

1. Push this repo to GitHub.
2. Create a new Railway project, connect the repo.
3. Set the **Start command** to:
   ```
   streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
4. Railway will auto-detect `requirements.txt` and install dependencies.

## Project structure

```
meridian/
├── app.py                          # Streamlit app (UI wrapper)
├── theme.py                        # Brand constants (colors, fonts, copy)
├── requirements.txt                # Python dependencies
├── .streamlit/config.toml          # Streamlit theme config
├── brand/                          # Brand assets
│   ├── foundations_logo_primary_reversed.png
│   ├── brand_spec.md               # Authoritative brand reference
│   └── README.md
└── 01_account_brief/               # Data + brief engine (do not modify)
    ├── brief_generator.py
    ├── accounts.csv
    ├── contacts.csv
    ├── deals.csv
    ├── call_notes.csv
    └── email_threads.csv
```

## Customization

All brand colors, fonts, and copy are centralized in `theme.py`. Streamlit theme defaults are in `.streamlit/config.toml`. Edit those two files to restyle without touching `app.py`.
