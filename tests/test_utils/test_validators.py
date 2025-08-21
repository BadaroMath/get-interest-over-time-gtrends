"""Tests for validation utilities."""

import pytest
from datetime import date

from trends_analyzer.utils.validators import (
    validate_keywords,
    validate_geo,
    validate_timeframe,
    validate_output_path,
    validate_batch_size
)


class TestValidateKeywords:
    """Test keyword validation."""
    
    def test_valid_single_keyword(self):
        """Test validation of single keyword."""
        result = validate_keywords('python programming')
        assert result == ['python programming']
    
    def test_valid_multiple_keywords(self):
        """Test validation of multiple keywords."""
        keywords = ['python', 'javascript', 'java']
        result = validate_keywords(keywords)
        assert result == keywords
    
    def test_empty_keywords(self):
        """Test validation fails for empty keywords."""
        with pytest.raises(ValueError, match="At least one keyword"):
            validate_keywords([])
    
    def test_too_many_keywords(self):
        """Test validation fails for too many keywords."""
        keywords = ['a', 'b', 'c', 'd', 'e', 'f']  # 6 keywords
        with pytest.raises(ValueError, match="Maximum 5 keywords"):
            validate_keywords(keywords)
    
    def test_empty_keyword_string(self):
        """Test validation fails for empty keyword string."""
        with pytest.raises(ValueError, match="Empty keyword"):
            validate_keywords([''])
    
    def test_keyword_too_long(self):
        """Test validation fails for overly long keywords."""
        long_keyword = 'a' * 101  # 101 characters
        with pytest.raises(ValueError, match="Keyword too long"):
            validate_keywords([long_keyword])
    
    def test_non_string_keyword(self):
        """Test validation fails for non-string keywords."""
        with pytest.raises(ValueError, match="Keyword must be string"):
            validate_keywords([123])
    
    def test_whitespace_handling(self):
        """Test proper handling of whitespace in keywords."""
        result = validate_keywords(['  python  ', '  javascript  '])
        assert result == ['python', 'javascript']


class TestValidateGeo:
    """Test geographic region validation."""
    
    def test_valid_country_codes(self):
        """Test validation of valid country codes."""
        valid_codes = ['US', 'GB', 'DE', 'FR', 'JP', 'BR']
        for code in valid_codes:
            result = validate_geo(code)
            assert result == code
    
    def test_valid_state_codes(self):
        """Test validation of valid state codes."""
        result = validate_geo('US-CA')
        assert result == 'US-CA'
    
    def test_valid_metro_codes(self):
        """Test validation of valid metro codes."""
        result = validate_geo('US-CA-807')
        assert result == 'US-CA-807'
    
    def test_worldwide_empty_string(self):
        """Test worldwide region (empty string)."""
        result = validate_geo('')
        assert result == ''
    
    def test_lowercase_conversion(self):
        """Test automatic uppercase conversion."""
        result = validate_geo('us')
        assert result == 'US'
    
    def test_invalid_format(self):
        """Test validation fails for invalid formats."""
        invalid_codes = ['USA', 'U', 'US-', 'US-CAL', '123']
        for code in invalid_codes:
            with pytest.raises(ValueError, match="Invalid geo format"):
                validate_geo(code)
    
    def test_non_string_geo(self):
        """Test validation fails for non-string input."""
        with pytest.raises(ValueError, match="Geo must be string"):
            validate_geo(123)


class TestValidateTimeframe:
    """Test timeframe validation."""
    
    def test_valid_predefined_timeframes(self):
        """Test validation of predefined timeframes."""
        valid_timeframes = [
            'now 1-H', 'now 4-H', 'now 1-d', 'now 7-d',
            'today 1-m', 'today 3-m', 'today 12-m', 'today 5-y', 'all'
        ]
        
        for timeframe in valid_timeframes:
            result = validate_timeframe(timeframe)
            assert result == timeframe
    
    def test_valid_custom_date_range(self):
        """Test validation of custom date ranges."""
        result = validate_timeframe('2023-01-01 2023-12-31')
        assert result == '2023-01-01 2023-12-31'
    
    def test_invalid_date_format(self):
        """Test validation fails for invalid date formats."""
        with pytest.raises(ValueError, match="Invalid timeframe format"):
            validate_timeframe('2023/01/01 2023/12/31')
    
    def test_start_date_after_end_date(self):
        """Test validation fails when start date is after end date."""
        with pytest.raises(ValueError, match="Start date must be before end date"):
            validate_timeframe('2023-12-31 2023-01-01')
    
    def test_future_end_date(self):
        """Test validation fails for future end dates."""
        future_date = '2030-12-31'
        with pytest.raises(ValueError, match="End date cannot be in the future"):
            validate_timeframe(f'2023-01-01 {future_date}')
    
    def test_too_old_start_date(self):
        """Test validation fails for dates too far in the past."""
        with pytest.raises(ValueError, match="Start date cannot be before"):
            validate_timeframe('2000-01-01 2023-12-31')
    
    def test_empty_timeframe(self):
        """Test validation fails for empty timeframe."""
        with pytest.raises(ValueError, match="Timeframe cannot be empty"):
            validate_timeframe('')
    
    def test_non_string_timeframe(self):
        """Test validation fails for non-string input."""
        with pytest.raises(ValueError, match="Timeframe must be string"):
            validate_timeframe(123)


class TestValidateOutputPath:
    """Test output path validation."""
    
    def test_csv_extension_added(self):
        """Test CSV extension is added when missing."""
        result = validate_output_path('output', 'csv')
        assert result == 'output.csv'
    
    def test_existing_extension_preserved(self):
        """Test existing extension is preserved."""
        result = validate_output_path('output.csv', 'csv')
        assert result == 'output.csv'
    
    def test_json_extension(self):
        """Test JSON extension handling."""
        result = validate_output_path('data', 'json')
        assert result == 'data.json'
    
    def test_unknown_format(self):
        """Test handling of unknown format."""
        result = validate_output_path('file', 'unknown')
        assert result == 'file'
    
    def test_empty_path(self):
        """Test validation fails for empty path."""
        with pytest.raises(ValueError, match="Output path cannot be empty"):
            validate_output_path('', 'csv')
    
    def test_non_string_path(self):
        """Test validation fails for non-string input."""
        with pytest.raises(ValueError, match="Output path must be string"):
            validate_output_path(123, 'csv')


class TestValidateBatchSize:
    """Test batch size validation."""
    
    def test_valid_batch_size(self):
        """Test validation of valid batch sizes."""
        result = validate_batch_size(5)
        assert result == 5
    
    def test_zero_batch_size(self):
        """Test validation fails for zero batch size."""
        with pytest.raises(ValueError, match="Batch size must be positive"):
            validate_batch_size(0)
    
    def test_negative_batch_size(self):
        """Test validation fails for negative batch size."""
        with pytest.raises(ValueError, match="Batch size must be positive"):
            validate_batch_size(-1)
    
    def test_too_large_batch_size(self):
        """Test validation fails for overly large batch size."""
        with pytest.raises(ValueError, match="Batch size too large"):
            validate_batch_size(101)
    
    def test_non_integer_batch_size(self):
        """Test validation fails for non-integer input."""
        with pytest.raises(ValueError, match="Batch size must be integer"):
            validate_batch_size(5.5)