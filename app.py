import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="IPL Auction Dashboard",
    layout="wide"
)

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    df = pd.read_csv("IPL_Squad_2023_Auction_Dataset.csv")
    df.drop(['Unnamed: 0'], axis=1, inplace=True)

    # Fix data issues
    df["COST IN ₹ (CR.)"] = pd.to_numeric(df["COST IN ₹ (CR.)"], errors="coerce").fillna(0)

    # ✅ FIXED STATUS LOGIC (IMPORTANT)
    df["Status"] = df.apply(
        lambda row: "Retained" if row["Base Price"] == "Retained"
        else ("Sold" if row["COST IN ₹ (CR.)"] > 0 else "Unsold"),
        axis=1
    )

    # Price Category
    df["Price Category"] = pd.cut(
        df["COST IN ₹ (CR.)"],
        bins=[-1, 2, 5, 10, 20],
        labels=["Low", "Medium", "High", "Very High"]
    )

    return df

df = load_data()

# ------------------ TITLE ------------------
st.title("🏏 IPL Auction Analysis Dashboard")

# ------------------ KPI METRICS ------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Players", len(df))
col2.metric("Total Teams", df["Team"].nunique())
col3.metric("Total Spending (Cr)", round(df["COST IN ₹ (CR.)"].sum(), 2))
col4.metric("Unsold Players", len(df[df["Status"] == "Unsold"]))

st.markdown("---")

# ------------------ SIDEBAR ------------------
st.sidebar.header("🔍 Filters")

team = st.sidebar.selectbox("Select Team", sorted(df["Team"].unique()))
player_type = st.sidebar.selectbox("Select Player Type", sorted(df["TYPE"].unique()))
status = st.sidebar.selectbox("Player Status", ["All", "Retained", "Sold", "Unsold"])

search = st.sidebar.text_input("Search Player")

# ------------------ FILTER LOGIC ------------------
filtered = df.copy()

if team:
    filtered = filtered[filtered["Team"] == team]

if player_type:
    filtered = filtered[filtered["TYPE"] == player_type]

if status != "All":
    filtered = filtered[filtered["Status"] == status]

if search:
    filtered = filtered[filtered["Player's List"].str.contains(search, case=False)]

# ------------------ DATA TABLE ------------------
st.subheader("📋 Filtered Players")
st.dataframe(filtered, width="stretch")

# ------------------ TEAM SPENDING ------------------
st.subheader("💰 Team Spending Overview")

team_spending = df.groupby("Team")["COST IN ₹ (CR.)"].sum().sort_values()

fig1, ax1 = plt.subplots()
team_spending.plot(kind='barh', ax=ax1)
ax1.set_xlabel("Amount (Cr)")
ax1.set_ylabel("Team")
st.pyplot(fig1)

# ------------------ TYPE SPENDING ------------------
st.subheader("📊 Spending by Player Type")

type_spending = df.groupby("TYPE")["COST IN ₹ (CR.)"].sum()

fig2, ax2 = plt.subplots()
type_spending.plot(kind='bar', ax=ax2)
ax2.set_ylabel("Amount (Cr)")
st.pyplot(fig2)

# ------------------ TOP PLAYERS ------------------
st.subheader("🔥 Top 10 Expensive Players")

top_players = df.sort_values("COST IN ₹ (CR.)", ascending=False).head(10)

fig3, ax3 = plt.subplots()
top_players.plot(
    x="Player's List",
    y="COST IN ₹ (CR.)",
    kind="bar",
    ax=ax3
)
plt.xticks(rotation=45)
st.pyplot(fig3)

# ------------------ PRICE DISTRIBUTION ------------------
st.subheader("💡 Price Distribution")
st.bar_chart(df["Price Category"].value_counts())

# ------------------ UNSOLD ANALYSIS ------------------
st.subheader("❌ Unsold Players Analysis")

unsold = df[df["Status"] == "Unsold"]

st.write(f"Total Unsold Players: {len(unsold)}")
st.dataframe(unsold.head(20), width="stretch")

# ------------------ SMART INSIGHTS ------------------
st.subheader("🧠 Key Insights")

# ✅ Safety checks (avoid crash if empty)
most_spent_team = team_spending.idxmax() if not team_spending.empty else "N/A"
least_spent_team = team_spending.idxmin() if not team_spending.empty else "N/A"
highest_type = type_spending.idxmax() if not type_spending.empty else "N/A"

st.markdown(f"""
- 🏆 **Highest Spending Team:** {most_spent_team}  
- 📉 **Lowest Spending Team:** {least_spent_team}  
- 💰 **Most Expensive Player Type:** {highest_type}  
- ❌ **Unsold Players:** {len(unsold)}  
- 📊 **Market Insight:** High number of unsold players suggests oversupply  
- 🔥 **Trend:** Teams prefer multi-role players (All-rounders dominate spending)  
""")

# ------------------ FOOTER ------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Advanced IPL Data Analysis Project")