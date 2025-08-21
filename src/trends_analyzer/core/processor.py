"""Data processing module for Google Trends data."""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple, Union
from pathlib import Path

from ..utils.logger import get_logger


class DataProcessor:
    """Handles processing and transformation of Google Trends data."""
    
    def __init__(self):
        """Initialize the data processor."""
        self.logger = get_logger(__name__)
    
    def merge_daily_monthly(
        self,
        daily_data: pd.DataFrame,
        monthly_data: pd.DataFrame,
        keywords: List[str]
    ) -> pd.DataFrame:
        """
        Merge daily and monthly data to create scaled daily values.
        
        This method combines daily granular data with monthly data to create
        more accurate daily trend values by scaling daily data using monthly baselines.
        
        Args:
            daily_data: DataFrame with daily trend data
            monthly_data: DataFrame with monthly trend data  
            keywords: List of keywords to process
            
        Returns:
            DataFrame with merged and scaled data
        """
        self.logger.info(
            "Merging daily and monthly data",
            daily_records=len(daily_data),
            monthly_records=len(monthly_data),
            keywords=keywords
        )
        
        if daily_data.empty or monthly_data.empty:
            self.logger.warning("Empty input data for merging")
            return pd.DataFrame()
        
        try:
            # Ensure both dataframes have required columns
            required_cols = ['year', 'month']
            for col in required_cols:
                if col not in daily_data.columns:
                    self.logger.error(f"Missing column in daily data: {col}")
                    return pd.DataFrame()
                if col not in monthly_data.columns:
                    self.logger.error(f"Missing column in monthly data: {col}")
                    return pd.DataFrame()
            
            # Create monthly data copy without date column for merging
            monthly_for_merge = monthly_data[[col for col in monthly_data.columns if col != 'date']].copy()
            
            # Merge on year and month
            merged_data = pd.merge(
                daily_data,
                monthly_for_merge,
                how='left',
                on=['year', 'month'],
                suffixes=('', '_monthly')
            )
            
            # Scale daily data using monthly data
            for keyword in keywords:
                daily_col = keyword
                monthly_col = f'{keyword}_monthly'
                scaled_col = f'{keyword}_daily'
                
                if daily_col in merged_data.columns and monthly_col in merged_data.columns:
                    # Scale daily values: daily * monthly / 100
                    merged_data[scaled_col] = (
                        merged_data[daily_col] * merged_data[monthly_col] / 100
                    ).round(2)
                    
                    # Remove original daily column to avoid confusion
                    merged_data = merged_data.drop(columns=[daily_col])
                else:
                    self.logger.warning(f"Missing columns for keyword {keyword}")
            
            # Remove temporary columns
            merged_data = merged_data.drop(columns=['year', 'month'], errors='ignore')
            
            # Sort by date
            if 'date' in merged_data.columns:
                merged_data = merged_data.sort_values('date').reset_index(drop=True)
            
            self.logger.info(f"Successfully merged data: {len(merged_data)} records")
            return merged_data
            
        except Exception as e:
            self.logger.error(f"Failed to merge daily and monthly data: {e}")
            raise
    
    def normalize_data(
        self,
        data: pd.DataFrame,
        method: str = 'minmax',
        columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Normalize numerical data using specified method.
        
        Args:
            data: Input DataFrame
            method: Normalization method ('minmax', 'zscore', 'robust')
            columns: Columns to normalize (defaults to numeric columns)
            
        Returns:
            DataFrame with normalized data
        """
        if data.empty:
            return data
        
        data_copy = data.copy()
        
        # Auto-detect numeric columns if not specified
        if columns is None:
            columns = data_copy.select_dtypes(include=[np.number]).columns.tolist()
            # Exclude metadata columns
            columns = [col for col in columns if not col.endswith(('_monthly', '_year', '_month'))]
        
        self.logger.info(f"Normalizing data using {method} method", columns=columns)
        
        try:
            for col in columns:
                if col not in data_copy.columns:
                    continue
                
                values = data_copy[col]
                
                if method == 'minmax':
                    # Min-Max normalization (0-1 range)
                    min_val = values.min()
                    max_val = values.max()
                    if max_val != min_val:
                        data_copy[f'{col}_normalized'] = (values - min_val) / (max_val - min_val)
                    else:
                        data_copy[f'{col}_normalized'] = 0
                
                elif method == 'zscore':
                    # Z-score normalization (mean=0, std=1)
                    mean_val = values.mean()
                    std_val = values.std()
                    if std_val != 0:
                        data_copy[f'{col}_normalized'] = (values - mean_val) / std_val
                    else:
                        data_copy[f'{col}_normalized'] = 0
                
                elif method == 'robust':
                    # Robust normalization using median and IQR
                    median_val = values.median()
                    q1 = values.quantile(0.25)
                    q3 = values.quantile(0.75)
                    iqr = q3 - q1
                    if iqr != 0:
                        data_copy[f'{col}_normalized'] = (values - median_val) / iqr
                    else:
                        data_copy[f'{col}_normalized'] = 0
                
                else:
                    self.logger.warning(f"Unknown normalization method: {method}")
            
            return data_copy
            
        except Exception as e:
            self.logger.error(f"Failed to normalize data: {e}")
            return data
    
    def calculate_trends(
        self,
        data: pd.DataFrame,
        value_columns: List[str],
        window_size: int = 7
    ) -> pd.DataFrame:
        """
        Calculate trend indicators (moving averages, growth rates, etc.).
        
        Args:
            data: Input DataFrame with time series data
            value_columns: Columns containing values to analyze
            window_size: Window size for moving averages
            
        Returns:
            DataFrame with trend indicators
        """
        if data.empty:
            return data
        
        data_copy = data.copy()
        
        # Ensure data is sorted by date
        if 'date' in data_copy.columns:
            data_copy = data_copy.sort_values('date')
        
        self.logger.info(f"Calculating trends with window size {window_size}")
        
        try:
            for col in value_columns:
                if col not in data_copy.columns:
                    continue
                
                values = data_copy[col]
                
                # Moving average
                data_copy[f'{col}_ma_{window_size}'] = values.rolling(
                    window=window_size, min_periods=1
                ).mean().round(2)
                
                # Moving standard deviation
                data_copy[f'{col}_std_{window_size}'] = values.rolling(
                    window=window_size, min_periods=1
                ).std().round(2)
                
                # Percentage change
                data_copy[f'{col}_pct_change'] = values.pct_change().fillna(0).round(4)
                
                # Growth rate (7-day)
                if len(values) >= window_size:
                    growth_rate = ((values / values.shift(window_size)) - 1) * 100
                    data_copy[f'{col}_growth_{window_size}d'] = growth_rate.fillna(0).round(2)
                
                # Volatility (coefficient of variation)
                rolling_mean = values.rolling(window=window_size, min_periods=1).mean()
                rolling_std = values.rolling(window=window_size, min_periods=1).std()
                volatility = (rolling_std / rolling_mean) * 100
                data_copy[f'{col}_volatility'] = volatility.fillna(0).round(2)
                
                # Trend direction (1: up, 0: stable, -1: down)
                ma_values = data_copy[f'{col}_ma_{window_size}']
                trend_direction = np.where(
                    ma_values > ma_values.shift(1), 1,
                    np.where(ma_values < ma_values.shift(1), -1, 0)
                )
                data_copy[f'{col}_trend_direction'] = trend_direction
            
            return data_copy
            
        except Exception as e:
            self.logger.error(f"Failed to calculate trends: {e}")
            return data
    
    def detect_anomalies(
        self,
        data: pd.DataFrame,
        value_columns: List[str],
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> pd.DataFrame:
        """
        Detect anomalies in the data using statistical methods.
        
        Args:
            data: Input DataFrame
            value_columns: Columns to analyze for anomalies
            method: Detection method ('iqr', 'zscore', 'isolation')
            threshold: Threshold for anomaly detection
            
        Returns:
            DataFrame with anomaly indicators
        """
        if data.empty:
            return data
        
        data_copy = data.copy()
        
        self.logger.info(f"Detecting anomalies using {method} method")
        
        try:
            for col in value_columns:
                if col not in data_copy.columns:
                    continue
                
                values = data_copy[col]
                anomaly_col = f'{col}_anomaly'
                
                if method == 'iqr':
                    # Interquartile Range method
                    q1 = values.quantile(0.25)
                    q3 = values.quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - threshold * iqr
                    upper_bound = q3 + threshold * iqr
                    
                    data_copy[anomaly_col] = (
                        (values < lower_bound) | (values > upper_bound)
                    ).astype(int)
                
                elif method == 'zscore':
                    # Z-score method
                    mean_val = values.mean()
                    std_val = values.std()
                    if std_val > 0:
                        z_scores = np.abs((values - mean_val) / std_val)
                        data_copy[anomaly_col] = (z_scores > threshold).astype(int)
                    else:
                        data_copy[anomaly_col] = 0
                
                else:
                    self.logger.warning(f"Unknown anomaly detection method: {method}")
                    data_copy[anomaly_col] = 0
            
            # Count total anomalies
            anomaly_columns = [col for col in data_copy.columns if col.endswith('_anomaly')]
            if anomaly_columns:
                data_copy['total_anomalies'] = data_copy[anomaly_columns].sum(axis=1)
            
            return data_copy
            
        except Exception as e:
            self.logger.error(f"Failed to detect anomalies: {e}")
            return data
    
    def aggregate_data(
        self,
        data: pd.DataFrame,
        groupby_columns: List[str],
        value_columns: List[str],
        agg_functions: Dict[str, Union[str, List[str]]] = None
    ) -> pd.DataFrame:
        """
        Aggregate data by specified columns.
        
        Args:
            data: Input DataFrame
            groupby_columns: Columns to group by
            value_columns: Columns to aggregate
            agg_functions: Aggregation functions to apply
            
        Returns:
            Aggregated DataFrame
        """
        if data.empty:
            return data
        
        if agg_functions is None:
            agg_functions = {col: ['mean', 'sum', 'min', 'max', 'std'] for col in value_columns}
        
        self.logger.info(f"Aggregating data by {groupby_columns}")
        
        try:
            # Filter out columns that don't exist
            valid_groupby = [col for col in groupby_columns if col in data.columns]
            valid_value_cols = [col for col in value_columns if col in data.columns]
            
            if not valid_groupby or not valid_value_cols:
                self.logger.warning("No valid columns for aggregation")
                return data
            
            # Perform aggregation
            agg_data = data.groupby(valid_groupby)[valid_value_cols].agg(agg_functions)
            
            # Flatten column names if multi-level
            if isinstance(agg_data.columns, pd.MultiIndex):
                agg_data.columns = ['_'.join(col).strip() for col in agg_data.columns.values]
            
            # Reset index to make groupby columns regular columns
            agg_data = agg_data.reset_index()
            
            self.logger.info(f"Aggregated data: {len(agg_data)} records")
            return agg_data
            
        except Exception as e:
            self.logger.error(f"Failed to aggregate data: {e}")
            return data
    
    def filter_data(
        self,
        data: pd.DataFrame,
        filters: Dict[str, any] = None,
        date_range: Tuple[str, str] = None,
        keywords: List[str] = None
    ) -> pd.DataFrame:
        """
        Filter data based on various criteria.
        
        Args:
            data: Input DataFrame
            filters: Dictionary of column filters
            date_range: Tuple of (start_date, end_date) strings
            keywords: Keywords to include
            
        Returns:
            Filtered DataFrame
        """
        if data.empty:
            return data
        
        filtered_data = data.copy()
        
        self.logger.info("Applying data filters")
        
        try:
            # Apply date range filter
            if date_range and 'date' in filtered_data.columns:
                start_date, end_date = date_range
                mask = (
                    (filtered_data['date'] >= start_date) & 
                    (filtered_data['date'] <= end_date)
                )
                filtered_data = filtered_data[mask]
                self.logger.info(f"Applied date filter: {start_date} to {end_date}")
            
            # Apply keyword filter
            if keywords:
                keyword_columns = [col for col in filtered_data.columns 
                                 if any(keyword in col for keyword in keywords)]
                if keyword_columns:
                    keep_columns = (['date'] + keyword_columns + 
                                  [col for col in filtered_data.columns 
                                   if not any(kw in col for kw in filtered_data.columns 
                                            if kw.endswith(('_daily', '_monthly')))])
                    keep_columns = list(set(keep_columns))  # Remove duplicates
                    filtered_data = filtered_data[
                        [col for col in keep_columns if col in filtered_data.columns]
                    ]
            
            # Apply custom filters
            if filters:
                for column, value in filters.items():
                    if column in filtered_data.columns:
                        if isinstance(value, (list, tuple)):
                            filtered_data = filtered_data[filtered_data[column].isin(value)]
                        else:
                            filtered_data = filtered_data[filtered_data[column] == value]
                        self.logger.info(f"Applied filter: {column} = {value}")
            
            self.logger.info(f"Filtered data: {len(filtered_data)} records")
            return filtered_data
            
        except Exception as e:
            self.logger.error(f"Failed to filter data: {e}")
            return data
    
    def add_metadata(
        self,
        data: pd.DataFrame,
        metadata: Dict[str, any] = None
    ) -> pd.DataFrame:
        """
        Add metadata columns to the DataFrame.
        
        Args:
            data: Input DataFrame
            metadata: Dictionary of metadata to add
            
        Returns:
            DataFrame with metadata columns
        """
        if data.empty:
            return data
        
        data_copy = data.copy()
        
        # Default metadata
        default_metadata = {
            'processed_date': datetime.now(),
            'processor_version': '1.0.0'
        }
        
        if metadata:
            default_metadata.update(metadata)
        
        # Add metadata columns
        for key, value in default_metadata.items():
            data_copy[key] = value
        
        self.logger.info(f"Added metadata: {list(default_metadata.keys())}")
        return data_copy