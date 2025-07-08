import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from pymongo import MongoClient
from datetime import timedelta, datetime, timezone, time
from random import randint
import altair as alt
from collections import defaultdict, deque

# ───── Streamlit Setup ─────
st.set_page_config(layout="wide", page_title="Sniper Analysis by Lampros")

# ───── Global Styling ─────
st.markdown("""
    <style>
    /* Remove top padding in main block */
    .block-container {
        padding-top: 0rem !important;
    }
    header[data-testid="stHeader"] {
        background: transparent;
        visibility: visible;
    }
    [data-testid="stSidebarNav"] {
        display: none;
    }
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
    }
    section[data-testid="stSidebar"] .markdown-text-container,
    div[role="radiogroup"] label span,
    h1 {
        color: white !important;
    }
    html, body {
        overflow-x: hidden !important;
    }
    .stApp {
        width: 100vw;
        box-sizing: border-box;
        background: radial-gradient(circle, rgba(18, 73, 97, 1) 0%, rgba(5, 27, 64, 1) 100%);
    }
    .glass-kpi {
        background: rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 1rem;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        color: white;
        text-align: center;
    }
    .glass-kpi h4 {
        font-size: 14px;
        font-weight: 600;
        text-align: center;
        margin-bottom: 0; line-height: 1;
        text-transform: uppercase;
        color: #ffffffcc;
    }
    .glass-kpi p {
        font-size: 35px;
        font-weight: bold;
        text-align: center;
        margin: 0; line-height: 1;
    }
    .kpi-inner {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# ───── Sidebar ─────
def render_sidebar():
    """Render the custom sidebar with navigation and branding."""
    with st.sidebar:
        st.markdown("---")
        #HERE, WE CHECK WHICH PAGE WE ARE ON AND LATER USE IT TO HIGHLIGHT THE CURRENT PAGE
        current_script = os.path.basename(__file__).lower()
        routes = [
            ("SELECT ANOTHER TOKEN", "/cards2", "cards2.py"),
            ("GLOBAL SNIPER ANALYSIS", "/global_snipers", "global_snipers.py")
        ]

        for label, path, filename in routes:
            is_active = filename.lower() == current_script
            bg = "#124961" if is_active else "transparent"
            st.markdown(
                f"""
                <a href="{path}" style="
                    display: block;
                    padding: 0.5rem 1rem;
                    margin-bottom: 0.5rem;
                    font-weight: bold;
                    border-radius: 6px;
                    color: white;
                    background-color: {bg};
                    text-decoration: none;
                ">{label}</a>
                """,
                unsafe_allow_html=True
            )
        st.markdown("---")

render_sidebar()
#-- CSS FOR THE TABLE
scrollable_style = """
<style>
    /* Wrapper container for scrollable table */
    .scrollable {
        max-height: 400px;
        overflow-y: auto;
        position: relative;
        overflow-x: auto;
        width: 78vw;
        box-sizing: border-box;
        display: block;
        font-family: 'Epilogue', sans-serif;
        font-size: 14px;
        color: #222;
    }
    
    /* Table styling */
    .scrollable table {
        width: 100%;
        backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin: 0 auto 0 0;
        table-layout: auto;
        text-align: center;
        border-collapse: separate;
        border-spacing: 0;
        border: 1px solid transparent; 
    }
    
    /* Table headers and cells */
    .scrollable th,
    .scrollable td {
        padding: 1px 3px;
        text-align: center;
        font-size: 15px;
        color: #fff;
        font-weight: 300;
        border: 1px solid transparent;
    }
    
    /* Header styling */
    .scrollable th {
        background: rgba(70, 70, 70);
        position: sticky; top:0;
        color: #fff;
        text-transform: uppercase;
        font-weight: 400;
    }
    
    /* Rounded top corners on first and last th */
    .scrollable th:first-child {
        border-top-left-radius: 8px;
    }
    .scrollable th:last-child {
        border-top-right-radius: 8px;
    }
    </style>
    """
st.markdown(scrollable_style, unsafe_allow_html=True)
# ───── Load DB Connection ─────
load_dotenv()
dbconn = os.getenv("MongoLink")
client = MongoClient(dbconn)
db = client['genesis_tokens_swap_info']


# ───── Token Parameter ─────
query_params = st.query_params
token = query_params.get('token', '').lower().strip()
if not token:
    st.warning("⚠️ No token specified. Redirecting to token choice...")
    st.switch_page("cards2.py")
colh, cold = st.columns([1, 3])
with colh:
    st.markdown(f"<h1 style='margin-top: 0rem; color: white;'>TOKEN {token.upper()}</h1>", unsafe_allow_html=True)

with cold:
    st.write("")
    doc = db["swap_progress"].find_one({"token_symbol": token.upper()})
    if doc:
        token_addr = doc.get("token_address", "N/A")
        lp_addr = doc.get("lp", "N/A")
        genesis_block = doc.get("genesis_block", "N/A")

        # We cannot get name, dao, or timestamp from swap_progress — we'll extract from first swap doc
        #token_collection = f"{token.lower()}_swap"
        token_collection = ['jarvis_swap', 'afath_swap', 'pilot_swap', 'tian_swap', 'vgn_swap', 'badai_swap',
                       'bolz_swap', 'trivi_swap', 'vruff_swap', 'wbug_swap', 'aispace_swap', 'wint_swap', 
                       'ling_swap', 'gloria_swap', 'light_swap', 'rwai_swap', 'nyko_swap', 'super_swap',
                       'xllm2_swap', 'maneki_swap', 'whim_swap']
        swap_doc = None
        for col_name in token_collection:
            result = db[col_name].find_one(
                {"genesis_token_symbol": token.upper()},
                sort=[("timestamp", 1)]
            )
            if result:
                swap_doc = result
                break

        name = swap_doc.get("persona_name", "N/A") if swap_doc else "N/A"
        dao_addr = swap_doc.get("persona_dao", "N/A") if swap_doc else "N/A"
        timestamp = swap_doc.get("timestamp", 0) if swap_doc else 0
        launch_time = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%d-%m-%Y %H:%M') if timestamp else "N/A"

# ───── Collection Naming ─────
token_in_col = f"{token.upper()}_IN"
token_out_col = f"{token.upper()}_OUT"
virtual_in_col = "Virtual_IN"
virtual_out_col = "Virtual_OUT"
collection_name = f"{token}_swap"

# ───── Fetch Data ─────
data = list(db[collection_name].find({}, {
    "blockNumber": 1, "txHash": 1, "maker": 1, "swapType": 1, "label": 1, "timestampReadable": 1,
    token_in_col: 1, token_out_col: 1, virtual_in_col: 1, virtual_out_col: 1,
    "genesis_usdc_price": 1, "genesis_virtual_price": 1, "virtual_usdc_price": 1
}))
#st.write("Fetched rows:", len(data))
#st.write("Sample doc:", data[0] if data else "No data")

tabdf = pd.DataFrame(data).fillna(0)

# ───── Process Data ─────
def extract_amount(row):
    if row.get("swapType") == "buy":
        return pd.Series([row.get(token_out_col), row.get(virtual_in_col)])
    elif row.get("swapType") == "sell":
        return pd.Series([row.get(token_in_col), row.get(virtual_out_col)])
    return pd.Series([None, None])

tabdf[["TokenAmount", "Virtual"]] = tabdf.apply(extract_amount, axis=1)
tabdf["TokenAmount"] = pd.to_numeric(tabdf["TokenAmount"]).round(4)
tabdf["Virtual"] = pd.to_numeric(tabdf["Virtual"]).round(4)
tabdf.rename(columns={"TokenAmount": token.upper()}, inplace=True)

tabdf["txHash"] = tabdf["txHash"].apply(lambda tx: f"<a href='https://basescan.org/tx/{tx}' target='_blank'>Link to txn</a>")
tabdf["swapType"] = tabdf["swapType"].apply(lambda x: f"<span style='color: {'green' if x == 'buy' else 'red'}; font-weight:bold'>{x}</span>")

tabdf = tabdf[[
    "blockNumber", "txHash", "maker", "swapType", "label", "timestampReadable",
    token.upper(), "Virtual", "genesis_usdc_price", "genesis_virtual_price", "virtual_usdc_price"
]].rename(columns={
    "blockNumber": "BLOCK", "txHash": "TX HASH", "maker": "MAKER",
    "swapType": "TX TYPE", "label": "SWAP TYPE", "timestampReadable": "TIME",
    "Virtual": "VIRTUAL",
    "genesis_usdc_price": "GENESIS \nPRICE ($)",
    "genesis_virtual_price": "GENESIS PRICE \n($VIRTUAL)",
    "virtual_usdc_price": "VIRTUAL \nPRICE ($)"
})
tabdf["MAKER"] = tabdf["MAKER"].apply(lambda addr: f"<span title='{addr}'>{addr[:5]}...{addr[-5:]}</span>" if isinstance(addr, str) else addr)
tabdf["TIME_PARSED"] = pd.to_datetime(tabdf["TIME"], errors='coerce')
tabdf["TX_TYPE_RAW"] = tabdf["TX TYPE"].str.extract(r">(\w+)<")
tabdf["TRANSACTION VALUE ($)"] = (pd.to_numeric(tabdf[token.upper()], errors="coerce") * pd.to_numeric(tabdf["GENESIS \nPRICE ($)"], errors="coerce")).round(4)
filtered_df = tabdf.copy()

sortable_columns = [
    "BLOCK",                   # from "blockNumber"
    "TIME",                    # from "timestampReadable"
    "VIRTUAL",                 # from "Virtual"
    "GENESIS \nPRICE ($)",     # from "genesis_usdc_price"
    "GENESIS PRICE \n($VIRTUAL)", # from "genesis_virtual_price"
    "VIRTUAL \nPRICE ($)"      # from "virtual_usdc_price"
]

tab1, tab2, tab3 = st.tabs(["TRANSCTIONS", "SNIPER INSIGHTS", "OTHER"])

with tab1:
    # ───── Filters: Panel 1 ─────
    with st.container():
        col1, col2, col3, col4, col5, col10 = st.columns(6)
    
        with col1:
            st.markdown("<div style='color: white; font-weight: 500;'>Transaction Type</div>", unsafe_allow_html=True)
            swap_filter = st.segmented_control("", options=["all", "buy", "sell"], default="all")
    
        with col2:
            st.markdown("<div style='color: white; font-weight: 500;'>Swap Type</div>", unsafe_allow_html=True)
            label_options = ["All"] + sorted(tabdf["SWAP TYPE"].dropna().unique())
            label_filter = st.selectbox("", label_options)
    
        with col3:
            st.markdown("<div style='color: white; font-weight: 500;'>Date Range</div>", unsafe_allow_html=True)
            date_range = st.date_input("", value=(tabdf["TIME_PARSED"].min(), tabdf["TIME_PARSED"].max()))
    
        with col4:
            st.markdown("<div style='color: white; font-weight: 500;'>Sort by</div>", unsafe_allow_html=True)
            sort_col = st.selectbox("Sort by", sortable_columns)
    
        with col5:
            st.markdown("<div style='color: white; font-weight: 500;'>Order</div>", unsafe_allow_html=True)
            sort_dir = st.radio("", options=["Ascending", "Descending"], horizontal=True)
    
        with col10:
            st.markdown("<div style='color: white; font-weight: 500;'>Search BLOCK or MAKER</div>", unsafe_allow_html=True)
            search_query = st.text_input("")
            if search_query:
                q = search_query.strip().lower()
                filtered_df = filtered_df[
                    filtered_df["BLOCK"].astype(str).str.contains(q) |
                    filtered_df["MAKER"].str.lower().str.contains(q)
                ]
    
    # ───── Apply Filters ─────
    if swap_filter != "all":
        filtered_df = filtered_df[filtered_df["TX_TYPE_RAW"].str.lower() == swap_filter.lower()]
    if label_filter != "All":
        filtered_df = filtered_df[filtered_df["SWAP TYPE"] == label_filter]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1]) + timedelta(days=1)
        filtered_df = filtered_df[(filtered_df["TIME_PARSED"] >= start_date) & (filtered_df["TIME_PARSED"] <= end_date)]
    
    # ───── Filters: Panel 2 (Numeric Range) ─────
    with st.container():
        col6, col7 = st.columns([1, 4])
        with col6:
            st.markdown("<div style='color: white; font-weight: 500;'>Filter by</div>", unsafe_allow_html=True)
            numeric_columns = [token.upper(), "VIRTUAL", "GENESIS \nPRICE ($)", "TRANSACTION VALUE ($)", "GENESIS PRICE \n($VIRTUAL)", "VIRTUAL \nPRICE ($)"]
            selected_col = st.selectbox("", numeric_columns)
    
        with col7:
            if selected_col in filtered_df.columns and not filtered_df[selected_col].dropna().empty:
                col_min, col_max = filtered_df[selected_col].min(), filtered_df[selected_col].max()
                if pd.notnull(col_min) and pd.notnull(col_max) and col_min != col_max:
                    st.markdown(f"<div style='color: white; font-weight: 500;'>Range for {selected_col}</div>", unsafe_allow_html=True)
                    value_range = st.slider(
                        "", float(col_min), float(col_max), (float(col_min), float(col_max)),
                        step=0.000001, format="%.6f"
                    )
                    filtered_df = filtered_df[
                        (filtered_df[selected_col] >= value_range[0]) &
                        (filtered_df[selected_col] <= value_range[1])
                    ]
    
    #--TABLE RENDERING
    filtered_df = filtered_df.sort_values(by=sort_col, ascending=(sort_dir == "Ascending"))
    filtered_df = filtered_df.drop(columns=["TX_TYPE_RAW", "TIME_PARSED"], errors="ignore")
    #ordering columns
    ordered_cols = [
        "BLOCK", "TX HASH", "MAKER", "TX TYPE", "SWAP TYPE", "TIME",
        token.upper(), "VIRTUAL", "GENESIS \nPRICE ($)", "TRANSACTION VALUE ($)",
        "GENESIS PRICE \n($VIRTUAL)", "VIRTUAL \nPRICE ($)"
    ]
    filtered_df = filtered_df[[col for col in ordered_cols if col in filtered_df.columns]]
    
    html_table = filtered_df.to_html(escape=False, index=False, float_format="%.4f")
    
    with st.container():
        st.markdown(scrollable_style, unsafe_allow_html=True)
        st.markdown(f"<div class='scrollable'>{html_table}</div>", unsafe_allow_html=True)


with tab2:

    # ───── Token from Query Params ─────
    token_upper = token.upper()

    # ───── Load Swap Data for Token ─────
    @st.cache_data(ttl=300)
    def load_swap_data(token):
        col_name = f"{token}_swap"
        data = list(db[col_name].find())
        if not data:
            return None
        df = pd.DataFrame(data)
        df.drop(columns=["_id"], errors="ignore", inplace=True)
        df["token_name"] = token.upper()
        df["timestampReadable"] = pd.to_datetime(df["timestampReadable"], errors='coerce')
        return df


    # ───── Launch Block (fallback logic) ─────
    @st.cache_data(ttl=600)
    def load_launch_blocks():
        client = MongoClient(dbconn)
        db = client["genesis_tokens_swap_info"]
        try:
            persona_data = list(db["swap_progress"].find({}, {"token_symbol": 1, "genesis_block": 1}))
            df = pd.DataFrame(persona_data)
            if not df.empty and "token_symbol" in df and "genesis_block" in df:
                return dict(zip(df["token_symbol"], df["genesis_block"]))
        except Exception as e:
            print("Error loading launch blocks:", e)
        return {}

    # ───── Sniper Detection Logic ─────
    #@st.cache_data(ttl=300)
    def process_sniper_data(combined_df, token_launch_blocks):
        buy_df = combined_df[combined_df["swapType"] == "buy"].copy()
        buy_df = buy_df.sort_values(by=["maker", "timestampReadable"])
        chunked_buys = []
        time_threshold = pd.Timedelta(minutes=10)

        for maker, group in buy_df.groupby("maker"):
            current_chunk = []
            chunk_start_time = None
            current_sum = 0
            for row in group.itertuples():
                if not current_chunk:
                    chunk_start_time = row.timestampReadable
                    current_chunk = [row]
                    token_prefix = row.token_name  # e.g., "AFATH"
                    field = f"{token_prefix}_OUT_BeforeTax"
                    current_sum = getattr(row, field, 0)  # fallback to 0 if field missing

                elif row.timestampReadable - chunk_start_time <= time_threshold:
                    current_chunk.append(row)
                    current_sum += getattr(row, field, 0)
                else:
                    if current_sum > 100000:
                        chunked_buys.extend(current_chunk)
                    chunk_start_time = row.timestampReadable
                    current_chunk = [row]
                    token_prefix = row.token_name
                    field = f"{token_prefix}_OUT_BeforeTax"
                    current_sum = getattr(row, field, 0)

            if current_sum > 100000:
                chunked_buys.extend(current_chunk)

        df_chunked_large_buys = pd.DataFrame(chunked_buys).drop_duplicates()
        if "transactionFee" in df_chunked_large_buys.columns:
            df_high_gas = df_chunked_large_buys[df_chunked_large_buys["transactionFee"] > 0.000002]
        else:
            df_high_gas = df_chunked_large_buys.copy()
            st.warning("⚠️ 'transactionFee' missing in dataset — skipping gas filter.")


        def is_sniper_buy(row):
            launch_block = token_launch_blocks.get(row["token_name"])
            return launch_block is not None and row["blockNumber"] <= launch_block + 100

        df_sniper_buys = df_high_gas[df_high_gas.apply(is_sniper_buy, axis=1)]

        sells = combined_df[combined_df["swapType"] == "sell"][["maker", "timestampReadable", "token_name"]]
        merged = pd.merge(
            df_sniper_buys[["maker", "timestampReadable", "token_name"]],
            sells,
            on=["maker", "token_name"],
            suffixes=("_buy", "_sell"),
        )
        merged["time_diff"] = (merged["timestampReadable_sell"] - merged["timestampReadable_buy"]).dt.total_seconds()
        quick_sells = merged[merged["time_diff"].between(0, 20 * 60)]
        potential_sniper_df = df_sniper_buys[df_sniper_buys["maker"].isin(quick_sells["maker"])].copy()
        #st.write("🔍 Potential sniper rows found:", len(potential_sniper_df))
        return potential_sniper_df, combined_df

    # ───── PnL Calculation ─────
    @st.cache_data(ttl=300)
    def calculate_pnl(potential_sniper_df, combined_df):
        results = []
        sniper_pairs = potential_sniper_df[["maker", "token_name"]].drop_duplicates()
        for _, row in sniper_pairs.iterrows():
            maker = row["maker"]
            token = row["token_name"]
            df = combined_df[(combined_df["maker"] == maker) & (combined_df["token_name"] == token)]
            df = df.sort_values(by="timestamp")
            trades = defaultdict(list)

            # Dynamic field names based on token
            out_before_tax_col = f"{token}_OUT_BeforeTax"
            out_after_tax_col = f"{token}_OUT_AfterTax"
            in_before_tax_col = f"{token}_IN_BeforeTax"
            in_after_tax_col = f"{token}_IN_AfterTax"

            buy_txn_count = (df["swapType"] == "buy").sum()
            sell_txn_count = (df["swapType"] == "sell").sum()
            first_buy_time = df.loc[df["swapType"] == "buy", "timestampReadable"].min()
            last_sell_time = df.loc[df["swapType"] == "sell", "timestampReadable"].max()
            avg_buy_price = df.loc[df["swapType"] == "buy", "genesis_usdc_price"].mean()
            avg_sell_price = df.loc[df["swapType"] == "sell", "genesis_usdc_price"].mean()
            total_tax_paid = df["Tax_1pct"].sum()
            total_tx_fees = df["transactionFee"].sum()

            for _, tx in df.iterrows():
                token_prefix = tx["token_name"]
                
                if tx["swapType"] == "buy":
                    out_before_tax = tx.get(f"{token_prefix}_OUT_BeforeTax", 0.0)
                    out_after_tax = tx.get(f"{token_prefix}_OUT_AfterTax", 0.0)
                    trades[maker].append({
                        "type": "buy",
                        "amount": out_after_tax,
                        "cost": out_before_tax,
                        "price": tx["genesis_usdc_price"]
                    })

                elif tx["swapType"] == "sell":
                    in_before_tax = tx.get(f"{token}_IN_BeforeTax", 0.0)
                    in_after_tax = tx.get(f"{token}_IN_AfterTax", 0.0)
                    trades[maker].append({
                        "type": "sell",
                        "amount": in_after_tax,
                        "from_wallet": in_before_tax,
                        "price": tx["genesis_usdc_price"]
                    })


            buy_queue = deque()
            realized = 0.0
            for tx in trades[maker]:
                if tx["type"] == "buy":
                    buy_queue.append({
                        "amount": tx["amount"],
                        "cost": tx["cost"],
                        "price": tx["price"]
                    })
                elif tx["type"] == "sell":
                    to_match = tx["from_wallet"]
                    proceeds = tx["amount"] * tx["price"]
                    while to_match > 0 and buy_queue:
                        buy = buy_queue.popleft()
                        match_amt = min(to_match, buy["amount"])
                        match_cost = buy["cost"] * (match_amt / buy["amount"])
                        realized += proceeds * (match_amt / tx["from_wallet"]) - match_cost * buy["price"]
                        to_match -= match_amt
                        leftover = buy["amount"] - match_amt
                        if leftover > 0:
                            buy_queue.appendleft({
                                "amount": leftover,
                                "cost": buy["cost"] * (leftover / buy["amount"]),
                                "price": buy["price"]
                            })

            remaining = sum(b["amount"] for b in buy_queue)
            latest_price = combined_df[combined_df["token_name"] == token].sort_values(by="timestamp", ascending=False).head(1)["genesis_usdc_price"].values[0]
            unrealized = remaining * latest_price

            results.append({
                "Wallet Address": maker,
                "Net PnL ($)": round(realized, 4),
                "Unrealized PnL ($)": round(unrealized, 4),
                "Remaining Tokens": float(f"{remaining:.4f}"),
                "Txn Count\n(BUY)": buy_txn_count,
                "Txn Count\n(SELL)": sell_txn_count,
                "First Buy Time": first_buy_time,
                "Last Sell Time": last_sell_time,
                "Average Buy Price ($)": round(avg_buy_price, 4),
                "Average Sell Price ($)": round(avg_sell_price, 4),
                "Total Tax Paid": round(total_tax_paid, 4),
                "Total Tx Fees Paid (ETH)": round(total_tx_fees, 4)
            })
        print("Returning results with rows:", len(results))
        print("Result keys:", results[0].keys() if results else "No results")

        return pd.DataFrame(results)
    #st.write("PnL DF Columns:", pnl_df.columns.tolist())


    # ───── Load and Process ─────
    with st.spinner("Loading data..."):
        combined_df = load_swap_data(token)
        if combined_df is None:
            st.error("No data found for this token.")
            st.stop()
        token_launch_blocks = load_launch_blocks()
        potential_sniper_df, combined_df = process_sniper_data(combined_df, token_launch_blocks)
        
        pnl_df = calculate_pnl(potential_sniper_df, combined_df)

    #-----------------------------------------------------------------------------------------------------------------------------
    # Streamlit UI
    st.title(f"Potential Snipers – PnL Overview for {token_upper}")
    st.subheader("📊 Sniper Summary Table")

    # Create filtered_df and add S.No once, cleanly
    filtered_df = pnl_df.copy().reset_index(drop=True)
    #filtered_df["S.No"] = range(1, len(filtered_df) + 1)
    filtered_df["Wallet Display"] = filtered_df["Wallet Address"].apply(
        lambda addr: f"<span title='{addr}'>{addr[:5]}...{addr[-5:]}</span>" if isinstance(addr, str) else addr
    )

    filtered_df["Net PnL ($)_styled"] = filtered_df["Net PnL ($)"].apply(
        lambda x: f"<span style='color: {'#74fe64' if x >= 0 else 'red'}; font-weight:bold'>{x:.4f}</span>"
    )
    # Sort by Net PnL descending
    filtered_df = filtered_df.sort_values(by="Net PnL ($)", ascending=False).reset_index(drop=True)
    #filtered_df["S.No"] = range(1, len(filtered_df) + 1)
    #st.dataframe(filtered_df, hide_index=True)
    # Convert column to numeric
    filtered_df['Net PnL ($)'] = pd.to_numeric(filtered_df['Net PnL ($)'], errors='coerce')

    # Get successful snipers
    successful_snipers = filtered_df[filtered_df['Net PnL ($)'] > 0]
    # Columns in desired order
    ordered_cols = [
        "Wallet Display",           # styled version
        "Net PnL ($)_styled",       # styled version
        "Unrealized PnL ($)",
        "Remaining Tokens",
        "Txn Count (BUY)",
        "Txn Count (SELL)",
        "First Buy Time",
        "Last Sell Time",
        "Average Buy Price ($)",
        "Average Sell Price ($)",
        "Total Tax Paid",
        "Total Tx Fees Paid (ETH)"
    ]

    # Rename for display and render
    html_table_sniper = (
        filtered_df[ordered_cols]
        .rename(columns={
            "Wallet Display": "Wallet Address",
            "Net PnL ($)_styled": "Net PnL ($)"
        })
        .to_html(escape=False, index=False)
    )
    st.markdown(f"<div class='scrollable'>{html_table_sniper}</div>", unsafe_allow_html=True)

    # KPIs
    num_unique_snipers = filtered_df['Wallet Address'].nunique()
    success_rate = (len(successful_snipers) / num_unique_snipers * 100) if num_unique_snipers > 0 else 0


    total_realized_pnl = filtered_df['Net PnL ($)'].sum()
    total_unrealized_pnl = filtered_df['Unrealized PnL ($)'].sum()

    # Total tokens held by snipers
    total_tokens_held = filtered_df['Remaining Tokens'].sum()
    total_supply = 1_000_000_000  # adjust if needed
    tokens_held_percentage = (total_tokens_held / total_supply) * 100 if total_supply > 0 else 0

    st.subheader('Sniper KPIs')
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        st.markdown(f"""
            <div class="glass-kpi">
                <h4>Total Unique Snipers</h4>
                <p>{num_unique_snipers}</p>
            </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
            <div class="glass-kpi">
                <h4>Success Rate of Trades (%)</h4>
                <p>{success_rate:.2f}%</p>
            </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
            <div class="glass-kpi">
                <h4>Total Realized PnL</h4>
                <p>${total_realized_pnl:,.2f}</p>
            </div>
        """, unsafe_allow_html=True)

    with kpi4:
        st.markdown(f"""
            <div class="glass-kpi">
                <h4>Total Unrealized PnL</h4>
                <p>${total_unrealized_pnl:,.2f}</p>
            </div>
        """, unsafe_allow_html=True)

    with kpi5:
        st.markdown(f"""
            <div class="glass-kpi">
                <h4>      Total Tokens Held by Snipers (%)</h4>
                <p>{tokens_held_percentage:.4f}%</p>
            </div>
        """, unsafe_allow_html=True)

    # Top 5 Traders by Net PnL
    st.subheader('Top 5 Traders by Total Net PnL')
    top5 = filtered_df.nlargest(5, 'Net PnL ($)')
    st.markdown("""
        <style>
        .glass-chart {
            padding: 1rem;
            margin: 1rem 0;
            background: rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.25);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        }
        </style>
    """, unsafe_allow_html=True)
    bar_chart = alt.Chart(top5).mark_bar().encode(
        y=alt.Y('Wallet Address:N', title='Wallet Address', sort=top5['Wallet Address'].tolist()),
        x=alt.X('Net PnL ($):Q', title='Net PnL ($)'),
        tooltip=['Wallet Address', 'Net PnL ($)']
    ).properties(
        width=600,
        height=300
    )
    st.altair_chart(bar_chart, use_container_width=True)

with tab3:
        st.header("MORE INSIGHTS INCOMING, STAY TUNED!")
