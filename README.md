# Smart Card Benefit Recommender

Smart Card Benefit Recommender is an India-focused Python, Streamlit, and SQLite decision workspace that helps users compare transaction rewards, annual card value, EMI cost, and credit utilisation.

## Problem Statement

Credit card users often own multiple cards but do not always know which card gives the best reward for shopping, dining, fuel, groceries, travel, entertainment, utilities, online shopping, or other expenses.

## Objective

The application answers one main question:

> Which credit card should I use for this transaction to receive the highest benefit?

For example, if a transaction is for ₹5,000 in Shopping and one card gives 5% while another gives 2%, the app recommends the 5% card and estimates a ₹250 benefit.

## Features

- Streamlit financial dashboard
- SQLite database persistence
- Add, edit, delete, and view cards
- Category-wise reward percentages
- Rule-based best-card recommendation
- Tie handling when multiple cards give the same benefit
- Reward comparison table
- Transaction saving with recommended card and actually used card
- Missed reward calculation
- Transaction history with date, category, card, merchant, and sorting filters
- Spending and rewards analytics
- Demo card loading and reset option
- Input validation for amounts, names, fees, and reward rates
- Curated starter library of five real-world Indian credit cards
- Official issuer source links and visible reward assumptions
- Annual wallet-value calculator with fees deducted
- Reducing-balance EMI and processing-fee calculator
- Credit-utilisation planning check
- Responsive modern dashboard interface for desktop and mobile
- Interactive category comparison and dashboard period controls
- Graph-based recommendation comparison with interactive tooltips
- EMI cost-composition chart and credit-utilisation gauge

## Curated Indian Card Library

The starter set includes CASHBACK SBI Card, Amazon Pay ICICI Bank Credit Card, HDFC Bank Millennia Credit Card, Flipkart Axis Bank Credit Card, and Axis Bank Freecharge Plus Credit Card.

The included percentages are intentionally varied illustrative values designed to demonstrate the recommendation engine and produce meaningful category winners. They must not be treated as current issuer offers. Every rate remains editable from the Card Library.

## Technology Used

- Python 3
- Streamlit
- SQLite
- Pandas
- Plotly

## Project Structure

```text
SmartCardBenefitRecommender/
├── app.py
├── recommender.py
├── database.py
├── analytics.py
├── cards.py
├── utils.py
├── database/
│   └── smartcard.db
├── assets/
│   ├── logo.png
│   └── card_images/
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

Open a terminal inside the project folder and create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows, activate it with `.venv\Scripts\activate`. Then install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## How to Run

Start the application with:

```bash
streamlit run app.py
```

The app will open in your browser. If it does not open automatically, Streamlit will show a local URL in the terminal.

## Publish on GitHub

GitHub stores the project source code, while Streamlit Community Cloud runs the Python application. GitHub Pages cannot run a Streamlit/Python server.

1. Create a new empty repository on GitHub.
2. Open a terminal in this project folder.
3. Run these commands, replacing the example repository URL:

```bash
git init
git add .
git commit -m "Initial Smart Card Benefit Recommender"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

## Deploy with Streamlit Community Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io/) with GitHub.
2. Select **Create app** and choose the repository created above.
3. Set the branch to `main` and the main file path to `app.py`.
4. Choose Python 3.12 in Advanced settings if a version is requested.
5. Deploy the app. Streamlit installs `requirements.txt` automatically.

No secrets or environment variables are required.

### Cloud data note

The app uses a local SQLite file. It works on Streamlit Community Cloud, but changes made by visitors can be lost when the app restarts or is redeployed. For permanent multi-user storage, replace SQLite with a hosted database such as PostgreSQL before using the app in production.

## Automated Checks

The GitHub Actions workflow in `.github/workflows/ci.yml` checks Python syntax and runs unit tests after every push or pull request.

Run the same checks locally with:

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

## Database Information

The project uses SQLite. The database file is stored at:

```text
database/smartcard.db
```

The database is initialized automatically when the app starts, so the project still works even if the database file is deleted.

### Main Tables

`cards`

- Stores card name, bank, card type, annual fee, reward type, and category-wise reward rates.

`transactions`

- Stores transaction amount, merchant, category, recommended card, used card, recommended reward, actual reward, missed reward, and transaction date.

`categories`

- Stores default spending categories.

`settings`

- Reserved for simple project settings.

## Recommendation Logic

The recommendation engine is written in normal Python inside `recommender.py`.

Basic formula:

```python
benefit = transaction_amount * reward_percentage / 100
```

Steps:

1. Read all saved cards from SQLite.
2. Read the transaction amount and selected category.
3. Get each card's reward rate for that category.
4. Calculate the expected benefit for every card.
5. Sort cards by expected benefit.
6. Recommend the best card.
7. If multiple cards have the same highest benefit, show them as equal winners.

## Missed Reward Calculation

When saving a transaction, the app asks which card was actually used.

```text
missed_reward = recommended_reward - actual_reward
```

If the user selected a card that was as good as the recommended card, missed reward is ₹0.

## Screenshots Section

Add screenshots here after running the Streamlit app:

- Dashboard
- Find Best Card
- My Cards
- Analytics
- Transaction History

## Starter Data

The Settings page can load or restore the curated Indian card starter library. Users can edit every rate and fee to match their own statement terms.

## Future Improvements

- Real bank/card APIs
- Merchant-specific offers
- Reward point conversion rules
- AI spending predictions
- New-card recommendations
- User authentication
- Multiple user profiles
- Cloud database
- Mobile application

## Viva Explanation Notes

This project is separated into small modules:

- `database.py` handles all SQLite operations.
- `recommender.py` contains the recommendation algorithm.
- `analytics.py` uses Pandas to summarize transactions.
- `cards.py` stores constants, demo data, and validation.
- `utils.py` contains formatting and small helper functions.
- `app.py` builds the Streamlit interface.

This structure makes the code easier to explain, test, and maintain.
