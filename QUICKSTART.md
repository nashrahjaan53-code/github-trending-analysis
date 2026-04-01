# Quick Start Guide

Get up and running with the GitHub Trending Analysis project in 5 minutes!

## Prerequisites

- Python 3.8+
- pip or conda package manager
- Git (optional)

## Installation & Setup

### Option 1: Automated Setup (Recommended)

```bash
cd github_trending_analysis

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: With Conda

```bash
conda create -n github-analysis python=3.11
conda activate github-analysis
pip install -r requirements.txt
```

## Getting Your GitHub Token (Optional but Recommended)

For higher API rate limits:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token"
3. Select scopes: `public_repo`, `repo`
4. Copy the token
5. Create `.env` file in project root:
   ```
   GITHUB_TOKEN=your_token_here
   ```

## Running the Analysis

### 1. Run the Full Pipeline

```bash
python main.py
```

This will:
- ✅ Collect trending repository data
- ✅ Process and engineer features
- ✅ Perform statistical analysis
- ✅ Train ML models
- ✅ Save results and models

**Expected Runtime:** 5-10 minutes (or instant with cached data)

### 2. View Interactive Dashboard

```bash
streamlit run dashboard/app.py
```

Opens at `http://localhost:8501`

Features:
- Real-time filtering
- Interactive visualizations
- Data explorer
- ML insights

### 3. Explore with Jupyter Notebook

```bash
jupyter notebook notebooks/exploratory_analysis.ipynb
```

## Project Structure

```
github_trending_analysis/
├── src/
│   ├── data_collection.py    # Web scraping & API integration
│   ├── data_processing.py    # Feature engineering
│   ├── analysis.py           # Statistical analysis
│   ├── ml_models.py          # ML clustering & prediction
│   └── utils.py              # Helper utilities
├── data/
│   ├── raw/                  # Original data
│   ├── processed/            # Processed datasets
│   └── models/               # Trained models
├── dashboard/
│   └── app.py               # Streamlit dashboard
├── notebooks/
│   └── exploratory_analysis.ipynb
├── main.py                  # Main pipeline script
└── requirements.txt
```

## Key Outputs

After running `python main.py`:

- **CSV Files:**
  - `data/processed/github_trending_processed.csv` - Cleaned data
  - `data/processed/github_trending_full_analysis.csv` - With ML predictions

- **Models:**
  - `data/models/clustering_model.pkl` - Repository clustering
  - `data/models/success_predictor_model.pkl` - Success prediction

- **Visualizations:**
  - Languages by stars
  - Stars vs forks scatter plot
  - Activity distribution charts

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution:** Make sure virtual environment is activated and run:
```bash
pip install -r requirements.txt
```

### Issue: "Failed to fetch from GitHub API"

**Solutions:**
- Check internet connection
- Add GitHub token to `.env` file (optional but increases limits)
- Wait a few minutes and try again (rate limiting)

### Issue: "Data files not found"

**Solution:** Run `python main.py` first to generate the data

## Customization

### Change Languages to Analyze

Edit in `main.py`:
```python
raw_data = collect_github_trending_data(
    languages=["python", "rust", "go"],  # Change here
    since="weekly"  # or "monthly"
)
```

### Adjust ML Model Parameters

In `src/ml_models.py`:
```python
# Change number of clusters
clustering = RepositoryClustering(n_clusters=5)

# Change success threshold
predictor = RepositorySuccessPredictor(success_threshold=0.8)
```

## Portfolio Highlights

This project demonstrates:

✅ **Data Engineering**
- Web scraping with BeautifulSoup
- REST API integration
- Feature engineering from raw data

✅ **Data Analysis**
- Exploratory data analysis (EDA)
- Statistical hypothesis testing
- Correlation analysis

✅ **Machine Learning**
- Unsupervised learning (K-means)
- Supervised learning (classification)
- Model evaluation & metrics

✅ **Visualization**
- Interactive Plotly charts
- Streamlit dashboards
- Matplotlib static plots

✅ **Software Engineering**
- Clean code architecture
- Modular design
- Comprehensive documentation
- Error handling & logging

## Next Steps

### To Improve Your Portfolio:

1. **Deploy Dashboard:**
   - Use Streamlit Cloud (free)
   - Share link in your resume

2. **Add More Features:**
   - Time-series forecasting
   - Sentiment analysis of descriptions
   - Repository recommendation engine

3. **Automated Updates:**
   - GitHub Actions for daily updates
   - Always-fresh data in dashboard

4. **Advanced Analytics:**
   - Topic modeling (LDA)
   - Network analysis
   - Language ecosystem relationships

## Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Pandas Guide:** https://pandas.pydata.org/docs
- **Scikit-Learn:** https://scikit-learn.org
- **GitHub API:** https://docs.github.com/en/rest

## Support

For issues or questions:
1. Check error logs in terminal
2. Review README.md for detailed info
3. Check data/raw/ for collected data
4. Verify internet connection

## License

MIT License - Use freely for portfolio projects!

---

**Happy Analyzing! 📊✨**
