"""
Utility functions for data processing and logging
"""

import os
import json
import pickle
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataManager:
    """Manages data I/O operations"""
    
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "raw"
        self.processed_path = self.base_path / "processed"
        self.models_path = self.base_path / "models"
        
        # Create directories if they don't exist
        for path in [self.raw_path, self.processed_path, self.models_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def save_csv(self, data, filename: str, subfolder: str = "processed"):
        """Save data as CSV"""
        if subfolder == "processed":
            path = self.processed_path / filename
        else:
            path = self.raw_path / filename
        
        data.to_csv(path, index=False)
        logger.info(f"Saved CSV: {path}")
        return path
    
    def load_csv(self, filename: str, subfolder: str = "processed"):
        """Load CSV data"""
        if subfolder == "processed":
            path = self.processed_path / filename
        else:
            path = self.raw_path / filename
        
        import pandas as pd
        data = pd.read_csv(path)
        logger.info(f"Loaded CSV: {path}")
        return data
    
    def save_json(self, data: Dict, filename: str):
        """Save data as JSON"""
        path = self.raw_path / filename
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved JSON: {path}")
        return path
    
    def load_json(self, filename: str):
        """Load JSON data"""
        path = self.raw_path / filename
        with open(path, 'r') as f:
            data = json.load(f)
        logger.info(f"Loaded JSON: {path}")
        return data
    
    def save_model(self, model: Any, filename: str):
        """Save ML model"""
        path = self.models_path / filename
        with open(path, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Saved model: {path}")
        return path
    
    def load_model(self, filename: str):
        """Load ML model"""
        path = self.models_path / filename
        with open(path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"Loaded model: {path}")
        return model


class GitHubAPI:
    """GitHub API wrapper"""
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = self._get_headers()
        self.remaining_requests = 60  # Default for unauthenticated
    
    def _get_headers(self) -> Dict[str, str]:
        """Construct API headers"""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers
    
    def get_repo_details(self, owner: str, repo: str) -> Dict:
        """Fetch repository details"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Failed to fetch {owner}/{repo}: {response.status_code}")
            return {}
    
    def search_repositories(self, query: str, sort: str = "stars", per_page: int = 30) -> List[Dict]:
        """Search repositories"""
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": query,
            "sort": sort,
            "per_page": per_page,
            "order": "desc"
        }
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            logger.warning(f"Search failed: {response.status_code}")
            return []
    
    def get_repo_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Fetch repository programming languages"""
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {}


def get_timestamp():
    """Get current timestamp string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_directory(path: str):
    """Ensure directory exists"""
    Path(path).mkdir(parents=True, exist_ok=True)


def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """Safe division"""
    return numerator / denominator if denominator != 0 else default
