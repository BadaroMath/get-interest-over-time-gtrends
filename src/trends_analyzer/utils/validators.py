"""Validation utilities for Google Trends Analyzer."""

import re
from datetime import datetime, date
from typing import List, Union, Optional
from dateutil.parser import parse as parse_date


def validate_keywords(keywords: Union[str, List[str]]) -> List[str]:
    """
    Validate and normalize keywords.
    
    Args:
        keywords: Single keyword string or list of keywords
        
    Returns:
        List of validated keywords
        
    Raises:
        ValueError: If keywords are invalid
    """
    if isinstance(keywords, str):
        keywords = [keywords]
    
    if not keywords:
        raise ValueError("At least one keyword must be provided")
    
    if len(keywords) > 5:
        raise ValueError("Maximum 5 keywords allowed per request")
    
    validated_keywords = []
    for keyword in keywords:
        if not isinstance(keyword, str):
            raise ValueError(f"Keyword must be string, got {type(keyword)}")
        
        keyword = keyword.strip()
        if not keyword:
            raise ValueError("Empty keyword not allowed")
        
        if len(keyword) > 100:
            raise ValueError(f"Keyword too long (max 100 chars): {keyword[:20]}...")
            
        validated_keywords.append(keyword)
    
    return validated_keywords


def validate_geo(geo: str) -> str:
    """
    Validate geographical region code.
    
    Args:
        geo: Geographic region code (e.g., 'US', 'GB', 'US-CA')
        
    Returns:
        Validated geo code
        
    Raises:
        ValueError: If geo code is invalid
    """
    if not isinstance(geo, str):
        raise ValueError(f"Geo must be string, got {type(geo)}")
    
    geo = geo.strip().upper()
    
    # Empty string means worldwide
    if geo == '':
        return geo
    
    # Valid patterns: 'US', 'US-CA', 'US-CA-807' (country, state, metro)
    geo_pattern = r'^[A-Z]{2}(-[A-Z]{2})?(-\d{3})?$'
    
    if not re.match(geo_pattern, geo):
        raise ValueError(f"Invalid geo format: {geo}. Expected format: 'US', 'US-CA', or 'US-CA-807'")
    
    return geo


def validate_timeframe(timeframe: str) -> str:
    """
    Validate timeframe parameter.
    
    Args:
        timeframe: Timeframe string (e.g., 'today 5-y', '2020-01-01 2020-12-31')
        
    Returns:
        Validated timeframe string
        
    Raises:
        ValueError: If timeframe is invalid
    """
    if not isinstance(timeframe, str):
        raise ValueError(f"Timeframe must be string, got {type(timeframe)}")
    
    timeframe = timeframe.strip()
    if not timeframe:
        raise ValueError("Timeframe cannot be empty")
    
    # Predefined timeframes
    predefined_timeframes = {
        'now 1-H', 'now 4-H', 'now 1-d', 'now 7-d',
        'today 1-m', 'today 3-m', 'today 12-m', 'today 5-y', 'all'
    }
    
    if timeframe in predefined_timeframes:
        return timeframe
    
    # Custom date range: 'YYYY-MM-DD YYYY-MM-DD'
    date_range_pattern = r'^\d{4}-\d{2}-\d{2} \d{4}-\d{2}-\d{2}$'
    
    if re.match(date_range_pattern, timeframe):
        try:
            start_date_str, end_date_str = timeframe.split(' ')
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if start_date >= end_date:
                raise ValueError("Start date must be before end date")
            
            if end_date > date.today():
                raise ValueError("End date cannot be in the future")
            
            # Check if date range is reasonable (not too far back)
            min_date = date(2004, 1, 1)  # Google Trends data starts around 2004
            if start_date < min_date:
                raise ValueError(f"Start date cannot be before {min_date}")
            
            return timeframe
            
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError(f"Invalid date format in timeframe: {timeframe}")
            raise
    
    raise ValueError(f"Invalid timeframe format: {timeframe}")


def validate_output_path(output_path: str, format_type: str = 'csv') -> str:
    """
    Validate and normalize output file path.
    
    Args:
        output_path: Output file path
        format_type: Expected file format
        
    Returns:
        Validated output path
        
    Raises:
        ValueError: If output path is invalid
    """
    if not isinstance(output_path, str):
        raise ValueError(f"Output path must be string, got {type(output_path)}")
    
    output_path = output_path.strip()
    if not output_path:
        raise ValueError("Output path cannot be empty")
    
    # Add extension if missing
    extensions = {
        'csv': '.csv',
        'json': '.json', 
        'parquet': '.parquet',
        'excel': '.xlsx'
    }
    
    if format_type in extensions:
        expected_ext = extensions[format_type]
        if not output_path.endswith(expected_ext):
            output_path += expected_ext
    
    return output_path


def validate_batch_size(batch_size: int, max_batch_size: int = 100) -> int:
    """
    Validate batch size parameter.
    
    Args:
        batch_size: Batch size for processing
        max_batch_size: Maximum allowed batch size
        
    Returns:
        Validated batch size
        
    Raises:
        ValueError: If batch size is invalid
    """
    if not isinstance(batch_size, int):
        raise ValueError(f"Batch size must be integer, got {type(batch_size)}")
    
    if batch_size <= 0:
        raise ValueError("Batch size must be positive")
    
    if batch_size > max_batch_size:
        raise ValueError(f"Batch size too large (max {max_batch_size}): {batch_size}")
    
    return batch_size