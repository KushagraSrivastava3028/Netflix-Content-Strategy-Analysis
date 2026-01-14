import argparse
import os
import sys
from textwrap import dedent

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# default template
pio.templates.default = "plotly_white"

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV file not found: {path}")
    df = pd.read_csv(path)
    return df


def clean_hours(df, col='Hours Viewed'):
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found in dataframe. Available cols: {df.columns.tolist()}")
    # remove commas, strip spaces, coerce to numeric
    df[col] = df[col].astype(str).str.replace(',', '').str.strip()
    df[col] = pd.to_numeric(df[col], errors='coerce')
    num_missing = df[col].isna().sum()
    if num_missing:
        print(f"Warning: {num_missing} rows have NaN for '{col}' after cleaning.")
    return df


def prepare_dates(df, date_col='Release Date'):
    if date_col not in df.columns:
        raise KeyError(f"Column '{date_col}' not found in dataframe. Available cols: {df.columns.tolist()}")
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    missing_dates = df[date_col].isna().sum()
    if missing_dates:
        print(f"Warning: {missing_dates} rows have invalid or missing dates in '{date_col}'.")
    df['Release Month'] = df[date_col].dt.month
    df['Release Day'] = df[date_col].dt.day_name()
    df['Release Year'] = df[date_col].dt.year
    return df


def get_season(month):
    if pd.isna(month):
        return None
    month = int(month)
    if month in [12, 1, 2]:
        return 'Winter'
    if month in [3, 4, 5]:
        return 'Spring'
    if month in [6, 7, 8]:
        return 'Summer'
    return 'Fall'


def save_fig(fig, name):
    path = os.path.join(OUTPUT_DIR, name + '.html')
    fig.write_html(path, include_plotlyjs='cdn')
    print(f"Saved interactive plot: {path}")


def plot_viewership_by_content_type(df):
    if 'Content Type' not in df.columns:
        print("Skipping content type plot: 'Content Type' column missing.")
        return
    agg = df.groupby('Content Type')['Hours Viewed'].sum().sort_values(ascending=False)
    fig = go.Figure(data=[go.Bar(x=agg.index, y=agg.values, marker_color=['skyblue' for _ in agg.index])])
    fig.update_layout(title='Total Viewership Hours by Content Type', xaxis_title='Content Type', yaxis_title='Total Hours Viewed')
    save_fig(fig, 'viewership_by_content_type')


def plot_viewership_by_language(df, lang_col='Language Indicator'):
    if lang_col not in df.columns:
        print(f"Skipping language plot: '{lang_col}' column missing.")
        return
    agg = df.groupby(lang_col)['Hours Viewed'].sum().sort_values(ascending=False)
    fig = go.Figure(data=[go.Bar(x=agg.index, y=agg.values)])
    fig.update_layout(title='Total Viewership Hours by Language', xaxis_title='Language', yaxis_title='Total Hours Viewed')
    save_fig(fig, 'viewership_by_language')


def plot_monthly_viewership(df):
    if 'Release Month' not in df.columns:
        print("Skipping monthly viewership: 'Release Month' missing.")
        return
    monthly = df.groupby('Release Month')['Hours Viewed'].sum().reindex(range(1,13), fill_value=0)
    fig = go.Figure(data=[go.Scatter(x=monthly.index, y=monthly.values, mode='lines+markers')])
    fig.update_layout(title='Total Viewership Hours by Release Month', xaxis_title='Month', yaxis_title='Total Hours Viewed')
    save_fig(fig, 'monthly_viewership')


def plot_viewership_by_type_and_month(df):
    if 'Content Type' not in df.columns:
        print("Skipping monthly by type: 'Content Type' missing.")
        return
    pivot = df.pivot_table(index='Release Month', columns='Content Type', values='Hours Viewed', aggfunc='sum').reindex(range(1,13)).fillna(0)
    fig = go.Figure()
    for col in pivot.columns:
        fig.add_trace(go.Scatter(x=pivot.index, y=pivot[col], mode='lines+markers', name=col))
    fig.update_layout(title='Viewership Trends by Content Type and Release Month', xaxis_title='Month', yaxis_title='Total Hours Viewed')
    save_fig(fig, 'monthly_viewership_by_type')


def plot_seasonal_viewership(df):
    if 'Release Month' not in df.columns:
        print("Skipping seasonal viewership: 'Release Month' missing.")
        return
    df['Release Season'] = df['Release Month'].apply(get_season)
    agg = df.groupby('Release Season')['Hours Viewed'].sum()
    seasons_order = ['Winter', 'Spring', 'Summer', 'Fall']
    agg = agg.reindex(seasons_order).fillna(0)
    fig = go.Figure(data=[go.Bar(x=agg.index, y=agg.values)])
    fig.update_layout(title='Total Viewership Hours by Release Season', xaxis_title='Season', yaxis_title='Total Hours Viewed')
    save_fig(fig, 'seasonal_viewership')


