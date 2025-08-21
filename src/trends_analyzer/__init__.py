"""
Google Trends Analyzer

A powerful, enterprise-grade Python toolkit for collecting, analyzing, 
and visualizing Google Trends data.

Author: Your Name
License: MIT
Version: 1.0.0
"""

from .core.analyzer import TrendsAnalyzer
from .core.collector import DataCollector
from .core.processor import DataProcessor
from .exporters.bigquery_exporter import BigQueryExporter
from .exporters.csv_exporter import CSVExporter
from .exporters.json_exporter import JSONExporter
from .utils.config import Config
from .utils.logger import setup_logger

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Package level constants
SUPPORTED_GEOS = [
    '', 'US', 'GB', 'CA', 'AU', 'DE', 'FR', 'IT', 'ES', 'NL', 'SE', 'NO', 
    'DK', 'FI', 'CH', 'AT', 'BE', 'IE', 'PT', 'GR', 'PL', 'CZ', 'HU', 
    'RO', 'BG', 'HR', 'SI', 'SK', 'LT', 'LV', 'EE', 'JP', 'KR', 'CN', 
    'IN', 'SG', 'HK', 'TW', 'TH', 'MY', 'ID', 'PH', 'VN', 'BR', 'MX', 
    'AR', 'CL', 'CO', 'PE', 'UY', 'PY', 'BO', 'EC', 'VE', 'ZA', 'EG', 
    'MA', 'NG', 'KE', 'GH', 'RU', 'UA', 'TR', 'IL', 'AE', 'SA', 'QA'
]

SUPPORTED_TIMEFRAMES = [
    'now 1-H', 'now 4-H', 'now 1-d', 'now 7-d',
    'today 1-m', 'today 3-m', 'today 12-m', 'today 5-y', 'all'
]

__all__ = [
    'TrendsAnalyzer',
    'DataCollector', 
    'DataProcessor',
    'BigQueryExporter',
    'CSVExporter',
    'JSONExporter',
    'Config',
    'setup_logger',
    'SUPPORTED_GEOS',
    'SUPPORTED_TIMEFRAMES'
]