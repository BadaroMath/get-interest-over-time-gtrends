"""JSON exporter for Google Trends data."""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from .base_exporter import BaseExporter


class JSONExporter(BaseExporter):
    """Export trends data to JSON format."""
    
    def __init__(
        self,
        output_dir: str = './results',
        include_metadata: bool = True,
        timestamp_files: bool = True,
        indent: int = 2,
        ensure_ascii: bool = False
    ):
        """
        Initialize JSON exporter.
        
        Args:
            output_dir: Directory for output files
            include_metadata: Whether to include metadata
            timestamp_files: Whether to add timestamps to filenames
            indent: JSON indentation level
            ensure_ascii: Whether to ensure ASCII encoding
        """
        super().__init__(output_dir, include_metadata, timestamp_files)
        self.indent = indent
        self.ensure_ascii = ensure_ascii
    
    def export(
        self,
        data: pd.DataFrame,
        filename: str,
        orient: str = 'records',
        date_format: str = 'iso',
        **kwargs
    ) -> str:
        """
        Export DataFrame to JSON.
        
        Args:
            data: DataFrame to export
            filename: Output filename
            orient: JSON orientation ('records', 'index', 'values', 'table')
            date_format: Date format ('iso', 'epoch')
            **kwargs: Additional pandas.to_json parameters
            
        Returns:
            Path to exported JSON file
        """
        self._validate_data(data)
        
        # Prepare data
        export_data = self._add_export_metadata(data)
        
        # Prepare filename
        output_path = self._prepare_filename(filename, '.json')
        
        try:
            # Configure JSON export parameters
            json_params = {
                'orient': orient,
                'date_format': date_format,
                'indent': self.indent,
                **kwargs
            }
            
            # Export to JSON
            json_str = export_data.to_json(**json_params)
            
            # Write to file with custom formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                # Parse and re-dump for consistent formatting
                json_data = json.loads(json_str)
                json.dump(
                    json_data,
                    f,
                    indent=self.indent,
                    ensure_ascii=self.ensure_ascii,
                    default=self._json_serializer
                )
            
            self.logger.info(
                f"Successfully exported to JSON",
                file=str(output_path),
                records=len(export_data),
                orient=orient
            )
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to export JSON: {e}")
            raise
    
    def export_structured(
        self,
        data: pd.DataFrame,
        filename: str,
        group_by: Optional[str] = None
    ) -> str:
        """
        Export data with structured JSON format.
        
        Args:
            data: DataFrame to export
            filename: Output filename
            group_by: Column to group data by
            
        Returns:
            Path to exported structured JSON file
        """
        self._validate_data(data)
        
        # Prepare filename
        output_path = self._prepare_filename(filename, '.json')
        
        try:
            # Create structured export
            if group_by and group_by in data.columns:
                # Group data by specified column
                structured_data = {}
                for group_value, group_data in data.groupby(group_by):
                    structured_data[str(group_value)] = group_data.drop(columns=[group_by]).to_dict('records')
            else:
                # Create hierarchical structure
                structured_data = {
                    'metadata': {
                        'export_timestamp': datetime.now().isoformat(),
                        'total_records': len(data),
                        'columns': list(data.columns),
                        'date_range': {
                            'start': data['date'].min() if 'date' in data.columns else None,
                            'end': data['date'].max() if 'date' in data.columns else None
                        } if 'date' in data.columns else None
                    },
                    'data': data.to_dict('records')
                }
            
            # Write structured JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    structured_data,
                    f,
                    indent=self.indent,
                    ensure_ascii=self.ensure_ascii,
                    default=self._json_serializer
                )
            
            self.logger.info(f"Successfully exported structured JSON to {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to export structured JSON: {e}")
            raise
    
    def export_analysis_results(
        self,
        results: Dict[str, pd.DataFrame],
        filename: str
    ) -> str:
        """
        Export analysis results in structured JSON format.
        
        Args:
            results: Dictionary of analysis results
            filename: Output filename
            
        Returns:
            Path to exported JSON file
        """
        # Prepare filename
        output_path = self._prepare_filename(filename, '.json')
        
        try:
            # Structure the results
            structured_results = {
                'metadata': {
                    'export_timestamp': datetime.now().isoformat(),
                    'analysis_types': list(results.keys()),
                    'total_datasets': len(results)
                },
                'results': {}
            }
            
            # Add each result dataset
            for analysis_type, data in results.items():
                if isinstance(data, pd.DataFrame):
                    structured_results['results'][analysis_type] = {
                        'metadata': {
                            'records': len(data),
                            'columns': list(data.columns)
                        },
                        'data': data.to_dict('records')
                    }
                elif isinstance(data, dict):
                    # Handle nested dictionary results (like related queries/topics)
                    structured_results['results'][analysis_type] = data
                else:
                    # Convert other types to string representation
                    structured_results['results'][analysis_type] = str(data)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    structured_results,
                    f,
                    indent=self.indent,
                    ensure_ascii=self.ensure_ascii,
                    default=self._json_serializer
                )
            
            self.logger.info(f"Successfully exported analysis results to {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to export analysis results: {e}")
            raise
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for non-serializable objects."""
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif pd.isna(obj):
            return None
        elif hasattr(obj, 'tolist'):  # NumPy arrays
            return obj.tolist()
        else:
            return str(obj)