def monthly_releases_and_viewership(df):
    monthly_releases = df['Release Month'].value_counts().sort_index().reindex(range(1,13), fill_value=0)
    monthly_viewership = df.groupby('Release Month')['Hours Viewed'].sum().reindex(range(1,13), fill_value=0)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_releases.index, y=monthly_releases.values, name='Number of Releases', opacity=0.7))
    fig.add_trace(go.Scatter(x=monthly_viewership.index, y=monthly_viewership.values, name='Viewership Hours', mode='lines+markers'))
    fig.update_layout(title='Monthly Release Patterns and Viewership Hours', xaxis_title='Month')
    save_fig(fig, 'monthly_releases_and_viewership')


def weekday_release_patterns(df):
    if 'Release Day' not in df.columns:
        print("Skipping weekday patterns: 'Release Day' missing.")
        return
    order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    releases = df['Release Day'].value_counts().reindex(order).fillna(0)
    viewership = df.groupby('Release Day')['Hours Viewed'].sum().reindex(order).fillna(0)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=releases.index, y=releases.values, name='Number of Releases'))
    fig.add_trace(go.Scatter(x=viewership.index, y=viewership.values, name='Viewership Hours', mode='lines+markers'))
    fig.update_layout(title='Weekly Release Patterns and Viewership Hours', xaxis_title='Day of Week')
    save_fig(fig, 'weekday_release_patterns')


def holiday_release_analysis(df, important_dates=None, window_days=3):
    if important_dates is None:
        important_dates = ['2023-01-01','2023-02-14','2023-07-04','2023-10-31','2023-12-25']
    important_dates = pd.to_datetime(important_dates)
    if 'Release Date' not in df.columns:
        print("Skipping holiday analysis: 'Release Date' missing.")
        return pd.DataFrame()
    mask = df['Release Date'].apply(lambda x: any(abs((x - d).days) <= window_days for d in important_dates) if pd.notna(x) else False)
    holiday_releases = df[mask].copy()
    if holiday_releases.empty:
        print("No releases found within the specified windows around important dates.")
        return holiday_releases
    out_path = os.path.join(OUTPUT_DIR, 'holiday_releases.csv')
    holiday_releases.to_csv(out_path, index=False)
    print(f"Saved holiday releases table: {out_path}")
    return holiday_releases


def print_top_titles(df, n=10):
    if 'Hours Viewed' not in df.columns:
        print("'Hours Viewed' column missing. Cannot compute top titles.")
        return
    top = df.nlargest(n, 'Hours Viewed')
    cols = [c for c in ['Title','Hours Viewed','Language Indicator','Content Type','Release Date'] if c in top.columns]
    print('\nTop titles:')
    print(top[cols].to_string(index=False))


