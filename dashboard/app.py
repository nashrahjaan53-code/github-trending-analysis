"""
Interactive Streamlit Dashboard for GitHub Trending Repository Analysis
Run with: streamlit run dashboard/app.py
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.utils import DataManager
from src.analysis import RepositoryAnalyzer

# Page config
st.set_page_config(
    page_title="GitHub Trending Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding-top: 0rem; }
    h1 { color: #0d47a1; margin-bottom: 0.5rem; }
    h2 { color: #1565c0; margin-top: 2rem; margin-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load processed data"""
    try:
        data_manager = DataManager()
        df = data_manager.load_csv("github_trending_full_analysis.csv")
        return df
    except FileNotFoundError:
        st.error("Data not found. Please run main.py first to generate the data.")
        return None

# Title
st.title("📊 GitHub Trending Repository Analysis Dashboard")
st.markdown("*Advanced data analysis & machine learning insights into trending repositories*")

# Load data
df = load_data()
if df is None:
    st.stop()

# Sidebar filters
st.sidebar.header("🔧 Filters")
languages = df['language'].unique()
licenses = df['license'].unique()

selected_languages = st.sidebar.multiselect(
    "Programming Languages",
    options=languages,
    default=list(languages)[:min(3, len(languages))]
)

# Only set default licenses that actually exist in data
default_licenses = [l for l in ['MIT', 'Apache 2.0'] if l in licenses]
if not default_licenses:
    default_licenses = list(licenses)[:min(2, len(licenses))]

selected_licenses = st.sidebar.multiselect(
    "Licenses",
    options=licenses,
    default=default_licenses
)

# Apply filters
filtered_df = df[
    (df['language'].isin(selected_languages)) &
    (df['license'].isin(selected_licenses))
]

# Main content - Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Repositories",
        len(filtered_df),
        f"+{len(df) - len(filtered_df)} excluded by filters"
    )

with col2:
    st.metric(
        "Avg Stars",
        f"{filtered_df['stars'].mean():.0f}",
        f"Max: {filtered_df['stars'].max():.0f}"
    )

with col3:
    st.metric(
        "Avg Forks",
        f"{filtered_df['forks'].mean():.0f}",
        f"Max: {filtered_df['forks'].max():.0f}"
    )

with col4:
    st.metric(
        "Avg Watchers",
        f"{filtered_df['watchers'].mean():.0f}",
        f"Max: {filtered_df['watchers'].max():.0f}"
    )

st.divider()

# Tab 1: Overview
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Overview", "🔍 Analysis", "🤖 ML Insights", "🏆 Top Repos", "📋 Data Explorer"]
)

