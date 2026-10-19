# Cardwise India

Cardwise is an explainable Indian credit-card benefit workspace built with Streamlit, Plotly and SQLite. It recommends a card for a purchase, shows the rule that won, tracks a private wallet and transaction ledger, and provides annual-value, break-even, EMI and utilisation calculators.

## What is included

- Eight sourced starter cards: CASHBACK SBI, Amazon Pay ICICI, HDFC Millennia, Swiggy HDFC, Flipkart Axis, Airtel Axis, HSBC Live+ and Axis Cashback
- Decimal-based reward engine with merchant, category, channel, membership and exclusion conditions
- Statement-cycle cap groups and deterministic tie handling
- Full-catalog and owned-card recommendation scopes
- Responsive overview, card explorer, wallet, analytics and transaction views
- Transaction CSV import/export, refunds, estimated and actual rewards
- Annual net-value, fee break-even, reducing-balance EMI and credit-utilisation calculators
- Anonymous session-isolated SQLite workspaces suitable for a public demo
- Demo workspace, official source links, assumptions and automated tests

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

On Windows, activate with `.venv\Scripts\activate`.

## Test

```bash
python -m pytest -q
python -m compileall -q .
```

The suite also runs with `python -m unittest discover -v`.

## Project layout

```text
app.py                 Streamlit product UI
catalog.py             Eight-card catalog and versioned rule data
reward_engine.py       Decimal rule evaluation and ranking
database.py            Stable-ID, workspace-isolated persistence
calculators.py         EMI and utilisation math
utils.py               Formatting and responsive visual system
tests/                 Engine, calculator and isolation coverage
CARD_SOURCES.md         Official sources and modelling assumptions
LIMITATIONS.md          Known boundaries
CHANGELOG.md            Release history
.github/workflows/      CI checks
```

## Publish to GitHub

Create an empty GitHub repository, then run from this directory:

```bash
git init
git add .
git commit -m "Build Cardwise India"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

## Deploy on Streamlit Community Cloud

1. Connect the GitHub repository at [share.streamlit.io](https://share.streamlit.io/).
2. Choose `main` and set the app file to `app.py`.
3. Deploy. No secrets or environment variables are required.

GitHub Pages cannot run a Python/Streamlit server. Use GitHub for source control and Streamlit Community Cloud for hosting.

## Data and accuracy

Cardwise never asks for card numbers, credentials, names or contact details. Browser sessions receive separate temporary SQLite files. On Community Cloud, temporary data can disappear after a restart; connect a managed database before using this as a persistent multi-user service.

Issuer terms change and banks determine rewards using MCCs, merchant IDs and posting behavior. Read [CARD_SOURCES.md](CARD_SOURCES.md) and [LIMITATIONS.md](LIMITATIONS.md), and verify issuer terms before making a financial decision.
