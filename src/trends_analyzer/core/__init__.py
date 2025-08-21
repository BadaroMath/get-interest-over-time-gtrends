"""Core functionality for Google Trends Analyzer."""

from .analyzer import TrendsAnalyzer
from .collector import DataCollector
from .processor import DataProcessor

__all__ = ['TrendsAnalyzer', 'DataCollector', 'DataProcessor']