def run_dashboard(args):
    st.title("Netflix Content Strategy Analysis Dashboard")

    try:
        df = load_data(args.file)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    st.write(f"Loaded data: {len(df)} rows, {len(df.columns)} columns")

    # clean
    df = clean_hours(df, col=args.hours_col)
    df = prepare_dates(df, date_col=args.date_col)

    # quick summary
    st.subheader("Data Summary")
    st.write("Columns available:", df.columns.tolist())

    # plots and outputs
    st.subheader("Viewership by Content Type")
    if 'Content Type' in df.columns:
        agg = df.groupby('Content Type')['Hours Viewed'].sum().sort_values(ascending=False)
        fig = go.Figure(data=[go.Bar(x=agg.index, y=agg.values, marker_color=['skyblue' for _ in agg.index])])
        fig.update_layout(title='Total Viewership Hours by Content Type', xaxis_title='Content Type', yaxis_title='Total Hours Viewed')
        st.plotly_chart(fig)
    else:
        st.write("Content Type column missing.")

    st.subheader("Viewership by Language")
    if args.language_col in df.columns:
        agg = df.groupby(args.language_col)['Hours Viewed'].sum().sort_values(ascending=False)
        fig = go.Figure(data=[go.Bar(x=agg.index, y=agg.values)])
        fig.update_layout(title='Total Viewership Hours by Language', xaxis_title='Language', yaxis_title='Total Hours Viewed')
        st.plotly_chart(fig)
    else:
        st.write(f"{args.language_col} column missing.")

    st.subheader("Monthly Viewership")
    if 'Release Month' in df.columns:
        monthly = df.groupby('Release Month')['Hours Viewed'].sum().reindex(range(1,13), fill_value=0)
        fig = go.Figure(data=[go.Scatter(x=monthly.index, y=monthly.values, mode='lines+markers')])
        fig.update_layout(title='Total Viewership Hours by Release Month', xaxis_title='Month', yaxis_title='Total Hours Viewed')
        st.plotly_chart(fig)
    else:
        st.write("Release Month column missing.")

    st.subheader("Viewership Trends by Content Type and Month")
    if 'Content Type' in df.columns:
        pivot = df.pivot_table(index='Release Month', columns='Content Type', values='Hours Viewed', aggfunc='sum').reindex(range(1,13)).fillna(0)
        fig = go.Figure()
        for col in pivot.columns:
            fig.add_trace(go.Scatter(x=pivot.index, y=pivot[col], mode='lines+markers', name=col))
        fig.update_layout(title='Viewership Trends by Content Type and Release Month', xaxis_title='Month', yaxis_title='Total Hours Viewed')
        st.plotly_chart(fig)
    else:
        st.write("Content Type column missing.")

    st.subheader("Seasonal Viewership")
    if 'Release Month' in df.columns:
        df['Release Season'] = df['Release Month'].apply(get_season)
        agg = df.groupby('Release Season')['Hours Viewed'].sum()
        seasons_order = ['Winter', 'Spring', 'Summer', 'Fall']
        agg = agg.reindex(seasons_order).fillna(0)
        fig = go.Figure(data=[go.Bar(x=agg.index, y=agg.values)])
        fig.update_layout(title='Total Viewership Hours by Release Season', xaxis_title='Season', yaxis_title='Total Hours Viewed')
        st.plotly_chart(fig)
    else:
        st.write("Release Month column missing.")

    st.subheader("Monthly Release Patterns and Viewership")
    monthly_releases = df['Release Month'].value_counts().sort_index().reindex(range(1,13), fill_value=0)
    monthly_viewership = df.groupby('Release Month')['Hours Viewed'].sum().reindex(range(1,13), fill_value=0)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_releases.index, y=monthly_releases.values, name='Number of Releases', opacity=0.7))
    fig.add_trace(go.Scatter(x=monthly_viewership.index, y=monthly_viewership.values, name='Viewership Hours', mode='lines+markers'))
    fig.update_layout(title='Monthly Release Patterns and Viewership Hours', xaxis_title='Month')
    st.plotly_chart(fig)

    st.subheader("Weekly Release Patterns and Viewership")
    if 'Release Day' in df.columns:
        order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        releases = df['Release Day'].value_counts().reindex(order).fillna(0)
        viewership = df.groupby('Release Day')['Hours Viewed'].sum().reindex(order).fillna(0)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=releases.index, y=releases.values, name='Number of Releases'))
        fig.add_trace(go.Scatter(x=viewership.index, y=viewership.values, name='Viewership Hours', mode='lines+markers'))
        fig.update_layout(title='Weekly Release Patterns and Viewership Hours', xaxis_title='Day of Week')
        st.plotly_chart(fig)
    else:
        st.write("Release Day column missing.")

    st.subheader("Top Titles")
    if 'Hours Viewed' in df.columns:
        top = df.nlargest(args.top_n, 'Hours Viewed')
        cols = [c for c in ['Title','Hours Viewed','Language Indicator','Content Type','Release Date'] if c in top.columns]
        st.dataframe(top[cols])
    else:
        st.write("'Hours Viewed' column missing.")

    holiday_releases = holiday_release_analysis(df)
    if not holiday_releases.empty:
        st.subheader("Holiday Releases")
        st.dataframe(holiday_releases)


def main(args):
    try:
        df = load_data(args.file)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

    print(f"Loaded data: {len(df)} rows, {len(df.columns)} columns")

    # clean
    df = clean_hours(df, col=args.hours_col)
    df = prepare_dates(df, date_col=args.date_col)

    # quick summary
    print('\nColumns available:', df.columns.tolist())

    # plots and outputs
    plot_viewership_by_content_type(df)
    plot_viewership_by_language(df, lang_col=args.language_col)
    plot_monthly_viewership(df)
    plot_viewership_by_type_and_month(df)
    plot_seasonal_viewership(df)
    monthly_releases_and_viewership(df)
    weekday_release_patterns(df)

    holiday_releases = holiday_release_analysis(df)

    print_top_titles(df, n=args.top_n)

    print('\nAll interactive plots and tables have been saved to the "outputs" folder.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Netflix Content Strategy Analysis')
    parser.add_argument('--file', type=str, default='netflix_content.csv', help='Path to the CSV file')
    parser.add_argument('--hours_col', type=str, default='Hours Viewed', help='Name of the Hours Viewed column')
    parser.add_argument('--date_col', type=str, default='Release Date', help='Name of the Release Date column')
    parser.add_argument('--language_col', type=str, default='Language Indicator', help='Name of the language column')
    parser.add_argument('--top_n', type=int, default=5, help='How many top titles to print')
    parser.add_argument('--web', action='store_true', help='Run the web dashboard instead of CLI analysis')
    args = parser.parse_args()
    if args.web:
        run_dashboard(args)
    else:
        main(args)
