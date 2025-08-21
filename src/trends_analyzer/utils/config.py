"""Configuration management for Google Trends Analyzer."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, validator
from dataclasses import dataclass, field


@dataclass
class AnalyzerConfig:
    """Configuration for the TrendsAnalyzer."""
    default_geo: str = 'US'
    default_timeframe: str = 'today 3-m'
    retry_attempts: int = 5
    timeout: int = 30
    cache_enabled: bool = True
    cache_dir: str = './cache'
    delay_between_requests: float = 1.0


@dataclass 
class LoggingConfig:
    """Configuration for logging."""
    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file: Optional[str] = None
    console: bool = True


@dataclass
class ExportConfig:
    """Configuration for data export."""
    default_format: str = 'csv'
    include_metadata: bool = True
    timestamp_columns: bool = True
    output_dir: str = './results'


@dataclass
class BigQueryConfig:
    """Configuration for BigQuery integration."""
    project_id: Optional[str] = None
    dataset_id: str = 'trends_data'
    location: str = 'US'
    write_disposition: str = 'WRITE_TRUNCATE'
    credentials_path: Optional[str] = None
    credentials_json: Optional[str] = None


class Config:
    """Main configuration class for Google Trends Analyzer."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file, environment, or defaults."""
        self.analyzer = AnalyzerConfig()
        self.logging = LoggingConfig()
        self.export = ExportConfig()
        self.bigquery = BigQueryConfig()
        
        # Load from file if provided
        if config_path:
            self.load_from_file(config_path)
            
        # Override with environment variables
        self.load_from_env()
    
    def load_from_file(self, config_path: str) -> None:
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Update configurations
        if 'analyzer' in config_data:
            self._update_dataclass(self.analyzer, config_data['analyzer'])
        if 'logging' in config_data:
            self._update_dataclass(self.logging, config_data['logging'])
        if 'export' in config_data:
            self._update_dataclass(self.export, config_data['export'])
        if 'bigquery' in config_data:
            self._update_dataclass(self.bigquery, config_data['bigquery'])
    
    def load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Analyzer config
        self.analyzer.default_geo = os.getenv('DEFAULT_GEO', self.analyzer.default_geo)
        self.analyzer.default_timeframe = os.getenv('DEFAULT_TIMEFRAME', self.analyzer.default_timeframe)
        self.analyzer.retry_attempts = int(os.getenv('RETRY_ATTEMPTS', self.analyzer.retry_attempts))
        self.analyzer.timeout = int(os.getenv('REQUEST_TIMEOUT', self.analyzer.timeout))
        self.analyzer.cache_dir = os.getenv('TRENDS_CACHE_DIR', self.analyzer.cache_dir)
        
        # Logging config
        self.logging.level = os.getenv('LOG_LEVEL', self.logging.level)
        self.logging.file = os.getenv('LOG_FILE', self.logging.file)
        
        # Export config
        self.export.default_format = os.getenv('DEFAULT_EXPORT_FORMAT', self.export.default_format)
        self.export.include_metadata = os.getenv('INCLUDE_METADATA', '').lower() == 'true'
        
        # BigQuery config
        self.bigquery.project_id = os.getenv('GOOGLE_CLOUD_PROJECT', self.bigquery.project_id)
        self.bigquery.dataset_id = os.getenv('BIGQUERY_DATASET', self.bigquery.dataset_id)
        self.bigquery.location = os.getenv('BIGQUERY_LOCATION', self.bigquery.location)
        self.bigquery.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', self.bigquery.credentials_path)
        self.bigquery.credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', self.bigquery.credentials_json)
    
    def _update_dataclass(self, obj: Any, data: Dict[str, Any]) -> None:
        """Update dataclass fields from dictionary."""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'analyzer': self.analyzer.__dict__,
            'logging': self.logging.__dict__,
            'export': self.export.__dict__,
            'bigquery': self.bigquery.__dict__
        }
    
    def save_to_file(self, config_path: str) -> None:
        """Save current configuration to YAML file."""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create configuration from dictionary."""
        config = cls()
        
        if 'analyzer' in config_dict:
            config._update_dataclass(config.analyzer, config_dict['analyzer'])
        if 'logging' in config_dict:
            config._update_dataclass(config.logging, config_dict['logging'])
        if 'export' in config_dict:
            config._update_dataclass(config.export, config_dict['export'])
        if 'bigquery' in config_dict:
            config._update_dataclass(config.bigquery, config_dict['bigquery'])
            
        return config