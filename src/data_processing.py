"""
Data processing and cleaning module
"""

import logging
import pandas as pd
import numpy as np
from typing import Tuple

logger = logging.getLogger(__name__)


def clean_numeric_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert numeric string values to actual numbers
    Handles values like '1.5k', '2.3m', etc.
    """
    numeric_cols = ['stars_today', 'total_stars', 'stars', 'forks', 'watchers', 'open_issues']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(_convert_to_number)
    
    return df


def _convert_to_number(value) -> float:
    """Convert string values with k/m suffix to actual numbers"""
    if pd.isna(value) or value == '' or value == 'Unknown':
        return 0
    
    if isinstance(value, (int, float)):
        return float(value)
    
    value = str(value).strip().lower()
    
    if 'm' in value:
        return float(value.replace('m', '')) * 1_000_000
    elif 'k' in value:
        return float(value.replace('k', '')) * 1_000
    else:
        try:
            return float(value)
        except:
            return 0


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values in the dataset"""
    # Fill missing values
    df['description'] = df['description'].fillna("No description")
    df['language'] = df['language'].fillna("Unknown")
    df['topics'] = df['topics'].fillna("No topics")
    df['license'] = df['license'].fillna("Unknown")
    
    # Fill numeric columns with 0
    numeric_cols = ['stars', 'forks', 'watchers', 'open_issues']
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    logger.info(f"Missing values handled. Shape: {df.shape}")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create new features from existing data"""
    
    # Engagement score
    df['engagement_score'] = (
        df['watchers'] * 0.3 +
        df['forks'] * 0.4 +
        df['stars'] * 0.3
    )
    
    # Fork to stars ratio
    df['fork_ratio'] = df['forks'] / (df['stars'] + 1)
    
    # Issue density (issues per star)
    df['issue_density'] = df['open_issues'] / (df['stars'] + 1)
    
    # Activity level estimate
    df['activity_level'] = np.where(
        df['issue_density'] < 0.01, 'Low',
        np.where(df['issue_density'] < 0.05, 'Medium', 'High')
    )
    
    # Description length (quality proxy)
    df['description_length'] = df['description'].str.len()
    
    # Is popular
    df['is_popular'] = (df['stars'] > df['stars'].quantile(0.75)).astype(int)
    
    # Language category
    language_categories = {
        'python': 'Dynamic',
        'javascript': 'Dynamic',
        'typescript': 'Dynamic',
        'java': 'Static',
        'go': 'Static',
        'rust': 'Static',
        'c++': 'Static',
        'c#': 'Static',
        'unknown': 'Other'
    }
    df['language_category'] = df['language'].str.lower().map(language_categories).fillna('Other')
    
    logger.info(f"Features engineered. New columns: {df.shape[1]}")
    return df


def normalize_features(df: pd.DataFrame, numerical_cols: list = None) -> Tuple[pd.DataFrame, dict]:
    """
    Normalize numerical features for ML models
    
    Args:
        df: Input dataframe
        numerical_cols: Columns to normalize
    
    Returns:
        Normalized dataframe and scaling info
    """
    from sklearn.preprocessing import StandardScaler
    
    if numerical_cols is None:
        numerical_cols = ['stars', 'forks', 'watchers', 'open_issues', 
                         'description_length', 'engagement_score']
    
    # Filter to existing columns
    numerical_cols = [col for col in numerical_cols if col in df.columns]
    
    scaler = StandardScaler()
    df_normalized = df.copy()
    df_normalized[numerical_cols] = scaler.fit_transform(df[numerical_cols])
    
    scaling_info = {
        'scaler': scaler,
        'columns': numerical_cols,
        'means': dict(zip(numerical_cols, scaler.mean_)),
        'stds': dict(zip(numerical_cols, scaler.scale_))
    }
    
    logger.info(f"Features normalized: {numerical_cols}")
    return df_normalized, scaling_info


def process_github_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Complete processing pipeline
    
    Args:
        df: Raw GitHub data
    
    Returns:
        Processed and enriched dataframe
    """
    logger.info("Starting data processing pipeline...")
    
    # Clean numeric values
    df = clean_numeric_values(df)
    logger.info("✓ Numeric values cleaned")
    
    # Handle missing values
    df = handle_missing_values(df)
    logger.info("✓ Missing values handled")
    
    # Engineer features
    df = engineer_features(df)
    logger.info("✓ Features engineered")
    
    # Remove duplicates (final check)
    original_count = len(df)
    df = df.drop_duplicates(subset=['full_name'], keep='first')
    logger.info(f"✓ Duplicates removed: {original_count - len(df)} rows")
    
    logger.info(f"Processing complete! Final shape: {df.shape}")
    return df
