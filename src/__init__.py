"""
GitHub Trending Repository Analysis Package
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from . import data_collection
from . import data_processing
from . import analysis
from . import ml_models
from . import utils

__all__ = [
    "data_collection",
    "data_processing", 
    "analysis",
    "ml_models",
    "utils"
]
