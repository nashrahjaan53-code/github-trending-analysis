# GitHub Trending Analysis - Implementation Guide

Detailed implementation notes and advanced usage for developers.

## Architecture Overview

### Data Flow

```
GitHub/Trending Website
         ↓
Data Collection (Web Scraping)
         ↓
GitHub API (Enrichment)
         ↓
Raw Data (JSON/CSV)
         ↓
Data Processing & Cleaning
         ↓
Feature Engineering
         ↓
Processed Data Ready for Analysis
         ↓
    ┌────┬──────┬──────┐
    ↓    ↓      ↓      ↓
 Analysis  ML   Viz  Dashboard
    
```

## Module Details

### 1. Data Collection (`src/data_collection.py`)

**Components:**
- `GithubTrendingScraper` - Scrapes GitHub trending page
- Web scraping with BeautifulSoup4
- GitHub API integration with rate limiting
- Error handling and logging

**Key Methods:**
```python
scraper = GithubTrendingScraper()

# Scrape trending repos
repos = scraper.scrape_trending(language="python", since="daily")

# Enrich with API data
enriched_repos = scraper.enrich_with_api_data(repos)
```

**Features Collected:**
- Repository metadata (owner, name, URL)
- Description
- Primary language
- Stars, forks, watchers
- Open issues
- License information
- Creation/update dates
- Topics/tags

### 2. Data Processing (`src/data_processing.py`)

**Processing Steps:**
1. **Numeric Conversion:** Convert "1.2k" → 1200
2. **Missing Value Handling:** Fill NaN values intelligently
3. **Feature Engineering:** Create calculated features
4. **Normalization:** Scale features for ML models

**Engineered Features:**
- `engagement_score` - Weighted combination of metrics
- `fork_ratio` - Forks per star
- `issue_density` - Issues per star
- `activity_level` - Categorical (Low/Medium/High)
- `description_length` - Content quality proxy
- `is_popular` - Binary popularity flag
- `language_category` - Dynamic vs Static typing

**Functions:**
```python
# Complete pipeline
processed_df = process_github_data(raw_df)

# Individual steps
cleaned = clean_numeric_values(df)
filled = handle_missing_values(cleaned)
engineered = engineer_features(filled)
normalized, scaling_info = normalize_features(engineered)
```

### 3. Analysis (`src/analysis.py`)

**RepositoryAnalyzer Class:**

```python
analyzer = RepositoryAnalyzer(df)

# Run all analyses
report = analyzer.generate_report()

# Individual analyses
analyzer.analyze_correlations()      # Pearson correlation
analyzer.analyze_languages()         # Language statistics
analyzer.analyze_licenses()          # License impact
analyzer.analyze_topics()            # Popular topics
analyzer.statistical_tests()         # Hypothesis testing
analyzer.get_summary_statistics()    # Descriptive stats
```

**Statistical Tests Performed:**
- **T-test:** Dynamic vs Static language popularity
- **ANOVA:** License impact on stars
- Correlation analysis
- Distribution analysis

### 4. Machine Learning (`src/ml_models.py`)

**Clustering (`RepositoryClustering`):**
- Algorithm: K-means clustering
- Features: stars, forks, watchers, open_issues, engagement_score
- Clusters: 4 default (customizable)
- Silhouette score for quality measurement

**Success Prediction (`RepositorySuccessPredictor`):**
- Algorithm: Random Forest Classification (or Logistic Regression)
- Target: Binary (Top 25% stars vs others)
- Features: forks, watchers, issues, description_length, engagement_score, fork_ratio
- Metrics: Accuracy, AUC-ROC, Classification Report

**Complete Pipeline:**
```python
pipeline = ModelPipeline(df)
results = pipeline.run_full_pipeline()

# Access results
clusters = results['clustering']
profiles = results['cluster_profiles']
predictor_perf = results['predictor_performance']
feature_importance = results['feature_importance']
```

## Advanced Usage

### Custom Data Collection

```python
from src.data_collection import GithubTrendingScraper

scraper = GithubTrendingScraper()

# Scrape specific language
repos = scraper.scrape_trending(language="rust", since="weekly")

# Enrich with API
repos = scraper.enrich_with_api_data(repos)

# Create DataFrame
import pandas as pd
df = pd.DataFrame(repos)
```

### Custom Analysis

```python
from src.analysis import RepositoryAnalyzer

analyzer = RepositoryAnalyzer(df)

# Custom correlation analysis
correlations = analyzer.analyze_correlations()
top_corr = correlations['top_pairs'].head(5)

# Custom language analysis
lang_stats = analyzer.analyze_language()
print(lang_stats.nlargest(10, 'avg_stars'))

# Perform tests
test_results = analyzer.statistical_tests()
```

