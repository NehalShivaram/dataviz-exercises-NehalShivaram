# Dataviz Exercises

Weekly data visualization exercises using Plotly and Streamlit.

## 🌱 Lecture 10 — CO2 Emissions Dashboard

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dataviz-exercises-nehalshivaram-6feh7eayfx5fnoojyspehj.streamlit.app)

**Live app:** https://dataviz-exercises-nehalshivaram-6feh7eayfx5fnoojyspehj.streamlit.app

An interactive dashboard exploring CO2 emissions by country and region, built with Streamlit and Plotly. Features:
- Region and country filters (chained)
- Adjustable date range
- Toggle between total CO2 (Mt) and CO2 per capita
- Line chart with a "highlight top emitter" mode
- Ranked bar chart for the most recent year in range
- KPI summary row (totals, % change, top emitter)

### Run locally
```bash
pip install -r requirements.txt
streamlit run week10/week10/lecture10_exercise.py
```

## 🗺️ Lecture 8 — Choropleth Maps

A notebook covering world choropleth maps with `plotly.express`:
- **Task 1:** Life expectancy vs. global average (2007 Gapminder data), diverging color scale
- **Task 2:** Custom GeoJSON choropleth — US population density by state, sequential color scale

### Run locally
```bash
pip install plotly pandas
jupyter notebook week08/lecture08_exercise.ipynb
```

## Repo structure
```
├── week08/
│   └── lecture08_exercise.ipynb
├── week10/
│   └── week10/
│       ├── lecture10_exercise.py
│       ├── data/
│       │   └── co2_emissions.csv
│       └── requirements.txt
└── README.md
```

## Requirements
- Python 3.10+
- streamlit
- pandas
- plotly
