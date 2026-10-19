"""Smart Card Benefit Recommender: private, explainable Streamlit workspace."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from io import StringIO
from uuid import uuid4

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from calculators import calculate_emi, calculate_utilisation
from catalog import CATEGORIES, CHANNELS, REVIEWED_ON
from database import (add_custom_catalog_card, add_transaction, add_user_card, configure_workspace, delete_transaction,
                      delete_user_card, get_catalog_cards, get_transactions, get_user_cards,
                      initialize_database, load_demo_data, reset_database, update_user_card)
from reward_engine import TransactionContext, evaluate, money, rank
from utils import format_currency, get_custom_css

st.set_page_config(page_title="Cardwise India", page_icon="💳", layout="wide", initial_sidebar_state="collapsed")
workspace_from_url = st.query_params.get("workspace", "")
if workspace_from_url and all(char.isalnum() or char in "-_" for char in workspace_from_url):
    st.session_state.workspace_id = workspace_from_url[:80]
elif "workspace_id" not in st.session_state:
    st.session_state.workspace_id = uuid4().hex
    st.query_params["workspace"] = st.session_state.workspace_id
configure_workspace(st.session_state.workspace_id)
initialize_database()
st.markdown(get_custom_css(), unsafe_allow_html=True)

PLOT = {"displayModeBar": False, "responsive": True}
PAGES = {
    "overview": "Overview", "best-card": "Best card", "cards": "Card explorer",
    "wallet": "My cards", "analytics": "Analytics", "transactions": "Transactions",
    "calculators": "Calculators", "settings": "Settings",
}


def rerun():
    st.rerun()


def card_map():
    return {c["id"]: c for c in get_catalog_cards()}


def card_name(card_id):
    return card_map().get(card_id, {}).get("name", "Not selected")


def chart_style(fig, height=330):
    fig.update_layout(height=height, autosize=True, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Inter, Arial", color="#253047", size=12), margin=dict(l=8, r=8, t=38, b=8),
                      legend=dict(orientation="h", y=1.12, x=0), hoverlabel=dict(bgcolor="white"))
    fig.update_xaxes(gridcolor="#e9edf5", zeroline=False, automargin=True)
    fig.update_yaxes(gridcolor="#e9edf5", zeroline=False, automargin=True)
    return fig


def heading(title, subtitle):
    st.markdown(f'<div class="page-title"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def nav_links(active: str, mobile=False) -> str:
    classes = "mobile-nav" if mobile else "top-nav"
    inline_style = (
        ' style="position:fixed;top:64px;left:12px;right:12px;width:auto;padding:12px;'
        'background:#fff;border:1px solid #e8ebed;border-radius:12px;'
        'box-shadow:0 16px 38px rgba(22,32,28,.18);display:flex;flex-direction:column;z-index:999"'
        if mobile else ""
    )
    links = "".join(
        f'<a class="{"active" if slug == active else ""}" href="?view={slug}&workspace={st.session_state.workspace_id}" target="_self">{label}</a>'
        for slug, label in PAGES.items()
    )
    return f'<nav class="{classes}"{inline_style}>{links}</nav>'


def render_app_header(active: str) -> None:
    st.markdown(
        f'''<header class="app-topbar">
            <details class="mobile-menu"><summary aria-label="Open navigation" style="list-style:none;width:38px;height:38px;display:flex;align-items:center;justify-content:center;font-size:21px;background:#f3f5f4;border:1px solid #e8ebed;border-radius:9px">&#9776;</summary>{nav_links(active, mobile=True)}</details>
            <a class="top-brand" href="?view=overview&workspace={st.session_state.workspace_id}" target="_self"><b>Cardwise</b></a>
            {nav_links(active)}
            <div class="header-status"><span></span> Private workspace</div>
        </header>''',
        unsafe_allow_html=True,
    )


def transaction_form(key="recommend"):
    a, b, c = st.columns([1, 1.25, 1])
    amount = a.number_input("Amount (₹)", min_value=1.0, value=2500.0, step=100.0, key=f"{key}-amount")
    merchant = b.text_input("Merchant", value="Amazon", key=f"{key}-merchant")
    category = c.selectbox("Category", CATEGORIES, key=f"{key}-category")
    d, e = st.columns(2)
    channel = d.segmented_control("Channel", CHANNELS, default="Online", key=f"{key}-channel")
    membership = e.segmented_control("Amazon membership", ["Prime", "Non-Prime"], default="Prime", key=f"{key}-membership")
    excluded = st.multiselect("Special classification", ["fuel", "rent", "wallet", "government", "education", "insurance", "jewellery", "emi", "gaming", "tolls", "railways"], key=f"{key}-tags")
    return TransactionContext.create(amount, category, merchant, channel or "Online", membership or "Prime", excluded)


active_view = st.query_params.get("view", "overview")
if active_view not in PAGES:
    active_view = "overview"
page = PAGES[active_view]

with st.sidebar:
    st.markdown('<div class="mobile-brand"><span class="brand-glyph"><i></i><i></i><i></i></span><b>Cardwise</b></div>', unsafe_allow_html=True)
    st.markdown(nav_links(active_view, mobile=True), unsafe_allow_html=True)
    st.markdown('<div class="sidebar-note"><b>Private workspace</b><br>Your data stays in this anonymous browser session.</div>', unsafe_allow_html=True)
    st.caption(f"Catalog reviewed {REVIEWED_ON}")

render_app_header(active_view)

cards = get_catalog_cards()
owned = get_user_cards()
transactions = get_transactions()


if page == "Overview":
    heading("Make every swipe count", "A calm command center for spend, rewards and the next best card.")
    if not transactions:
        st.info("Start with demo data for a complete dashboard, or add your first transaction.")
        if st.button("Load demo workspace", type="primary"):
            load_demo_data(); rerun()
    spend = sum(Decimal(t["amount"]) * (-1 if t["is_refund"] else 1) for t in transactions)
    rewards = sum(Decimal(t["actual_reward"] or t["estimated_reward"]) * (-1 if t["is_refund"] else 1) for t in transactions)
    missed = Decimal("0")
    for t in transactions:
        tx = TransactionContext.create(t["amount"], t["category"], t["merchant"], t["channel"], tags=t["tags"])
        best = rank(cards, tx)[0]["reward"]
        missed += max(Decimal("0"), best - Decimal(t["actual_reward"] or t["estimated_reward"]))
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Tracked spend", format_currency(spend)); k2.metric("Reward value", format_currency(rewards))
    k3.metric("Missed opportunity", format_currency(missed)); k4.metric("Cards in wallet", len(owned))
    left, right = st.columns([1.45, 1])
    with left:
        st.subheader("Spend rhythm")
        if transactions:
            df = pd.DataFrame(transactions); df["month"] = pd.to_datetime(df.transaction_date).dt.to_period("M").astype(str); df["amount_num"] = pd.to_numeric(df.amount) * df.is_refund.map({0: 1, 1: -1})
            monthly = df.groupby("month", as_index=False).amount_num.sum()
            fig = px.area(monthly, x="month", y="amount_num", markers=True, color_discrete_sequence=["#6658d3"])
            fig.update_traces(fillcolor="rgba(102,88,211,.12)"); st.plotly_chart(chart_style(fig), use_container_width=True, config=PLOT)
        else: st.markdown('<div class="empty">Your monthly spend trend will appear here.</div>', unsafe_allow_html=True)
    with right:
        st.subheader("Category mix")
        if transactions:
            category = df.groupby("category", as_index=False).amount_num.sum().sort_values("amount_num")
            fig = px.bar(category, x="amount_num", y="category", orientation="h", color="amount_num", color_continuous_scale=["#d8d3ff", "#6658d3"])
            fig.update_layout(coloraxis_showscale=False); st.plotly_chart(chart_style(fig), use_container_width=True, config=PLOT)
        else: st.markdown('<div class="empty">Category allocation appears after your first transaction.</div>', unsafe_allow_html=True)
    if transactions:
        st.subheader("Recent activity")
        recent = pd.DataFrame([{"Date": t["transaction_date"], "Merchant": t["merchant"], "Category": t["category"], "Card": card_name(t["used_card_id"]), "Amount": float(t["amount"]), "Reward": float(t["actual_reward"] or t["estimated_reward"])} for t in transactions[:5]])
        st.dataframe(recent, hide_index=True, use_container_width=True)
    st.subheader("Quick recommendation")
    tx = transaction_form("overview")
    if st.button("Find my best card", type="primary", use_container_width=True):
        st.session_state.quick_results = rank(cards, tx)
    if "quick_results" in st.session_state:
        result = st.session_state.quick_results[0]
        st.success(f"Use {result['card_name']} · estimated {format_currency(result['reward'])} · {result['reason']}")

elif page == "Best card":
    heading("Best card for this purchase", "Compare your wallet or the full catalog with transparent rule-level reasoning.")
    tx = transaction_form("best")
    scope = st.segmented_control("Compare", ["My cards", "Full catalog"], default="Full catalog")
    if st.button("Rank cards", type="primary", use_container_width=True):
        ids = {x["catalog_card_id"] for x in owned}
        pool = [c for c in cards if c["id"] in ids] if scope == "My cards" else cards
        st.session_state.ranked = rank(pool or cards, tx)
        st.session_state.rank_tx = tx
    if "ranked" in st.session_state:
        ranked = st.session_state.ranked
        winner = ranked[0]
        st.markdown(f'<div class="winner"><span>TOP MATCH</span><h2>{winner["card_name"]}</h2><strong>{format_currency(winner["reward"])}</strong><p>{winner["reason"]}</p></div>', unsafe_allow_html=True)
        df = pd.DataFrame([{"Card": r["card_name"], "Reward": float(r["reward"]), "Rate": f"{r['rate']}%", "Why": r["reason"]} for r in ranked])
        fig = px.bar(df.head(8).sort_values("Reward"), x="Reward", y="Card", orientation="h", color="Reward", color_continuous_scale=["#d7d2ff", "#6658d3"])
        fig.update_layout(coloraxis_showscale=False); st.plotly_chart(chart_style(fig, 390), use_container_width=True, config=PLOT)
        st.dataframe(df, hide_index=True, use_container_width=True)
        used = st.selectbox("Card you will use", [r["card_id"] for r in ranked], format_func=card_name)
        actual = next(r for r in ranked if r["card_id"] == used)
        if st.button("Save this transaction"):
            add_transaction({"amount": st.session_state.rank_tx.amount, "merchant": st.session_state.rank_tx.merchant.title(), "category": st.session_state.rank_tx.category, "channel": st.session_state.rank_tx.channel, "transaction_date": date.today(), "used_card_id": used, "recommended_card_id": winner["card_id"], "estimated_reward": actual["reward"], "tags": list(st.session_state.rank_tx.tags)}); st.toast("Transaction saved")

elif page == "Card explorer":
    heading("Explore the catalog", "Compare sourced Indian cards or add your own reward profile.")
    with st.expander("Add a card manually"):
        st.caption("Create a private custom card when it is not available in the starter catalog.")
        with st.form("manual-card-form", clear_on_submit=True):
            a, b = st.columns(2)
            custom_name = a.text_input("Card name", placeholder="Example: My Rewards Card")
            custom_issuer = b.text_input("Issuer", placeholder="Bank name")
            c, d, e = st.columns(3)
            custom_network = c.selectbox("Network", ["Visa", "Mastercard", "RuPay", "American Express", "Other"])
            custom_fee = d.number_input("Annual fee (₹)", min_value=0.0, step=100.0)
            custom_waiver = e.number_input("Fee-waiver spend (₹)", min_value=0.0, step=1000.0)
            st.markdown("**Reward rates**")
            rate_columns = st.columns(2)
            custom_rates = {
                category: rate_columns[index % 2].number_input(
                    f"{category} (%)", min_value=0.0, max_value=100.0,
                    step=0.1, key=f"manual-rate-{category}",
                )
                for index, category in enumerate(CATEGORIES)
            }
            add_to_wallet = st.checkbox("Also add this card to My Cards", value=True)
            submitted = st.form_submit_button("Create custom card", type="primary", use_container_width=True)
        if submitted:
            if not custom_name.strip() or not custom_issuer.strip():
                st.error("Card name and issuer are required.")
            elif not any(custom_rates.values()):
                st.error("Enter at least one reward rate greater than 0%.")
            else:
                custom_rules = [
                    {
                        "id": f"manual-{index}", "rate": str(rate), "categories": [category],
                        "merchants": [], "channels": [], "cap": None, "cap_group": None,
                        "excludes": [], "membership": None, "priority": 20,
                        "min_amount": "0", "effective_from": date.today().isoformat(),
                        "note": "User-entered uncapped estimate.",
                    }
                    for index, (category, rate) in enumerate(custom_rates.items()) if rate > 0
                ]
                custom_id = add_custom_catalog_card({
                    "name": custom_name.strip(), "issuer": custom_issuer.strip(),
                    "network": custom_network, "annual_fee": str(custom_fee),
                    "fee_waiver": str(custom_waiver), "accent": "#6658d3",
                    "featured": "Custom reward profile", "rules": custom_rules,
                    "reviewed_on": date.today().isoformat(),
                })
                if add_to_wallet:
                    add_user_card(custom_id)
                st.toast("Custom card created")
                rerun()
    q = st.text_input("Search cards or issuers", placeholder="Try dining, Axis or Amazon")
    fee = st.selectbox("Annual fee", ["Any", "Lifetime free", "Up to ₹500", "Up to ₹1,000"])
    filtered = [c for c in cards if q.lower() in (c["name"] + c["issuer"] + c["featured"]).lower()]
    if fee == "Lifetime free": filtered = [c for c in filtered if Decimal(c["annual_fee"]) == 0]
    elif fee == "Up to ₹500": filtered = [c for c in filtered if Decimal(c["annual_fee"]) <= 500]
    elif fee == "Up to ₹1,000": filtered = [c for c in filtered if Decimal(c["annual_fee"]) <= 1000]
    for row_start in range(0, len(filtered), 2):
        cols = st.columns(2)
        for col, card in zip(cols, filtered[row_start:row_start + 2]):
            with col:
                top = max(Decimal(r["rate"]) for r in card["rules"])
                st.markdown(f'<div class="catalog-card" style="--card-accent:{card["accent"]}"><small>{card["issuer"]} · {card["network"]}</small><h3>{card["name"]}</h3><p>{card["featured"]}</p><div><b>Up to {top}%</b><span>Fee {format_currency(card["annual_fee"])}</span></div></div>', unsafe_allow_html=True)
                with st.expander("Rates, caps and assumptions"):
                    for r in sorted(card["rules"], key=lambda x: x["priority"], reverse=True):
                        cap = f" · cap ₹{r['cap']}" if r.get("cap") else " · uncapped"
                        st.write(f"**{r['rate']}%** — {r['id']}{cap}")
                        if r.get("note"): st.caption(r["note"])
                    if card.get("source"):
                        st.link_button("Official source", card["source"])
                    else:
                        st.caption("Manual card · rates supplied by you")
                if st.button("Add to my cards", key=f"add-{card['id']}", use_container_width=True):
                    if card["id"] in {x["catalog_card_id"] for x in owned}: st.toast("Already in your wallet")
                    else: add_user_card(card["id"]); rerun()

elif page == "My cards":
    heading("My cards", "Track limits and balances without storing account numbers.")
    if not owned: st.info("Your wallet is empty. Add cards from Card explorer.")
    for item in owned:
        card = card_map()[item["catalog_card_id"]]
        limit = float(item["credit_limit"]); balance = float(item["current_balance"])
        utilisation = balance / limit * 100 if limit else 0
        with st.container(border=True):
            left, right = st.columns([2, 1])
            left.subheader(item["nickname"] or card["name"]); left.caption(f"{card['issuer']} · ending digits are never requested")
            right.metric("Utilisation", f"{utilisation:.1f}%")
            with st.expander("Edit card details"):
                nick = st.text_input("Nickname", item["nickname"] or "", key=f"nick-{item['id']}")
                a, b = st.columns(2); lim = a.number_input("Credit limit", 0.0, value=limit, key=f"lim-{item['id']}"); bal = b.number_input("Current balance", 0.0, value=balance, key=f"bal-{item['id']}")
                if st.button("Save", key=f"save-{item['id']}"): update_user_card(item["id"], nick, lim, bal); rerun()
                if st.button("Remove", key=f"remove-{item['id']}"): delete_user_card(item["id"]); rerun()

elif page == "Analytics":
    heading("Reward analytics", "One filter controls every metric and chart on this page.")
    if not transactions: st.info("Add transactions or load demo data to unlock analytics.")
    else:
        df = pd.DataFrame(transactions); df["date"] = pd.to_datetime(df.transaction_date); df["amount_num"] = pd.to_numeric(df.amount) * df.is_refund.map({0: 1, 1: -1}); df["reward_num"] = pd.to_numeric(df.actual_reward.fillna(df.estimated_reward)) * df.is_refund.map({0: 1, 1: -1})
        start, end = st.date_input("Period", value=(df.date.min().date(), df.date.max().date()))
        view = df[(df.date.dt.date >= start) & (df.date.dt.date <= end)]
        a, b, c = st.columns(3); a.metric("Spend", format_currency(view.amount_num.sum())); b.metric("Rewards", format_currency(view.reward_num.sum())); c.metric("Effective return", f"{view.reward_num.sum()/view.amount_num.sum()*100:.2f}%" if view.amount_num.sum() else "0%")
        l, r = st.columns(2)
        by_card = view.groupby("used_card_id", as_index=False).reward_num.sum(); by_card["Card"] = by_card.used_card_id.map(card_name)
        fig = px.bar(by_card.sort_values("reward_num"), x="reward_num", y="Card", orientation="h", color_discrete_sequence=["#6658d3"]); l.plotly_chart(chart_style(fig), use_container_width=True, config=PLOT)
        by_cat = view.groupby("category", as_index=False).amount_num.sum(); fig = px.pie(by_cat, values="amount_num", names="category", hole=.62, color_discrete_sequence=px.colors.qualitative.Safe); r.plotly_chart(chart_style(fig), use_container_width=True, config=PLOT)

elif page == "Transactions":
    heading("Transactions", "Add, inspect, export and remove the activity behind your dashboard.")
    with st.expander("Add a transaction", expanded=not transactions):
        tx = transaction_form("ledger")
        used = st.selectbox("Card used", [c["id"] for c in cards], format_func=card_name)
        tdate = st.date_input("Date", date.today()); refund = st.checkbox("This is a refund")
        if st.button("Add transaction", type="primary"):
            ranked = rank(cards, tx); actual = evaluate(card_map()[used], tx)
            add_transaction({"amount": tx.amount, "merchant": tx.merchant.title(), "category": tx.category, "channel": tx.channel, "transaction_date": tdate, "used_card_id": used, "recommended_card_id": ranked[0]["card_id"], "estimated_reward": actual["reward"], "tags": list(tx.tags), "is_refund": refund}); rerun()
    if transactions:
        table = pd.DataFrame([{"Date": t["transaction_date"], "Merchant": t["merchant"], "Category": t["category"], "Amount": float(t["amount"]) * (-1 if t["is_refund"] else 1), "Card": card_name(t["used_card_id"]), "Reward": float(t["actual_reward"] or t["estimated_reward"]), "id": t["id"]} for t in transactions])
        st.dataframe(table.drop(columns="id"), hide_index=True, use_container_width=True)
        st.download_button("Export CSV", table.drop(columns="id").to_csv(index=False), "cardwise-transactions.csv", "text/csv")
        chosen = st.selectbox("Select transaction to remove", table.id, format_func=lambda x: f"{table.loc[table.id == x, 'Date'].iloc[0]} · {table.loc[table.id == x, 'Merchant'].iloc[0]}")
        if st.button("Delete selected", type="secondary"): delete_transaction(chosen); rerun()
    upload = st.file_uploader("Import CSV", type="csv", help="Columns: amount, merchant, category, channel, transaction_date, used_card_id")
    if upload and st.button("Import rows"):
        incoming = pd.read_csv(upload); required = {"amount", "merchant", "category", "channel", "transaction_date", "used_card_id"}
        if not required.issubset(incoming.columns): st.error("CSV is missing required columns: " + ", ".join(sorted(required - set(incoming.columns))))
        else:
            for _, row in incoming.iterrows():
                tx = TransactionContext.create(row.amount, row.category, row.merchant, row.channel); ranked = rank(cards, tx); actual = evaluate(card_map()[row.used_card_id], tx)
                add_transaction({**row.to_dict(), "recommended_card_id": ranked[0]["card_id"], "estimated_reward": actual["reward"]})
            rerun()

elif page == "Calculators":
    heading("Planning calculators", "Stress-test card value, borrowing cost and utilisation before acting.")
    tab1, tab2, tab3, tab4 = st.tabs(["Annual value", "Break-even", "EMI", "Utilisation"])
    with tab1:
        spends = {}; cols = st.columns(2)
        for i, category in enumerate(CATEGORIES): spends[category] = cols[i % 2].number_input(f"{category} / month", min_value=0.0, value=2000.0 if i < 4 else 0.0, step=500.0, key=f"annual-{category}")
        merchant = st.text_input("Representative merchant", "Amazon")
        results = []
        for card in cards:
            gross = sum(
                evaluate(card, TransactionContext.create(value, category, merchant))["reward"]
                for category, value in spends.items() if value > 0
            ) * 12
            fee = Decimal(card["annual_fee"]); annual_spend = Decimal(str(sum(spends.values()) * 12)); waived = bool(Decimal(card["fee_waiver"]) and annual_spend >= Decimal(card["fee_waiver"])); net = gross - (0 if waived else fee)
            results.append({"Card": card["name"], "Gross reward": float(gross), "Fee charged": 0 if waived else float(fee), "Net value": float(net)})
        out = pd.DataFrame(results).sort_values("Net value", ascending=False); st.dataframe(out, hide_index=True, use_container_width=True)
        fig = px.bar(out.sort_values("Net value"), x="Net value", y="Card", orientation="h", color="Net value", color_continuous_scale=["#d9d5ff", "#6658d3"]); fig.update_layout(coloraxis_showscale=False); st.plotly_chart(chart_style(fig, 390), use_container_width=True, config=PLOT)
    with tab2:
        card = st.selectbox("Card", cards, format_func=lambda x: x["name"], key="break-card"); expected_rate = st.number_input("Expected effective reward rate (%)", 0.1, 25.0, 2.0, .1)
        required = float(Decimal(card["annual_fee"]) * 100 / Decimal(str(expected_rate))) if expected_rate else 0
        st.metric("Spend to recover annual fee", format_currency(required)); st.caption("Annual fee ÷ effective reward rate. Taxes, welcome offers and redemption friction are excluded.")
    with tab3:
        a, b = st.columns(2); principal = a.number_input("Purchase amount", 1000.0, value=50000.0); rate = b.number_input("Annual interest (%)", 0.0, value=15.0); months = a.number_input("Tenure (months)", 1, value=12); fee = b.number_input("Processing fee (%)", 0.0, value=1.0)
        emi = calculate_emi(principal, rate, months, fee); x, y, z = st.columns(3); x.metric("Monthly EMI", format_currency(emi["monthly_emi"])); y.metric("Interest", format_currency(emi["interest"])); z.metric("Total cost", format_currency(emi["total_cost"]))
    with tab4:
        a, b = st.columns(2); balance = a.number_input("Outstanding balance", 0.0, value=25000.0); limit = b.number_input("Credit limit", 1.0, value=100000.0)
        util = calculate_utilisation(balance, limit); st.metric("Utilisation", f"{util['percentage']}%", util["band"]); st.progress(min(float(util["percentage"]) / 100, 1.0))

else:
    heading("Settings & data", "Control demo data and your anonymous workspace.")
    st.subheader("Data controls")
    if st.button("Load fresh demo data", type="primary"): load_demo_data(); rerun()
    st.warning("Reset removes cards and transactions from this browser session only.")
    if st.button("Reset workspace"): reset_database(); rerun()
    st.subheader("About the catalog")
    st.write("Reward terms can change without notice. Cardwise records source links and a review date, but always verify the issuer terms before applying or spending.")
    st.caption(f"Catalog reviewed {REVIEWED_ON} · No card numbers, names, email addresses or credentials are collected.")
