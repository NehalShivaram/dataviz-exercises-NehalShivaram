
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="CO2 Dashboard", page_icon="🌱", layout="wide")

# ── Data ──────────────────────────────────────────────────────────────────────
# @st.cache_data: Streamlit reruns the entire script on every widget interaction.
# Without caching, the CSV is read from disk on every interaction — slow and wasteful.
# cache_data stores the result after the first run and reuses it until the file changes.
@st.cache_data
def load_data():
    here = Path(__file__).parent
    # Try a few likely locations so this works regardless of exact repo nesting
    candidates = [
        here / "data" / "co2_emissions.csv",
        here.parent / "data" / "co2_emissions.csv",
        here.parent.parent / "data" / "co2_emissions.csv",
        here / "co2_emissions.csv",
    ]
    for path in candidates:
        if path.exists():
            df = pd.read_csv(path)
            df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
            return df
    tried = "\n".join(f"- {c}" for c in candidates)
    st.error(f"Could not find co2_emissions.csv. Tried:\n{tried}")
    st.stop()

df = load_data()

st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")

# ── TASK 1: Sidebar with 5 widgets ────────────────────────────────────────────
#   a) st.selectbox for Region (with 'All')
#   b) st.multiselect for Countries (updates based on region — chained)
#   c) st.date_input for date range (two-handle; convert years to Jan-1 dates)
#   d) st.radio for Metric: "Total CO2 (Mt)" vs "CO2 per capita"
#   e) st.checkbox labelled "Show only top emitter highlighted"
#
# Guards:
#   - empty countries → st.warning + st.stop()
#   - incomplete date_input → st.warning + st.stop()
# Convert date_input result to pd.Timestamp before filtering.
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    # a) Region selectbox (with "All")
    regions = ["All"] + sorted(df["Region"].dropna().unique().tolist())
    selected_region = st.selectbox("Region", regions)

    # b) Country multiselect — chained: options depend on the region picked above
    region_df = df if selected_region == "All" else df[df["Region"] == selected_region]
    available_countries = sorted(region_df["Country"].unique().tolist())
    selected_countries = st.multiselect(
        "Countries", available_countries, default=available_countries[:5]
    )

    # c) Date range — two-handle date_input; years converted to Jan-1 dates
    min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
    date_range = st.date_input(
        "Date range",
        value=(pd.Timestamp(f"{min_year}-01-01"), pd.Timestamp(f"{max_year}-01-01")),
        min_value=pd.Timestamp(f"{min_year}-01-01"),
        max_value=pd.Timestamp(f"{max_year}-01-01"),
    )

    # d) Metric radio
    metric_label = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita"])
    metric_col = "CO2_Mt" if metric_label == "Total CO2 (Mt)" else "CO2_per_capita"

    # e) Highlight top emitter checkbox
    highlight_top = st.checkbox("Show only top emitter highlighted")

# Guards
if not selected_countries:
    st.warning("Select at least one country to continue.")
    st.stop()

if len(date_range) != 2:
    st.warning("Select a complete date range (start and end date).")
    st.stop()

start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])

filtered = df[
    (df["Country"].isin(selected_countries))
    & (df["Date"] >= start_date)
    & (df["Date"] <= end_date)
]


# ── TASK 2: Filter summary caption ────────────────────────────────────────────
# Show: "X countries | Region | Date range | Metric"
# BBD rule: always show users how many records match current filters
# ─────────────────────────────────────────────────────────────────────────────
st.caption(
    f"**{len(selected_countries)} countries** · "
    f"**{selected_region}** · "
    f"**{start_date.year}–{end_date.year}** · "
    f"**{metric_label}**"
)


# ── TASK 3: Two charts reacting to ALL filters ────────────────────────────────
#   Left: line chart — selected metric over time, one line per country
#         If "Show only top emitter highlighted" checkbox is on:
#           - grey all lines except the highest emitter in the date range
#           - label that country at the end of its line (SWD grey-and-highlight)
#   Right: bar chart — ranking for the last year in selected date range
#
# BBD colour requirement: name the colour type in a comment next to each chart
# SWD requirements: white background, insight title, use_container_width=True
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    # Line chart — colour: qualitative (one categorical hue per country)
    line_df = filtered.copy()

    if highlight_top:
        last_slice = line_df[line_df["Date"] == line_df["Date"].max()]
        top_country = last_slice.loc[last_slice[metric_col].idxmax(), "Country"]

        # Grey out everyone except the top emitter (SWD grey-and-highlight)
        color_map = {c: "#d9d9d9" for c in selected_countries if c != top_country}
        color_map[top_country] = "#e63946"

        fig_line = px.line(
            line_df, x="Date", y=metric_col, color="Country",
            color_discrete_map=color_map,
        )
        for trace in fig_line.data:
            trace.line.width = 4 if trace.name == top_country else 1.5

        # Label the highlighted country at the end of its line instead of a legend
        end_point = line_df[line_df["Country"] == top_country].sort_values("Date").iloc[-1]
        fig_line.add_annotation(
            x=end_point["Date"], y=end_point[metric_col],
            text=top_country, showarrow=False, xanchor="left", xshift=8,
            font=dict(color="#e63946", size=13),
        )
        fig_line.update_layout(showlegend=False)
        insight_title = f"{top_country} Leads Emissions Among Selected Countries"
    else:
        fig_line = px.line(line_df, x="Date", y=metric_col, color="Country")
        insight_title = f"{metric_label} Over Time by Country"

    fig_line.update_layout(
        title=insight_title,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=50, b=0),
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    # Bar chart — colour: sequential (encodes emissions magnitude, rank matters)
    last_year_df = filtered[filtered["Date"] == filtered["Date"].max()].sort_values(
        metric_col, ascending=True
    )
    top_emitter = last_year_df.iloc[-1]["Country"] if not last_year_df.empty else None
    last_year = int(filtered["Date"].max().year) if not filtered.empty else None

    fig_bar = px.bar(
        last_year_df, x=metric_col, y="Country", orientation="h",
        color=metric_col, color_continuous_scale="Reds",
    )
    fig_bar.update_layout(
        title=f"{top_emitter} Ranks Highest in {last_year}" if top_emitter else "Ranking",
        plot_bgcolor="white",
        paper_bgcolor="white",
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=50, b=0),
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ── EXTENSION: KPI row above the charts ───────────────────────────────────────
#   - Total CO2 in last year of selected range (sum across selected countries)
#   - % change from first to last year
#   - Country with highest emissions in last year
# ─────────────────────────────────────────────────────────────────────────────
# NOTE: placed here to match the template's section order. Move this block
# above `col_left, col_right = st.columns(...)` if you want it to render
# visually above the charts.
if not filtered.empty:
    kpi1, kpi2, kpi3 = st.columns(3)

    last_slice = filtered[filtered["Date"] == filtered["Date"].max()]
    first_slice = filtered[filtered["Date"] == filtered["Date"].min()]

    last_total = last_slice[metric_col].sum()
    first_total = first_slice[metric_col].sum()
    pct_change = ((last_total - first_total) / first_total * 100) if first_total else 0
    top_row = last_slice.sort_values(metric_col, ascending=False).iloc[0]

    kpi1.metric(f"Total {metric_label} ({int(filtered['Date'].max().year)})", f"{last_total:,.1f}")
    kpi2.metric("Change over range", f"{pct_change:+.1f}%")
    kpi3.metric("Top emitter", top_row["Country"])