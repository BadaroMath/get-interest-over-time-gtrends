"""Base exporter class for Google Trends Analyzer."""

import pandas as pd
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ..utils.logger import get_logger


class BaseExporter(ABC):
    """Abstract base class for data exporters."""
    
    def __init__(
        self,
        output_dir: str = './results',
        include_metadata: bool = True,
        timestamp_files: bool = True
    ):
        """
        Initialize the base exporter.
        
        Args:
            output_dir: Directory for output files
            include_metadata: Whether to include metadata in exports
            timestamp_files: Whether to add timestamps to filenames
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.include_metadata = include_metadata
        self.timestamp_files = timestamp_files
        self.logger = get_logger(__name__)
    
    @abstractmethod
    def export(
        self,
        data: pd.DataFrame,
        filename: str,
        **kwargs
    ) -> str:
        """
        Export data to specified format.
        
        Args:
            data: DataFrame to export
            filename: Output filename
            **kwargs: Additional export parameters
            
        Returns:
            Path to exported file
        """
        pass
    
    def _prepare_filename(self, filename: str, extension: str) -> Path:
        """
        Prepare output filename with timestamp and extension.
        
        Args:
            filename: Base filename
            extension: File extension (with dot)
            
        Returns:
            Complete file path
        """
        # Remove existing extension if present
        base_name = Path(filename).stem
        
        # Add timestamp if requested
        if self.timestamp_files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"{base_name}_{timestamp}"
        
        # Add extension
        full_filename = f"{base_name}{extension}"
        
        return self.output_dir / full_filename
    
    def _add_export_metadata(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add export metadata to DataFrame.
        
        Args:
            data: Input DataFrame
            
        Returns:
            DataFrame with export metadata
        """
        if not self.include_metadata:
            return data
        
        data_copy = data.copy()
        
        # Add export metadata
        data_copy['export_timestamp'] = datetime.now()
        data_copy['exporter_version'] = '1.0.0'
        
        return data_copy
    
    def _validate_data(self, data: pd.DataFrame) -> None:
        """
        Validate data before export.
        
        Args:
            data: DataFrame to validate
            
        Raises:
            ValueError: If data is invalid
        """
        if data is None:
            raise ValueError("Data cannot be None")
        
        if data.empty:
            self.logger.warning("Exporting empty DataFrame")
        
        # Check for any obvious data issues
        if len(data.columns) == 0:
            raise ValueError("DataFrame has no columns")
    
    def export_multiple(
        self,
        data_dict: Dict[str, pd.DataFrame],
        base_filename: str,
        **kwargs
    ) -> Dict[str, str]:
        """
        Export multiple DataFrames.
        
        Args:
            data_dict: Dictionary mapping names to DataFrames
            base_filename: Base filename for outputs
            **kwargs: Additional export parameters
            
        Returns:
            Dictionary mapping names to exported file paths
        """
        results = {}
        
        for name, data in data_dict.items():
            filename = f"{base_filename}_{name}"
            try:
                exported_path = self.export(data, filename, **kwargs)
                results[name] = exported_path
                self.logger.info(f"Exported {name} to {exported_path}")
            except Exception as e:
                self.logger.error(f"Failed to export {name}: {e}")
                results[name] = None
        
        return results