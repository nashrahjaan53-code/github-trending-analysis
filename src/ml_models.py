"""
Machine Learning models for repository analysis and prediction
"""

import logging
import pandas as pd
import numpy as np
from typing import Tuple, Dict
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import warnings

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')


class RepositoryClustering:
    """K-means clustering for repository categorization"""
    
    def __init__(self, n_clusters: int = 4):
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = None
        self.feature_names = None
    
    def fit(self, df: pd.DataFrame) -> Dict:
        """
        Fit clustering model
        
        Args:
            df: Input dataframe
        
        Returns:
            Clustering results
        """
        # Select features
        features = ['stars', 'forks', 'watchers', 'open_issues', 'engagement_score']
        features = [f for f in features if f in df.columns]
        
        self.feature_names = features
        X = df[features].fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit KMeans
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        clusters = self.kmeans.fit_predict(X_scaled)
        
        logger.info(f"✓ Clustering complete - {self.n_clusters} clusters identified")
        
        return {
            'clusters': clusters,
            'centers': self.kmeans.cluster_centers_,
            'inertia': self.kmeans.inertia_,
            'silhouette': self._calculate_silhouette(X_scaled)
        }
    
    def _calculate_silhouette(self, X_scaled) -> float:
        """Calculate silhouette score"""
        from sklearn.metrics import silhouette_score
        try:
            return silhouette_score(X_scaled, self.kmeans.labels_)
        except:
            return None
    
    def predict_cluster(self, df: pd.DataFrame) -> np.ndarray:
        """Predict clusters for new data"""
        features = self.feature_names
        X = df[features].fillna(0)
        X_scaled = self.scaler.transform(X)
        return self.kmeans.predict(X_scaled)
    
    def get_cluster_profiles(self, df: pd.DataFrame) -> Dict:
        """Get characteristics of each cluster"""
        clusters = self.predict_cluster(df)
        df_with_clusters = df.copy()
        df_with_clusters['cluster'] = clusters
        
        profiles = {}
        for cluster_id in range(self.n_clusters):
            cluster_data = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
            profiles[f'Cluster_{cluster_id}'] = {
                'size': len(cluster_data),
                'avg_stars': cluster_data['stars'].mean(),
                'avg_forks': cluster_data['forks'].mean(),
                'avg_watchers': cluster_data['watchers'].mean(),
                'top_language': cluster_data['language'].mode()[0] if len(cluster_data['language'].mode()) > 0 else 'Unknown',
                'description': self._describe_cluster(cluster_id, cluster_data)
            }
        
        return profiles
    
    def _describe_cluster(self, cluster_id: int, cluster_data: pd.DataFrame) -> str:
        """Generate human-readable cluster description"""
        avg_stars = cluster_data['stars'].mean()
        avg_forks = cluster_data['forks'].mean()
        
        if avg_stars > cluster_data['stars'].quantile(0.75):
            return "Highly Popular Repositories"
        elif avg_forks > cluster_data['forks'].quantile(0.75):
            return "Community-Driven Repositories"
        elif cluster_data['open_issues'].mean() > cluster_data['open_issues'].quantile(0.75):
            return "Active Development"
        else:
            return "Growing/Emerging Repositories"


class RepositorySuccessPredictor:
    """Predict repository success (binary classification)"""
    
    def __init__(self, success_threshold: float = 0.75):
        self.success_threshold = success_threshold
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.performance = {}
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for modeling
        
        Args:
            df: Input dataframe
        
        Returns:
            Features and target variable
        """
        # Define success: repositories in top quartile of stars
        success_threshold = df['stars'].quantile(self.success_threshold)
        y = (df['stars'] >= success_threshold).astype(int)
        
        # Select features
        features = ['forks', 'watchers', 'open_issues', 'description_length', 
                   'engagement_score', 'fork_ratio']
        features = [f for f in features if f in df.columns]
        self.feature_names = features
        
        X = df[features].fillna(0)
        
        logger.info(f"Target distribution: {y.value_counts().to_dict()}")
        
        return X.values, y.values
    
    def train(self, df: pd.DataFrame, model_type: str = 'random_forest') -> Dict:
        """
        Train success prediction model
        
        Args:
            df: Training data
            model_type: 'random_forest' or 'logistic_regression'
        
        Returns:
            Training results
        """
        X, y = self.prepare_data(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        else:
            self.model = LogisticRegression(random_state=42, max_iter=1000)
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        self.performance = {
            'accuracy': (y_pred == y_test).mean(),
            'auc_roc': roc_auc_score(y_test, y_pred_proba),
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'test_size': len(y_test),
            'model_type': model_type
        }
        
        logger.info(f"✓ Model trained - Accuracy: {self.performance['accuracy']:.3f}, AUC: {self.performance['auc_roc']:.3f}")
        
        return self.performance
    
    def predict_success(self, df: pd.DataFrame) -> np.ndarray:
        """Predict success for new repositories"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        features = self.feature_names
        X = df[features].fillna(0)
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)[:, 1]
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance scores"""
        if not hasattr(self.model, 'feature_importances_'):
            logger.warning("Model doesn't support feature importance")
            return {}
        
        importances = dict(zip(self.feature_names, self.model.feature_importances_))
        return dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))


class ModelPipeline:
    """Complete ML pipeline"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.clustering = RepositoryClustering(n_clusters=4)
        self.predictor = RepositorySuccessPredictor()
        self.results = {}
    
    def run_full_pipeline(self) -> Dict:
        """Execute complete analysis pipeline"""
        logger.info("Running full ML pipeline...")
        
        # Clustering
        logger.info("Step 1: Clustering repositories...")
        clustering_results = self.clustering.fit(self.df)
        self.df['cluster'] = clustering_results['clusters']
        self.results['clustering'] = clustering_results
        self.results['cluster_profiles'] = self.clustering.get_cluster_profiles(self.df)
        
        # Success prediction
        logger.info("Step 2: Training success predictor...")
        self.results['predictor_performance'] = self.predictor.train(self.df)
        self.df['success_probability'] = self.predictor.predict_success(self.df)
        self.results['feature_importance'] = self.predictor.get_feature_importance()
        
        logger.info("✓ ML pipeline complete")
        return self.results
