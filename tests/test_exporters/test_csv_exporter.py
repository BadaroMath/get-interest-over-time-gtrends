"""Tests for CSV exporter."""

import pytest
import pandas as pd
from pathlib import Path

from trends_analyzer.exporters import CSVExporter


class TestCSVExporter:
    """Test cases for CSV exporter."""
    
    def test_initialization(self, temp_output_dir):
        """Test CSV exporter initialization."""
        exporter = CSVExporter(
            output_dir=temp_output_dir,
            encoding='utf-8',
            separator=','
        )
        
        assert exporter.output_dir == Path(temp_output_dir)
        assert exporter.encoding == 'utf-8'
        assert exporter.separator == ','
    
    def test_export_basic(self, csv_exporter, sample_trends_data):
        """Test basic CSV export functionality."""
        output_path = csv_exporter.export(sample_trends_data, 'test_export')
        
        assert Path(output_path).exists()
        assert output_path.endswith('.csv')
        
        # Verify content
        exported_data = pd.read_csv(output_path)
        assert len(exported_data) > 0
        assert 'python' in exported_data.columns
    
    def test_export_with_custom_separator(self, temp_output_dir, sample_trends_data):
        """Test CSV export with custom separator."""
        exporter = CSVExporter(
            output_dir=temp_output_dir,
            separator=';',
            timestamp_files=False
        )
        
        output_path = exporter.export(sample_trends_data, 'custom_sep')
        
        # Verify separator
        with open(output_path, 'r') as f:
            content = f.read()
            assert ';' in content
    
    def test_export_without_index(self, csv_exporter, sample_trends_data):
        """Test CSV export without index."""
        output_path = csv_exporter.export(
            sample_trends_data, 
            'no_index',
            index=False
        )
        
        exported_data = pd.read_csv(output_path)
        # Should not have unnamed index column
        assert not any(col.startswith('Unnamed') for col in exported_data.columns)
    
    def test_export_with_metadata(self, temp_output_dir, sample_trends_data):
        """Test CSV export with metadata."""
        exporter = CSVExporter(
            output_dir=temp_output_dir,
            include_metadata=True,
            timestamp_files=False
        )
        
        output_path = exporter.export(sample_trends_data, 'with_metadata')
        
        exported_data = pd.read_csv(output_path)
        assert 'export_timestamp' in exported_data.columns
        assert 'exporter_version' in exported_data.columns
    
    def test_export_without_metadata(self, temp_output_dir, sample_trends_data):
        """Test CSV export without metadata."""
        exporter = CSVExporter(
            output_dir=temp_output_dir,
            include_metadata=False,
            timestamp_files=False
        )
        
        output_path = exporter.export(sample_trends_data, 'no_metadata')
        
        exported_data = pd.read_csv(output_path)
        assert 'export_timestamp' not in exported_data.columns
        assert 'exporter_version' not in exported_data.columns
    
    def test_export_summary(self, csv_exporter, sample_trends_data):
        """Test CSV summary export."""
        output_path = csv_exporter.export_summary(
            sample_trends_data,
            'summary_test',
            include_statistics=True
        )
        
        assert Path(output_path).exists()
        
        summary_data = pd.read_csv(output_path)
        assert 'mean' in summary_data.columns
        assert 'std' in summary_data.columns
    
    def test_export_multiple(self, csv_exporter, sample_trends_data):
        """Test exporting multiple DataFrames."""
        data_dict = {
            'dataset1': sample_trends_data,
            'dataset2': sample_trends_data.copy()
        }
        
        results = csv_exporter.export_multiple(data_dict, 'multi_export')
        
        assert len(results) == 2
        assert 'dataset1' in results
        assert 'dataset2' in results
        
        for file_path in results.values():
            assert Path(file_path).exists()
    
    def test_filename_preparation(self, csv_exporter):
        """Test filename preparation with timestamps."""
        csv_exporter.timestamp_files = True
        
        filename = csv_exporter._prepare_filename('test', '.csv')
        
        assert filename.suffix == '.csv'
        assert 'test' in filename.name
    
    def test_validate_data_empty(self, csv_exporter):
        """Test validation with empty data."""
        empty_data = pd.DataFrame()
        
        # Should not raise exception, just log warning
        csv_exporter._validate_data(empty_data)
    
    def test_validate_data_none(self, csv_exporter):
        """Test validation with None data."""
        with pytest.raises(ValueError, match="Data cannot be None"):
            csv_exporter._validate_data(None)
    
    def test_export_with_charts_data(self, csv_exporter, sample_trends_data):
        """Test export with chart-ready data."""
        results = csv_exporter.export_with_charts_data(
            sample_trends_data,
            'chart_test'
        )
        
        assert 'main' in results
        assert 'chart' in results
        
        for file_path in results.values():
            assert Path(file_path).exists()