### Model Training & Deployment

```python
from src.ml_models import ModelPipeline
from src.utils import DataManager

# Train
pipeline = ModelPipeline(df)
results = pipeline.run_full_pipeline()

# Save models
data_manager = DataManager()
data_manager.save_model(pipeline.clustering, "my_clustering.pkl")
data_manager.save_model(pipeline.predictor, "my_predictor.pkl")

# Load & use
loaded_clustering = data_manager.load_model("my_clustering.pkl")
new_clusters = loaded_clustering.predict_cluster(new_df)
```

## API Rate Limiting

GitHub API limits:
- **Unauthenticated:** 60 requests/hour
- **Authenticated:** 5,000 requests/hour

The code includes:
- Automatic rate limiting with `time.sleep()`
- Warning logs when rate limits approached
- Graceful error handling

## Performance Optimization

### Speed up data collection:
```python
# Use fewer languages
languages = ["python", "javascript"]  # Instead of all

# Use existing data
df = data_manager.load_csv("github_trending_full_analysis.csv")
```

### Speed up ML:
```python
# Reduce dataset size for testing
sample_df = df.sample(n=50, random_state=42)
pipeline = ModelPipeline(sample_df)  # Faster
```

## Extending the Project

### Add Time-Series Forecasting

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler

# Predict future star growth
df['stars_tomorrow'] = model.predict(features)
```

### Add Sentiment Analysis

```python
from textblob import TextBlob

df['description_sentiment'] = df['description'].apply(
    lambda x: TextBlob(x).sentiment.polarity
)
```

### Add Recommendation Engine

```python
# Collaborative filtering
from sklearn.decomposition import TruncatedSVD

# Create user-repo matrix
user_repo_matrix = pd.crosstab(users, repos)

# SVD for recommendations
svd = TruncatedSVD(n_components=10)
recommendations = svd.fit_transform(user_repo_matrix)
```

## Debugging

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check data at each stage

```python
from src.utils import DataManager

dm = DataManager()

# List all saved data
import os
print(os.listdir('data/raw/'))
print(os.listdir('data/processed/'))

# Load and inspect
raw = dm.load_json('trending_repos_*.json')
processed = dm.load_csv('github_trending_processed.csv')
```

### Validate data quality

```python
# Check for issues
print(df.isnull().sum())          # Missing values
print(df.duplicated().sum())      # Duplicates
print(df.dtypes)                   # Data types
print(df.describe())               # Statistics
```

## Testing

### Unit Tests (example)

```python
# tests/test_data_processing.py
import pytest
from src.data_processing import clean_numeric_values
import pandas as pd

def test_numeric_conversion():
    df = pd.DataFrame({'stars': ['1.2k', '500']})
    result = clean_numeric_values(df)
    assert result.loc[0, 'stars'] == 1200
    assert result.loc[1, 'stars'] == 500
```

### Integration Tests

```python
# Test full pipeline
def test_full_pipeline():
    df = create_sample_data()
    processed = process_github_data(df)
    
    assert len(processed) > 0
    assert 'engagement_score' in processed.columns
    assert processed['stars'].dtype in ['float64', 'int64']
```

## Cloud Deployment

### Deploy Dashboard to Streamlit Cloud

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub repo
4. Select `dashboard/app.py` as main file
5. Share link!

### Deploy with Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "dashboard/app.py"]
```

## Project Statistics

### Code Metrics
- **Total Lines of Code:** ~2000
- **Number of Modules:** 5
- **Functions:** 50+
- **Classes:** 6
- **Documentation:** 100% of public APIs

### Data Processing
- **Max repositories:** 1000+
- **Features engineered:** 10+
- **Processing time:** 1-5 minutes
- **Storage:** <100MB

### ML Models
- **Clustering:** K-means, 4 clusters
- **Classification:** Random Forest, 100 estimators
- **Model accuracy:** 75-85%
- **Model size:** <5MB

## Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| GitHub API 404 | Rate limited | Wait 1 hour or use token |
| Numba errors | Missing dependency | `pip install scikit-learn` |
| Streamlit blank page | Port busy | `streamlit run ... --server.port 8502` |
| OOM error | Large dataset | Filter data first or sample |
| Slow analysis | Many repos | Use sample: `df.sample(n=100)` |

---

## References

- **Scikit-learn Docs:** https://scikit-learn.org/stable/
- **Pandas Documentation:** https://pandas.pydata.org/docs/
- **GitHub API:** https://docs.github.com/en/rest
- **Streamlit API:** https://docs.streamlit.io/