# TAB 1: OVERVIEW
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Top Languages
        st.subheader("Top Programming Languages")
        lang_data = filtered_df.groupby('language').agg({
            'stars': 'mean',
            'full_name': 'count'
        }).rename(columns={'full_name': 'count'}).sort_values('stars', ascending=False).head(10)
        
        fig = px.bar(
            lang_data.reset_index(),
            x='language',
            y='stars',
            color='count',
            title="Average Stars by Language",
            labels={'stars': 'Avg Stars', 'language': 'Language', 'count': 'Repo Count'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # License Distribution
        st.subheader("Repository Licenses")
        license_counts = filtered_df['license'].value_counts().head(8)
        fig = px.pie(
            values=license_counts.values,
            names=license_counts.index,
            title="License Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Stars vs Forks
    st.subheader("Repository Popularity: Stars vs Forks")
    fig = px.scatter(
        filtered_df.nlargest(50, 'stars'),
        x='stars',
        y='forks',
        size='watchers',
        color='language',
        hover_data=['repo_name', 'owner'],
        title="Top 50 Repositories: Stars vs Forks",
        labels={'stars': 'Stars', 'forks': 'Forks', 'watchers': 'Watchers'}
    )
    fig.update_layout(hovermode='closest')
    st.plotly_chart(fig, use_container_width=True)

# TAB 2: STATISTICAL ANALYSIS
with tab2:
    st.subheader("Statistical Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Summary statistics
        st.write("**Key Metrics Distribution**")
        metrics_summary = {
            'Metric': ['Stars', 'Forks', 'Watchers', 'Open Issues'],
            'Mean': [
                f"{filtered_df['stars'].mean():.0f}",
                f"{filtered_df['forks'].mean():.0f}",
                f"{filtered_df['watchers'].mean():.0f}",
                f"{filtered_df['open_issues'].mean():.1f}"
            ],
            'Median': [
                f"{filtered_df['stars'].median():.0f}",
                f"{filtered_df['forks'].median():.0f}",
                f"{filtered_df['watchers'].median():.0f}",
                f"{filtered_df['open_issues'].median():.1f}"
            ],
            'Max': [
                f"{filtered_df['stars'].max():.0f}",
                f"{filtered_df['forks'].max():.0f}",
                f"{filtered_df['watchers'].max():.0f}",
                f"{filtered_df['open_issues'].max():.0f}"
            ]
        }
        st.dataframe(pd.DataFrame(metrics_summary), use_container_width=True)
    
    with col2:
        # Correlation heatmap
        st.write("**Metric Correlations**")
        numeric_cols = ['stars', 'forks', 'watchers', 'open_issues']
        corr_matrix = filtered_df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            labels=dict(color="Correlation"),
            title="Correlation Matrix",
            color_continuous_scale="RdBu",
            zmin=-1, zmax=1
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Distribution plots
    st.write("**Metric Distributions**")
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(
            filtered_df,
            x='stars',
            nbins=30,
            title="Stars Distribution",
            color_discrete_sequence=['#636EFA']
        )
        fig.update_xaxes(type='log', title='Stars (log scale)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.histogram(
            filtered_df,
            x='forks',
            nbins=30,
            title="Forks Distribution",
            color_discrete_sequence=['#EF553B']
        )
        fig.update_xaxes(type='log', title='Forks (log scale)')
        st.plotly_chart(fig, use_container_width=True)

# TAB 3: ML INSIGHTS
with tab3:
    st.subheader("Machine Learning Insights")
    
    if 'cluster' in filtered_df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Cluster distribution
            cluster_counts = filtered_df['cluster'].value_counts().sort_index()
            fig = px.bar(
                x=cluster_counts.index,
                y=cluster_counts.values,
                title="Repository Clusters",
                labels={'x': 'Cluster', 'y': 'Count'},
                color=cluster_counts.values,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Success probability distribution
            st.write("**Repository Success Probability**")
            if 'success_probability' in filtered_df.columns:
                fig = px.histogram(
                    filtered_df,
                    x='success_probability',
                    nbins=20,
                    title="Success Probability Distribution",
                    color_discrete_sequence=['#00CC96']
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Cluster characteristics
        st.write("**Cluster Characteristics**")
        cluster_analysis = filtered_df.groupby('cluster').agg({
            'stars': 'mean',
            'forks': 'mean',
            'watchers': 'mean',
            'language': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown',
            'full_name': 'count'
        }).rename(columns={'full_name': 'count'})
        cluster_analysis.columns = ['Avg Stars', 'Avg Forks', 'Avg Watchers', 'Top Language', 'Count']
        cluster_analysis.index.name = 'Cluster'
        st.dataframe(cluster_analysis, use_container_width=True)

# TAB 4: TOP REPOSITORIES
with tab4:
    st.subheader("🏆 Top Repositories")
    
    sort_by = st.selectbox(
        "Sort by:",
        ["Stars", "Forks", "Watchers", "Engagement Score"]
    )
    
    sort_col = {
        "Stars": "stars",
        "Forks": "forks",
        "Watchers": "watchers",
        "Engagement Score": "engagement_score"
    }[sort_by]
    
    top_n = st.slider("Number of repositories to show:", 5, 30, 10)
    
    top_repos = filtered_df.nlargest(top_n, sort_col)[
        ['full_name', 'description', 'language', 'stars', 'forks', 'watchers']
    ].copy()
    
    top_repos.columns = ['Repository', 'Description', 'Language', 'Stars', 'Forks', 'Watchers']
    
    # Make links clickable
    def make_clickable(url):
        return f'<a href="https://github.com/{url}" target="_blank">{url}</a>'
    
    st.dataframe(
        top_repos.style.format({
            'Stars': '{:.0f}',
            'Forks': '{:.0f}',
            'Watchers': '{:.0f}'
        }),
        use_container_width=True,
        hide_index=True
    )

# TAB 5: DATA EXPLORER
with tab5:
    st.subheader("📋 Full Dataset Explorer")
    
    # Display options
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input("Search repositories:", placeholder="Search by name or owner")
    
    with col2:
        sort_column = st.selectbox("Sort by:", ['stars', 'forks', 'watchers', 'full_name'])
    
    # Filter and sort
    display_df = filtered_df.copy()
    if search_term:
        display_df = display_df[
            (display_df['full_name'].str.contains(search_term, case=False, na=False)) |
            (display_df['description'].str.contains(search_term, case=False, na=False))
        ]
    
    display_df = display_df.sort_values(sort_column, ascending=False)
    
    st.dataframe(
        display_df[['full_name', 'description', 'language', 'stars', 'forks', 'watchers', 'license']],
        use_container_width=True,
        hide_index=True
    )

# Footer
st.divider()
st.markdown("""
**Portfolio Project: GitHub Trending Repository Analysis**  
*Built with Python, Pandas, Scikit-Learn, Plotly, and Streamlit*

[View on GitHub](https://github.com) | [Documentation](README.md)
""")
