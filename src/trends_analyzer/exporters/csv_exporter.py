"""CSV exporter for Google Trends data."""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any

from .base_exporter import BaseExporter


class CSVExporter(BaseExporter):
    """Export trends data to CSV format."""
    
    def __init__(
        self,
        output_dir: str = './results',
        include_metadata: bool = True,
        timestamp_files: bool = True,
        encoding: str = 'utf-8',
        separator: str = ','
    ):
        """
        Initialize CSV exporter.
        
        Args:
            output_dir: Directory for output files
            include_metadata: Whether to include metadata
            timestamp_files: Whether to add timestamps to filenames
            encoding: File encoding
            separator: CSV separator character
        """
        super().__init__(output_dir, include_metadata, timestamp_files)
        self.encoding = encoding
        self.separator = separator
    
    def export(
        self,
        data: pd.DataFrame,
        filename: str,
        index: bool = False,
        date_format: str = '%Y-%m-%d',
        **kwargs
    ) -> str:
        """
        Export DataFrame to CSV.
        
        Args:
            data: DataFrame to export
            filename: Output filename
            index: Whether to include index in CSV
            date_format: Format for date columns
            **kwargs: Additional pandas.to_csv parameters
            
        Returns:
            Path to exported CSV file
        """
        self._validate_data(data)
        
        # Prepare data
        export_data = self._add_export_metadata(data)
        
        # Prepare filename
        output_path = self._prepare_filename(filename, '.csv')
        
        try:
            # Configure CSV export parameters
            csv_params = {
                'index': index,
                'encoding': self.encoding,
                'sep': self.separator,
                'date_format': date_format,
                **kwargs
            }
            
            # Export to CSV
            export_data.to_csv(output_path, **csv_params)
            
            self.logger.info(
                f"Successfully exported to CSV",
                file=str(output_path),
                records=len(export_data),
                columns=len(export_data.columns)
            )
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {e}")
            raise
    
    def export_summary(
        self,
        data: pd.DataFrame,
        filename: str,
        include_statistics: bool = True
    ) -> str:
        """
        Export summary statistics to CSV.
        
        Args:
            data: DataFrame to summarize
            filename: Output filename
            include_statistics: Whether to include detailed statistics
            
        Returns:
            Path to exported summary CSV
        """
        self._validate_data(data)
        
        # Generate summary
        numeric_columns = data.select_dtypes(include=['number']).columns
        
        if len(numeric_columns) == 0:
            self.logger.warning("No numeric columns found for summary")
            return None
        
        summary_data = data[numeric_columns].describe()
        
        if include_statistics:
            # Add additional statistics
            additional_stats = pd.DataFrame({
                col: {
                    'variance': data[col].var(),
                    'skewness': data[col].skew() if hasattr(data[col], 'skew') else None,
                    'kurtosis': data[col].kurtosis() if hasattr(data[col], 'kurtosis') else None,
                } for col in numeric_columns
            }).T
            
            summary_data = pd.concat([summary_data.T, additional_stats], axis=1)
        
        # Export summary
        summary_filename = f"{filename}_summary"
        return self.export(summary_data, summary_filename)
    
    def export_with_charts_data(
        self,
        data: pd.DataFrame,
        filename: str,
        chart_columns: Optional[list] = None
    ) -> Dict[str, str]:
        """
        Export data with separate chart-ready data.
        
        Args:
            data: DataFrame to export
            filename: Base filename
            chart_columns: Columns to include in chart data
            
        Returns:
            Dictionary with paths to exported files
        """
        results = {}
        
        # Export main data
        results['main'] = self.export(data, filename)
        
        # Export chart data
        if chart_columns is None:
            chart_columns = [col for col in data.columns 
                           if col not in ['export_timestamp', 'exporter_version']]
        
        chart_data = data[['date'] + [col for col in chart_columns if col in data.columns]]
        chart_filename = f"{filename}_chart_data"
        results['chart'] = self.export(chart_data, chart_filename)
        
        return results