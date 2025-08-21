"""Tests for the main TrendsAnalyzer class."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from trends_analyzer import TrendsAnalyzer, Config
from trends_analyzer.utils.validators import validate_keywords


class TestTrendsAnalyzer:
    """Test cases for TrendsAnalyzer class."""
    
    def test_initialization_default(self):
        """Test analyzer initialization with defaults."""
        analyzer = TrendsAnalyzer()
        
        assert analyzer.config is not None
        assert analyzer.config.analyzer.default_geo == 'US'
        assert analyzer.collector is not None
        assert analyzer.processor is not None
    
    def test_initialization_with_config_file(self, temp_config_file):
        """Test analyzer initialization with config file."""
        analyzer = TrendsAnalyzer(config=temp_config_file)
        
        assert analyzer.config.analyzer.retry_attempts == 3
        assert analyzer.config.analyzer.timeout == 10
    
    def test_initialization_with_config_dict(self):
        """Test analyzer initialization with config dictionary."""
        config_dict = {
            'analyzer': {
                'default_geo': 'GB',
                'retry_attempts': 10
            }
        }
        
        analyzer = TrendsAnalyzer(config=config_dict)
        
        assert analyzer.config.analyzer.default_geo == 'GB'
        assert analyzer.config.analyzer.retry_attempts == 10
    
    def test_from_config_classmethod(self, temp_config_file):
        """Test creating analyzer from config file using classmethod."""
        analyzer = TrendsAnalyzer.from_config(temp_config_file)
        
        assert isinstance(analyzer, TrendsAnalyzer)
        assert analyzer.config.analyzer.retry_attempts == 3
    
    @patch('trends_analyzer.core.collector.DataCollector.collect_interest_over_time')
    def test_get_trends_basic(self, mock_collect, sample_trends_data):
        """Test basic trends collection."""
        mock_collect.return_value = sample_trends_data
        
        analyzer = TrendsAnalyzer()
        result = analyzer.get_trends(
            keywords=['python'],
            timeframe='today 3-m',
            geo='US'
        )
        
        assert not result.empty
        assert 'python' in result.columns
        mock_collect.assert_called_once()
    
    def test_get_trends_input_validation(self):
        """Test input validation for get_trends."""
        analyzer = TrendsAnalyzer()
        
        # Test invalid keywords
        with pytest.raises(ValueError):
            analyzer.get_trends(keywords=[])
        
        with pytest.raises(ValueError):
            analyzer.get_trends(keywords=[''] * 6)  # Too many keywords
    
    @patch('trends_analyzer.core.collector.DataCollector.collect_daily_data')
    def test_get_daily_trends(self, mock_collect, sample_daily_data):
        """Test daily trends collection."""
        mock_collect.return_value = sample_daily_data
        
        analyzer = TrendsAnalyzer()
        result = analyzer.get_daily_trends(
            keywords=['artificial intelligence'],
            since_date='2023-01-01',
            geo='US'
        )
        
        assert not result.empty
        mock_collect.assert_called_once()
    
    @patch('trends_analyzer.core.collector.DataCollector.collect_monthly_data')
    def test_get_monthly_trends(self, mock_collect, sample_monthly_data):
        """Test monthly trends collection."""
        mock_collect.return_value = sample_monthly_data
        
        analyzer = TrendsAnalyzer()
        result = analyzer.get_monthly_trends(
            keywords=['machine learning'],
            geo='US',
            since_date='2023-01-01'
        )
        
        assert not result.empty
        mock_collect.assert_called_once()
    
    @patch('trends_analyzer.core.collector.DataCollector.collect_daily_data')
    @patch('trends_analyzer.core.collector.DataCollector.collect_monthly_data')
    def test_get_comprehensive_analysis(self, mock_monthly, mock_daily, 
                                      sample_daily_data, sample_monthly_data):
        """Test comprehensive analysis."""
        mock_daily.return_value = sample_daily_data
        mock_monthly.return_value = sample_monthly_data
        
        analyzer = TrendsAnalyzer()
        results = analyzer.get_comprehensive_analysis(
            keywords=['test_keyword'],
            geo='US',
            since_date='2023-01-01'
        )
        
        assert isinstance(results, dict)
        assert 'daily' in results
        assert 'monthly' in results
    
    @patch('trends_analyzer.core.collector.DataCollector.collect_interest_over_time')
    def test_analyze_batch(self, mock_collect, sample_trends_data):
        """Test batch analysis of multiple keywords."""
        mock_collect.return_value = sample_trends_data
        
        analyzer = TrendsAnalyzer()
        keywords = ['python', 'javascript', 'java', 'cpp', 'go']
        
        results = analyzer.analyze_batch(
            keyword_list=keywords,
            batch_size=3
        )
        
        assert isinstance(results, dict)
        # Should handle batching properly
        assert len(results) <= len(keywords)
    
    @patch('trends_analyzer.core.collector.DataCollector.collect_interest_over_time')
    def test_compare_keywords(self, mock_collect, sample_trends_data):
        """Test keyword comparison functionality."""
        mock_collect.return_value = sample_trends_data
        
        analyzer = TrendsAnalyzer()
        result = analyzer.compare_keywords(
            keywords=['python', 'javascript'],
            timeframe='today 12-m',
            normalize=True
        )
        
        assert not result.empty
        # Should have normalized columns
        normalized_cols = [col for col in result.columns if 'normalized' in col]
        assert len(normalized_cols) > 0
    
    def test_get_summary_stats(self, sample_trends_data):
        """Test summary statistics generation."""
        analyzer = TrendsAnalyzer()
        
        stats = analyzer.get_summary_stats(
            data=sample_trends_data,
            value_columns=['python', 'javascript']
        )
        
        assert not stats.empty
        assert 'mean' in stats.columns
        assert 'std' in stats.columns
        assert len(stats) == 2  # Two keywords
    
    def test_get_summary_stats_empty_data(self):
        """Test summary stats with empty data."""
        analyzer = TrendsAnalyzer()
        
        stats = analyzer.get_summary_stats(pd.DataFrame())
        
        assert stats.empty
    
    def test_error_handling_empty_data(self):
        """Test handling of empty data responses."""
        analyzer = TrendsAnalyzer()
        
        with patch.object(analyzer.collector, 'collect_interest_over_time', 
                         return_value=pd.DataFrame()):
            result = analyzer.get_trends(['test'])
            assert result.empty