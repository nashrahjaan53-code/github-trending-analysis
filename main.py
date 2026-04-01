"""
Main orchestration script for the GitHub Trending Analysis pipeline
Run this to execute the complete analysis workflow
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data_collection import collect_github_trending_data
from src.data_processing import process_github_data
from src.analysis import RepositoryAnalyzer, create_visualizations
from src.ml_models import ModelPipeline
from src.utils import DataManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Execute complete analysis pipeline"""
    
    print("\n" + "="*70)
    print("GitHub Trending Repository Analysis & Recommendation System")
    print("="*70 + "\n")
    
    data_manager = DataManager()
    
    # Step 1: Data Collection
    print("STEP 1: Collecting GitHub Trending Data")
    print("-" * 70)
    try:
        raw_data = collect_github_trending_data(
            languages=["python", "javascript", "java", "go", "rust", "typescript"],
            since="daily"
        )
        print(f"✓ Collected {len(raw_data)} repositories\n")
    except Exception as e:
        logger.error(f"Data collection failed: {str(e)}")
        print("⚠ Using sample data instead (you may need to install dependencies)")
        # Create sample data for demonstration
        import pandas as pd
        import numpy as np
        raw_data = create_sample_data()
    
    # Step 2: Data Processing
    print("STEP 2: Processing and Engineering Features")
    print("-" * 70)
    processed_data = process_github_data(raw_data)
    print(f"✓ Processed data shape: {processed_data.shape}\n")
    
    # Save processed data
    data_manager.save_csv(processed_data, "github_trending_processed.csv", subfolder="processed")
    
    # Step 3: Statistical Analysis
    print("STEP 3: Statistical Analysis")
    print("-" * 70)
    analyzer = RepositoryAnalyzer(processed_data)
    analysis_report = analyzer.generate_report()
    
    # Display key findings
    summary = analysis_report['results']['summary_statistics']
    print("\nKey Metrics Summary:")
    for metric, stats in summary.items():
        print(f"  {metric}: Mean={stats['mean']:.0f}, Median={stats['median']:.0f}, Max={stats['max']}")
    
    # Top correlations
    top_corr = analysis_report['results']['correlations']['top_pairs'].head(3)
    print("\nTop Correlations:")
    for _, row in top_corr.iterrows():
        print(f"  {row['variable_1']} ↔ {row['variable_2']}: {row['correlation']:.3f}")
    
    # Language analysis
    print("\nTop Languages by Average Stars:")
    lang_analysis = analysis_report['results']['language_analysis'].head(5)
    for lang, row in lang_analysis.iterrows():
        print(f"  {lang}: {row['avg_stars']:.0f} avg stars ({int(row['count'])} repos)")
    
    print()
    
    # Step 4: Machine Learning
    print("STEP 4: Machine Learning - Clustering & Prediction")
    print("-" * 70)
    pipeline = ModelPipeline(processed_data)
    ml_results = pipeline.run_full_pipeline()
    
    # Display cluster profiles
    print("\nRepository Clusters:")
    for cluster_name, profile in ml_results['cluster_profiles'].items():
        print(f"  {cluster_name}:")
        print(f"    - Size: {profile['size']} repositories")
        print(f"    - Avg Stars: {profile['avg_stars']:.0f}")
        print(f"    - Top Language: {profile['top_language']}")
        print(f"    - Type: {profile['description']}")
    
    # Display success prediction performance
    pred_perf = ml_results['predictor_performance']
    print(f"\nSuccess Prediction Model Performance:")
    print(f"  - Accuracy: {pred_perf['accuracy']:.3f}")
    print(f"  - AUC-ROC: {pred_perf['auc_roc']:.3f}")
    print(f"  - Model: {pred_perf['model_type']}")
    
    # Feature importance
    print(f"\nTop Features for Repository Success:")
    feature_imp = ml_results['feature_importance']
    for feat, imp in list(feature_imp.items())[:5]:
        print(f"  - {feat}: {imp:.3f}")
    
    print()
    
    # Step 5: Save Results
    print("STEP 5: Saving Results")
    print("-" * 70)
    
    # Save enhanced data
    enhanced_data = pipeline.df
    data_manager.save_csv(enhanced_data, "github_trending_full_analysis.csv", subfolder="processed")
    print("✓ Saved full analysis data")
    
    # Save models
    data_manager.save_model(pipeline.clustering, "clustering_model.pkl")
    data_manager.save_model(pipeline.predictor, "success_predictor_model.pkl")
    print("✓ Saved ML models")
    
    # Create visualizations
    try:
        create_visualizations(processed_data)
        print("✓ Created visualizations")
    except Exception as e:
        logger.warning(f"Visualization creation failed: {str(e)}")
    
    print()
    
    # Final Summary
    print("="*70)
    print("✅ Analysis Complete!")
    print("="*70)
    print(f"\n📊 Results saved to:")
    print(f"   - data/processed/github_trending_processed.csv")
    print(f"   - data/processed/github_trending_full_analysis.csv")
    print(f"   - data/models/clustering_model.pkl")
    print(f"   - data/models/success_predictor_model.pkl")
    print(f"\n📈 To view interactive dashboard, run:")
    print(f"   streamlit run dashboard/app.py")
    print(f"\n📝 Repository Statistics:")
    print(f"   - Total repositories analyzed: {len(processed_data)}")
    print(f"   - Languages covered: {processed_data['language'].nunique()}")
    print(f"   - Average stars: {processed_data['stars'].mean():.0f}")
    print(f"   - Average forks: {processed_data['forks'].mean():.0f}")
    print("\n")


def create_sample_data():
    """Create sample data for demonstration"""
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    n_repos = 100
    
    languages = ['python', 'javascript', 'java', 'go', 'rust', 'typescript']
    
    data = {
        'owner': [f'owner_{i}' for i in range(n_repos)],
        'repo_name': [f'repo_{i}' for i in range(n_repos)],
        'full_name': [f'owner_{i}/repo_{i}' for i in range(n_repos)],
        'url': [f'https://github.com/owner_{i}/repo_{i}' for i in range(n_repos)],
        'description': [f'Sample description {i}' for i in range(n_repos)],
        'language': np.random.choice(languages, n_repos),
        'stars': np.random.exponential(100, n_repos).astype(int),
        'forks': np.random.exponential(50, n_repos).astype(int),
        'watchers': np.random.exponential(30, n_repos).astype(int),
        'open_issues': np.random.poisson(5, n_repos),
        'license': np.random.choice(['MIT', 'Apache 2.0', 'GPL', 'Unknown'], n_repos),
        'topics': ['python,data-science' if i % 2 == 0 else 'web,javascript' for i in range(n_repos)]
    }
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    main()
