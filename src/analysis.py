"""
Statistical analysis module
"""

import logging
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple, List
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)


class RepositoryAnalyzer:
    """Performs statistical analysis on repository data"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.results = {}
    
    def analyze_correlations(self) -> Dict:
        """
        Calculate correlations between key metrics
        """
        numeric_cols = ['stars', 'forks', 'watchers', 'open_issues', 'engagement_score']
        numeric_cols = [col for col in numeric_cols if col in self.df.columns]
        
        correlation_matrix = self.df[numeric_cols].corr()
        
        # Find strongest correlations
        corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr = correlation_matrix.iloc[i, j]
                col1 = correlation_matrix.columns[i]
                col2 = correlation_matrix.columns[j]
                corr_pairs.append({
                    'variable_1': col1,
                    'variable_2': col2,
                    'correlation': corr,
                    'abs_correlation': abs(corr)
                })
        
        corr_df = pd.DataFrame(corr_pairs).sort_values('abs_correlation', ascending=False)
        
        self.results['correlations'] = {
            'matrix': correlation_matrix,
            'top_pairs': corr_df.head(10),
            'full_pairs': corr_df
        }
        
        logger.info("✓ Correlation analysis complete")
        return self.results['correlations']
    
    def analyze_languages(self) -> pd.DataFrame:
        """
        Analyze programming languages statistics
        """
        language_stats = self.df.groupby('language').agg({
            'stars': ['mean', 'median', 'max', 'count'],
            'forks': 'mean',
            'engagement_score': 'mean',
            'watchers': 'mean'
        }).round(2)
        
        language_stats.columns = ['avg_stars', 'median_stars', 'max_stars', 'count',
                                  'avg_forks', 'avg_engagement', 'avg_watchers']
        language_stats = language_stats.sort_values('avg_stars', ascending=False)
        
        self.results['language_analysis'] = language_stats
        logger.info("✓ Language analysis complete")
        return language_stats
    
    def analyze_licenses(self) -> pd.DataFrame:
        """
        Analyze license distribution and impact
        """
        license_stats = self.df.groupby('license').agg({
            'stars': ['mean', 'count'],
            'forks': 'mean',
            'full_name': 'count'
        }).round(2)
        
        license_stats.columns = ['avg_stars', 'repo_count', 'avg_forks', 'total_repos']
        license_stats = license_stats.sort_values('avg_stars', ascending=False)
        license_stats = license_stats[license_stats['repo_count'] >= 5]  # Filter small groups
        
        self.results['license_analysis'] = license_stats
        logger.info("✓ License analysis complete")
        return license_stats
    
    def analyze_topics(self) -> Dict:
        """
        Analyze popular topics and their impact
        """
        # Explode topics and analyze
        topics_list = []
        for topics_str in self.df['topics'].dropna():
            if topics_str and topics_str != 'No topics':
                topics = [t.strip() for t in str(topics_str).split(',')]
                topics_list.extend(topics)
        
        topic_counts = pd.Series(topics_list).value_counts().head(20)
        
        self.results['top_topics'] = topic_counts
        logger.info(f"✓ Topic analysis complete - Found {len(topic_counts)} topics")
        return {'top_topics': topic_counts}
    
    def statistical_tests(self) -> Dict:
        """
        Perform statistical hypothesis tests
        """
        test_results = {}
        
        # Test 1: Are dynamic languages more popular?
        if 'language_category' in self.df.columns:
            dynamic = self.df[self.df['language_category'] == 'Dynamic']['stars']
            static = self.df[self.df['language_category'] == 'Static']['stars']
            
            t_stat, p_value = stats.ttest_ind(dynamic.dropna(), static.dropna())
            test_results['dynamic_vs_static'] = {
                'test': 't-test',
                'statistic': round(t_stat, 4),
                'p_value': round(p_value, 6),
                'significant': p_value < 0.05,
                'dynamic_mean_stars': round(dynamic.mean(), 2),
                'static_mean_stars': round(static.mean(), 2)
            }
        
        # Test 2: ANOVA - Do different licenses have different star counts?
        if 'license' in self.df.columns:
            license_groups = [group['stars'].dropna().values 
                            for name, group in self.df.groupby('license') 
                            if len(group) >= 5]
            
            if len(license_groups) > 2:
                f_stat, p_value = stats.f_oneway(*license_groups)
                test_results['license_impact'] = {
                    'test': 'ANOVA',
                    'statistic': round(f_stat, 4),
                    'p_value': round(p_value, 6),
                    'significant': p_value < 0.05
                }
        
        self.results['statistical_tests'] = test_results
        logger.info("✓ Statistical tests complete")
        return test_results
    
    def get_summary_statistics(self) -> Dict:
        """
        Get summary statistics for key metrics
        """
        summary = {}
        
        for col in ['stars', 'forks', 'watchers', 'open_issues']:
            if col in self.df.columns:
                summary[col] = {
                    'mean': round(self.df[col].mean(), 2),
                    'median': round(self.df[col].median(), 2),
                    'std': round(self.df[col].std(), 2),
                    'min': int(self.df[col].min()),
                    'max': int(self.df[col].max()),
                    'q1': round(self.df[col].quantile(0.25), 2),
                    'q3': round(self.df[col].quantile(0.75), 2)
                }
        
        self.results['summary_statistics'] = summary
        logger.info("✓ Summary statistics calculated")
        return summary
    
    def generate_report(self) -> Dict:
        """
        Generate comprehensive analysis report
        """
        logger.info("Generating comprehensive report...")
        
        # Run all analyses
        self.get_summary_statistics()
        self.analyze_correlations()
        self.analyze_languages()
        self.analyze_licenses()
        self.analyze_topics()
        self.statistical_tests()
        
        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'total_repositories': len(self.df),
            'results': self.results
        }
        
        logger.info("✓ Report generation complete")
        return report


def create_visualizations(df: pd.DataFrame, output_dir: str = "visualizations"):
    """
    Create static visualizations for analysis
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 6)
    
    # Plot 1: Top Languages by Average Stars
    if 'language' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        lang_stats = df.groupby('language')['stars'].mean().sort_values(ascending=False).head(10)
        lang_stats.plot(kind='barh', ax=ax, color='steelblue')
        ax.set_xlabel('Average Stars')
        ax.set_title('Top 10 Languages by Average Stars')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/languages_by_stars.png", dpi=300)
        plt.close()
    
    # Plot 2: Stars vs Forks Scatter
    if 'stars' in df.columns and 'forks' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(df['stars'], df['forks'], alpha=0.5, s=50, color='coral')
        ax.set_xlabel('Stars')
        ax.set_ylabel('Forks')
        ax.set_title('Repository Stars vs Forks')
        ax.set_xscale('log')
        ax.set_yscale('log')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/stars_vs_forks.png", dpi=300)
        plt.close()
    
    # Plot 3: Activity Level Distribution
    if 'activity_level' in df.columns:
        fig, ax = plt.subplots(figsize=(8, 6))
        activity_counts = df['activity_level'].value_counts()
        activity_counts.plot(kind='bar', ax=ax, color=['green', 'orange', 'red'])
        ax.set_ylabel('Count')
        ax.set_title('Repository Activity Level Distribution')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/activity_distribution.png", dpi=300)
        plt.close()
    
    logger.info(f"Visualizations saved to {output_dir}")
