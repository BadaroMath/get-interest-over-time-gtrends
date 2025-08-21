"""Test configuration and fixtures."""

import pytest
import pandas as pd
from datetime import datetime, date
import tempfile
import shutil
from pathlib import Path

from trends_analyzer import TrendsAnalyzer, Config
from trends_analyzer.core import DataCollector, DataProcessor
from trends_analyzer.exporters import CSVExporter, JSONExporter


@pytest.fixture
def sample_trends_data():
    """Sample trends data for testing."""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    data = pd.DataFrame({
        'date': dates,
        'python': [50 + i % 30 for i in range(len(dates))],
        'javascript': [40 + i % 25 for i in range(len(dates))],
        'geo': 'US',
        'timeframe': 'today 12-m',
        'collection_date': datetime.now()
    })
    return data


@pytest.fixture
def sample_daily_data():
    """Sample daily data with trend indicators."""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    base_values = [50 + i % 30 + (i // 30) for i in range(len(dates))]
    
    data = pd.DataFrame({
        'date': dates,
        'artificial_intelligence_daily': base_values,
        'artificial_intelligence_monthly': [80] * len(dates),
        'month': dates.month,
        'year': dates.year,
        'geo': 'US'
    })
    return data


@pytest.fixture
def sample_monthly_data():
    """Sample monthly data."""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='MS')
    data = pd.DataFrame({
        'date': dates,
        'machine_learning_monthly': [70 + i % 20 for i in range(len(dates))],
        'month': dates.month,
        'year': dates.year,
        'geo': 'US'
    })
    return data


@pytest.fixture
def temp_config_file():
    """Temporary configuration file."""
    config_content = """
analyzer:
  default_geo: 'US'
  retry_attempts: 3
  timeout: 10

logging:
  level: 'INFO'
  console: true

export:
  default_format: 'csv'
  include_metadata: true
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_output_dir():
    """Temporary output directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_analyzer():
    """Mock analyzer for testing without API calls."""
    config = Config()
    config.analyzer.retry_attempts = 1
    config.analyzer.timeout = 5
    return TrendsAnalyzer(config=config)


@pytest.fixture
def data_processor():
    """Data processor instance."""
    return DataProcessor()


@pytest.fixture
def csv_exporter(temp_output_dir):
    """CSV exporter with temporary directory."""
    return CSVExporter(
        output_dir=temp_output_dir,
        timestamp_files=False
    )


@pytest.fixture
def json_exporter(temp_output_dir):
    """JSON exporter with temporary directory."""
    return JSONExporter(
        output_dir=temp_output_dir,
        timestamp_files=False
    )