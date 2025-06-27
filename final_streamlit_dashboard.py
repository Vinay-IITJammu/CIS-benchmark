
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
import datetime

st.set_page_config(page_title="CIS Benchmark Dashboard", layout="wide")

# Header
st.markdown("### Created by **Group 2, PGDCS-2, IIT Jammu**")
st.title("🛡️ CIS Benchmark Violation Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("simulated_cis_control_violations.csv")
    np.random.seed(42)
    timestamps = pd.date_range(datetime.datetime.now() - datetime.timedelta(days=30), periods=len(df), freq='H')
    df['timestamp'] = np.random.choice(timestamps, size=len(df))
    return df

df = load_data()

# Organize control names into mock categories (as real categories are unavailable)
categories = {
    "Authentication": ["Enforce MFA for User Sign-in", "Configure Account Lockout Policy", "Enforce Device Passcode", "Require Face ID or Touch ID for Unlock"],
    "Network Security": ["Enable Windows Defender Firewall", "Disable SMBv1 Protocol", "Disable USB Debugging", "Disable Siri on Lock Screen"],
    "Application Control": ["Disable Unknown Sources for App Installation", "Block Installation of Unapproved Apps", "Disable Password Manager", "Disable Autofill for Forms", "Disable Autofill for Payment Methods", "Disable Autofill Address Profile"],
    "Privacy & Data Protection": ["Disable USB Restricted Mode (allow USB only when unlocked)", "Enable Google Safe Browsing", "Enable Microsoft Defender SmartScreen"],
    "System Hardening": ["Ensure Windows Defender Antivirus is Enabled", "Enable Safe Browsing Protection", "Enforce Auto-Lock Time", "Enforce Screen Lock Timeout"]
}

flat_controls = [item for sublist in categories.values() for item in sublist]
available_controls = [ctrl for ctrl in df["control_name"].unique() if ctrl in flat_controls]

# Sidebar Filters
with st.sidebar:
    st.markdown("### Created by **Group 2, PGDCS-2, IIT Jammu**")
    st.title("⚙️ Filters")

    os_types = df['os_type'].unique().tolist()
    if st.button("Clear All OS"):
        selected_os = []
    elif st.button("Select All OS"):
        selected_os = os_types
    else:
        selected_os = st.multiselect("Operating System", options=os_types, default=os_types)

    st.markdown("---")
    st.subheader("📌 Control Filters")

    selected_controls = []
    for category, controls in categories.items():
        with st.expander(category, expanded=True):
            if st.button(f"Clear {category}", key=f"clear_{category}"):
                selected = []
            elif st.button(f"Select All {category}", key=f"select_{category}"):
                selected = controls
            else:
                selected = st.multiselect(f"{category} Controls", options=controls, default=controls, key=category)
            selected_controls.extend(selected)

    st.markdown("---")
    sort_order = st.selectbox("Sort Order", options=["Descending", "Ascending"])
    top_n = st.slider("Top N Controls", min_value=5, max_value=30, value=10)
    date_range = st.date_input("Date Range", [df['timestamp'].min(), df['timestamp'].max()])
    show_data = st.checkbox("Show Raw Data Table", value=False)

# Apply filters
df_filtered = df[
    (df['os_type'].isin(selected_os)) &
    (df['control_name'].isin(selected_controls)) &
    (df['timestamp'].dt.date >= date_range[0]) &
    (df['timestamp'].dt.date <= date_range[1])
]

# TABS
tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary Charts", "🔥 Heatmaps", "📈 Trend Analysis", "🧾 Raw Data & Export"])

with tab1:
    st.header("🔍 Violation Overview")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Violations by OS Type")
        os_counts = df_filtered['os_type'].value_counts()
        fig1, ax1 = plt.subplots()
        sns.barplot(x=os_counts.index, y=os_counts.values, ax=ax1)
        ax1.set_ylabel("Violation Count")
        ax1.set_xlabel("OS")
        st.pyplot(fig1)

    with col2:
        st.subheader(f"Top {top_n} Violated Controls")
        control_counts = df_filtered['control_name'].value_counts().head(top_n)
        if sort_order == "Ascending":
            control_counts = control_counts.sort_values()
        fig2, ax2 = plt.subplots()
        sns.barplot(x=control_counts.values, y=control_counts.index, ax=ax2)
        ax2.set_xlabel("Violation Count")
        ax2.set_ylabel("Control")
        st.pyplot(fig2)

with tab2:
    st.header("🔥 Heatmap of Violations")
    heatmap_data = df_filtered.groupby(['os_type', 'control_name']).size().unstack(fill_value=0)
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    sns.heatmap(heatmap_data, cmap="YlGnBu", annot=True, fmt="d", ax=ax3)
    ax3.set_title("Violation Heatmap by OS and Control")
    st.pyplot(fig3)

with tab3:
    st.header("📈 Trend Analysis")
    trend = df_filtered.groupby(df_filtered['timestamp'].dt.date).size().reset_index(name="violations")
    fig4 = px.line(trend, x='timestamp', y='violations', title="Violations Over Time")
    st.plotly_chart(fig4, use_container_width=True)

with tab4:
    st.header("🧾 Raw Data Viewer & Export")
    if show_data:
        st.dataframe(df_filtered)
    st.download_button(
        label="📥 Download Filtered Data",
        data=df_filtered.to_csv(index=False),
        file_name="filtered_violations.csv",
        mime="text/csv"
    )
