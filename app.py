import streamlit as st
import pandas as pd
import plotly.express as px
import glob
# v2

st.set_page_config(page_title="ESADE Sustainable Finance", page_icon="🌱", layout="wide")
st.title("🌱 ESADE Sustainable Finance Dashboard")
st.success("App is running successfully!")

# Load portfolio
files = sorted(glob.glob("outputs/portfolio/final_portfolio_*.csv"))
if files:
    df = pd.read_csv(files[-1])
    st.subheader(f"Portfolio — {len(df)} holdings")
    st.dataframe(df, use_container_width=True)
    fig = px.pie(df, names="ticker", values="weight", title="Portfolio Weights")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No portfolio data found.")
