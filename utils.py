"""Presentation utilities."""
from decimal import Decimal, InvalidOperation


def format_currency(value, show_zero=True):
    try: number = Decimal(str(value or 0))
    except InvalidOperation: number = Decimal("0")
    sign = "-" if number < 0 else ""; number = abs(number); whole, _, decimals = f"{number:.2f}".partition(".")
    if len(whole) > 3:
        tail, lead, groups = whole[-3:], whole[:-3], []
        while lead: groups.insert(0, lead[-2:]); lead = lead[:-2]
        whole = ",".join(groups + [tail])
    suffix = "" if decimals == "00" else f".{decimals}"
    return f"{sign}₹{whole}{suffix}"


def format_percentage(value):
    return f"{Decimal(str(value or 0)).normalize()}%"


def clean_text(value):
    return str(value or "").strip()


def get_custom_css():
    return """
    <style>
    :root{--accent:#7559db;--accent-2:#9d85ed;--lime:#b8ed69;--orange:#ff8a3d;--ink:#15171c;--muted:#6d7380;--line:#e8ebed;--mint:#e9f6ee;--canvas:#f3f8fa;--panel:#fff}
    html,body,[class*="css"]{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
    .stApp{background:var(--mint);color:var(--ink)}
    [data-testid="stAppViewContainer"]{padding:10px;background:var(--mint)}
    [data-testid="stMain"]{background:var(--canvas);border-radius:22px;overflow-y:auto!important;overflow-x:hidden!important;scrollbar-gutter:stable}
    [data-testid="stMainBlockContainer"]{width:100%;max-width:1480px!important;padding:0 1.55rem 3rem!important}
    [data-testid="stHeader"]{height:0;background:transparent}
    [data-testid="stToolbar"]{display:none}
    h1,h2,h3,p{letter-spacing:0} h1{font-size:1.65rem!important;line-height:1.15} h2{font-size:1.15rem!important} h3{font-size:.98rem!important}

    section[data-testid="stSidebar"]{display:none}
    [data-testid="collapsedControl"],[data-testid="stExpandSidebarButton"],.mobile-menu{display:none}
    .app-topbar{height:76px;display:grid;grid-template-columns:190px 1fr 190px;align-items:center;gap:1rem;margin:0 -1.55rem 1.2rem;padding:0 1.55rem;background:#f7fbfc;border-bottom:1px solid #e6efeb}
    .top-brand,.mobile-brand{display:flex;align-items:center;gap:.65rem;color:var(--ink)!important;text-decoration:none!important;font-size:1.1rem}
    .brand-glyph{width:30px;height:28px;display:flex;flex-direction:column;justify-content:center;gap:3px}
    .brand-glyph i{display:block;height:5px;background:var(--ink);border-radius:2px}.brand-glyph i:nth-child(1){width:26px}.brand-glyph i:nth-child(2){width:20px}.brand-glyph i:nth-child(3){width:26px}
    .top-nav{justify-self:center;display:flex;align-items:center;gap:.2rem;background:#fff;padding:5px;border-radius:999px;border:1px solid #edf0ee;box-shadow:0 5px 16px rgba(31,48,41,.04)}
    .top-nav a{color:#5d6269!important;text-decoration:none!important;padding:.55rem .82rem;border-radius:999px;font-size:.79rem;font-weight:600;white-space:nowrap}
    .top-nav a:hover{background:#f2f0fb;color:var(--accent)!important}.top-nav a.active{background:var(--lime);color:#1c2815!important}
    .header-status{justify-self:end;display:flex;align-items:center;gap:.45rem;background:#fff;padding:.55rem .72rem;border:1px solid var(--line);border-radius:999px;color:#4f5660;font-size:.75rem;font-weight:650}
    .header-status span{width:8px;height:8px;border-radius:50%;background:#53b86a;box-shadow:0 0 0 3px #e1f5e5}

    .page-title{margin:.25rem 0 1.2rem}.page-title h1{margin:0}.page-title>p{color:var(--muted);margin:.35rem 0 0;font-size:.88rem}
    div[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:16px;padding:1rem 1.05rem;box-shadow:0 4px 14px rgba(38,55,49,.035);min-height:116px}
    div[data-testid="stMetric"]:before{content:"";display:block;width:28px;height:4px;border-radius:4px;background:var(--lime);margin-bottom:.65rem}
    div[data-testid="stMetric"] *{color:var(--ink)!important}div[data-testid="stMetricValue"]{font-size:1.5rem;font-weight:750;overflow-wrap:anywhere}div[data-testid="stMetricLabel"]{color:var(--muted)!important;font-size:.8rem}
    div[data-testid="stHorizontalBlock"]{gap:.85rem}
    [data-testid="stPlotlyChart"],div[data-testid="stDataFrame"],div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border:1px solid var(--line);border-radius:16px!important;overflow:hidden;box-shadow:0 4px 14px rgba(38,55,49,.03)}
    [data-testid="stPlotlyChart"]{padding:.35rem}
    div[data-testid="stVerticalBlockBorderWrapper"]{padding:.3rem}
    .winner{background:#1c2030;color:#fff;border-radius:16px;padding:1.35rem 1.5rem;margin:1.1rem 0;border:0}.winner span{font-size:.68rem;font-weight:800;color:var(--lime)}.winner h2{color:#fff;margin:.25rem 0}.winner strong{font-size:1.8rem}.winner p{color:#d7d9e4;margin:.35rem 0 0}
    .catalog-card{background:#fff;border:1px solid var(--line);border-top:4px solid var(--card-accent);border-radius:16px;padding:1.1rem;margin:.45rem 0;min-height:170px;box-shadow:0 5px 16px rgba(38,55,49,.035)}
    .catalog-card small{color:var(--muted)}.catalog-card h3{margin:.5rem 0 .25rem}.catalog-card p{color:var(--muted);min-height:42px}.catalog-card>div{display:flex;justify-content:space-between;align-items:center}.catalog-card b{color:var(--card-accent)}
    .empty{height:280px;display:grid;place-items:center;color:var(--muted);border:1px dashed #ccd7d1;border-radius:16px;background:#fff}
    .stButton>button,.stDownloadButton>button,.stLinkButton>a{border-radius:10px!important;min-height:2.55rem;font-weight:700}.stButton>button[kind="primary"]{background:var(--accent);border-color:var(--accent)}
    div[data-baseweb="select"]>div,div[data-testid="stTextInput"] input,div[data-testid="stNumberInput"] input{border-radius:10px!important;background:#fff}
    [data-testid="stTabs"] [data-baseweb="tab-list"]{gap:.35rem;background:#fff;border:1px solid var(--line);padding:5px;border-radius:12px;width:max-content;max-width:100%}
    [data-testid="stTabs"] button{border-radius:8px;padding:.4rem .75rem}[data-testid="stTabs"] [aria-selected="true"]{background:#eeeafd;color:var(--accent)}
    .mobile-nav,.mobile-brand{display:none}

    @media(max-width:1100px){
      [data-testid="stAppViewContainer"]{padding:0}.stApp,[data-testid="stAppViewContainer"]{background:var(--canvas)}[data-testid="stMain"]{border-radius:0}
      [data-testid="stMainBlockContainer"]{padding:0 .9rem 4rem!important}.app-topbar{height:60px;display:flex;justify-content:center;margin:0 -.9rem 1rem;padding:0 3.4rem;background:#fff;position:sticky;top:0;z-index:90}.top-brand{font-size:1rem}.brand-glyph{display:none}
      .top-nav,.header-status,section[data-testid="stSidebar"]{display:none!important}
      [data-testid="collapsedControl"],[data-testid="stExpandSidebarButton"]{display:none!important}
      .app-topbar .top-brand .brand-glyph{display:none!important}.mobile-menu{display:block;position:absolute;left:.9rem;top:11px;z-index:130}.mobile-menu summary{list-style:none!important;width:38px;height:38px;display:flex!important;align-items:center;justify-content:center;background:#f3f5f4;border:1px solid var(--line);border-radius:9px;cursor:pointer;font-size:20px;font-weight:800;line-height:1}.mobile-menu summary::-webkit-details-marker{display:none!important}.mobile-menu summary::marker{display:none;content:""}
      .mobile-menu .mobile-nav{position:absolute;top:45px;left:0;width:min(82vw,300px);padding:.65rem;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 16px 38px rgba(22,32,28,.16)}
      section[data-testid="stSidebar"]>div{padding-top:1rem}.mobile-brand{display:flex;margin:.2rem 0 1.3rem}.mobile-nav{display:flex;flex-direction:column;gap:.2rem}.mobile-nav a{color:#4d535d!important;text-decoration:none!important;padding:.72rem .8rem;border-radius:9px;font-size:.9rem}.mobile-nav a.active{background:#eeeafd;color:var(--accent)!important;font-weight:750}
      .sidebar-note{background:#f5f7f6;border:1px solid var(--line);padding:.8rem;border-radius:10px;color:var(--muted);font-size:.78rem;margin:1.5rem 0 1rem}
      .page-title h1{font-size:1.38rem!important}.page-title{margin-bottom:1rem}.page-title>p{font-size:.82rem}
      div[data-testid="stHorizontalBlock"]{flex-wrap:wrap;gap:.7rem}div[data-testid="stHorizontalBlock"]>div{min-width:100%!important;width:100%!important}
      div[data-testid="stMetric"]{min-height:96px}.catalog-card{min-height:0}.catalog-card p{min-height:0}.js-plotly-plot,.plot-container{max-width:100%!important}.winner{padding:1.1rem}.winner strong{font-size:1.5rem}
      [data-testid="stTabs"] [data-baseweb="tab-list"]{width:100%;overflow-x:auto;flex-wrap:nowrap}[data-testid="stTabs"] button{white-space:nowrap}
    }
    </style>
    """
