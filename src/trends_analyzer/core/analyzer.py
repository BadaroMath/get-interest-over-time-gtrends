"""Main analyzer class for Google Trends analysis."""

import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional, Union, Tuple
from pathlib import Path

from .collector import DataCollector
from .processor import DataProcessor
from ..utils.config import Config
from ..utils.logger import setup_logger, get_logger
from ..utils.validators import validate_keywords, validate_geo, validate_timeframe


class TrendsAnalyzer:
    """
    Main class for Google Trends analysis.
    
    This class provides a high-level interface for collecting, processing,
    and analyzing Google Trends data.
    """
    
    def __init__(
        self,
        config: Optional[Union[Config, str, Dict]] = None,
        geo: str = 'US',
        retry_attempts: int = 5,
        delay_between_requests: float = 1.0
    ):
        """
        Initialize the TrendsAnalyzer.
        
        Args:
            config: Configuration object, file path, or dictionary
            geo: Default geographic region
            retry_attempts: Number of retry attempts for failed requests
            delay_between_requests: Delay between requests in seconds
        """
        # Load configuration
        if isinstance(config, str):
            self.config = Config(config)
        elif isinstance(config, dict):
            self.config = Config.from_dict(config)
        elif isinstance(config, Config):
            self.config = config
        else:
            self.config = Config()
        
        # Override config with provided parameters
        if geo != 'US':
            self.config.analyzer.default_geo = geo
        if retry_attempts != 5:
            self.config.analyzer.retry_attempts = retry_attempts
        if delay_between_requests != 1.0:
            self.config.analyzer.delay_between_requests = delay_between_requests
        
        # Set up logging
        self.logger = setup_logger(
            level=self.config.logging.level,
            log_file=self.config.logging.file,
            console=self.config.logging.console
        )
        self.struct_logger = get_logger(__name__)
        
        # Initialize components
        self.collector = DataCollector(
            retry_attempts=self.config.analyzer.retry_attempts,
            delay_between_requests=self.config.analyzer.delay_between_requests,
            timeout=self.config.analyzer.timeout,
            geo=self.config.analyzer.default_geo
        )
        
        self.processor = DataProcessor()
        
        # Create cache directory if needed
        if self.config.analyzer.cache_enabled:
            cache_dir = Path(self.config.analyzer.cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.struct_logger.info("TrendsAnalyzer initialized", 
                               geo=self.config.analyzer.default_geo,
                               cache_enabled=self.config.analyzer.cache_enabled)
    
    @classmethod
    def from_config(cls, config_path: str) -> 'TrendsAnalyzer':
        """
        Create TrendsAnalyzer from configuration file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configured TrendsAnalyzer instance
        """
        return cls(config=config_path)
    
    def get_trends(
        self,
        keywords: Union[str, List[str]],
        timeframe: str = None,
        geo: str = None,
        include_related: bool = False
    ) -> pd.DataFrame:
        """
        Get basic trends data for keywords.
        
        Args:
            keywords: Keyword or list of keywords to analyze
            timeframe: Time range for analysis
            geo: Geographic region
            include_related: Whether to include related queries/topics
            
        Returns:
            DataFrame with trends data
        """
        # Validate and normalize inputs
        keywords = validate_keywords(keywords)
        timeframe = timeframe or self.config.analyzer.default_timeframe
        geo = geo or self.config.analyzer.default_geo
        
        timeframe = validate_timeframe(timeframe)
        geo = validate_geo(geo)
        
        self.struct_logger.info(
            "Getting trends data",
            keywords=keywords,
            timeframe=timeframe,
            geo=geo
        )
        
        try:
            # Collect interest over time data
            data = self.collector.collect_interest_over_time(
                keywords=keywords,
                timeframe=timeframe,
                geo=geo
            )
            
            if data.empty:
                self.struct_logger.warning("No data returned from API")
                return data
            
            # Add metadata
            data = self.processor.add_metadata(data, {
                'keywords': keywords,
                'timeframe': timeframe,
                'geo': geo,
                'analysis_type': 'basic_trends'
            })
            
            # Collect related data if requested
            if include_related:
                related_queries = self.collector.get_related_queries(keywords, timeframe, geo)
                related_topics = self.collector.get_related_topics(keywords, timeframe, geo)
                
                # Store as attributes for later access
                data.attrs['related_queries'] = related_queries
                data.attrs['related_topics'] = related_topics
            
            self.struct_logger.info("Successfully retrieved trends data", 
                                   records=len(data))
            return data
            
        except Exception as e:
            self.struct_logger.error("Failed to get trends data", error=str(e))
            raise
    
    def get_daily_trends(
        self,
        keywords: Union[str, List[str]],
        timeframe: str = None,
        geo: str = None,
        since_date: str = None
    ) -> pd.DataFrame:
        """
        Get detailed daily trends data.
        
        Args:
            keywords: Keyword or list of keywords to analyze
            timeframe: Time range for analysis (or use since_date)
            geo: Geographic region
            since_date: Start date for data collection (YYYY-MM-DD)
            
        Returns:
            DataFrame with daily trends data
        """
        keywords = validate_keywords(keywords)
        geo = geo or self.config.analyzer.default_geo
        geo = validate_geo(geo)
        
        self.struct_logger.info(
            "Getting daily trends data",
            keywords=keywords,
            timeframe=timeframe,
            geo=geo,
            since_date=since_date
        )
        
        try:
            if since_date:
                # Generate monthly periods for detailed collection
                time_ranges = self.collector.generate_monthly_periods(
                    since_date=since_date
                )
                
                # Collect daily data across all periods
                daily_data = self.collector.collect_daily_data(
                    keywords=keywords,
                    time_ranges=time_ranges,
                    geo=geo
                )
            else:
                # Use provided timeframe
                timeframe = timeframe or self.config.analyzer.default_timeframe
                timeframe = validate_timeframe(timeframe)
                
                daily_data = self.collector.collect_interest_over_time(
                    keywords=keywords,
                    timeframe=timeframe,
                    geo=geo
                )
            
            if daily_data.empty:
                self.struct_logger.warning("No daily data returned")
                return daily_data
            
            # Calculate trend indicators
            value_columns = [col for col in daily_data.columns 
                           if col in keywords or col.endswith('_daily')]
            
            if value_columns:
                daily_data = self.processor.calculate_trends(
                    data=daily_data,
                    value_columns=value_columns
                )
            
            # Add metadata
            daily_data = self.processor.add_metadata(daily_data, {
                'keywords': keywords,
                'geo': geo,
                'analysis_type': 'daily_trends',
                'since_date': since_date
            })
            
            self.struct_logger.info("Successfully retrieved daily trends", 
                                   records=len(daily_data))
            return daily_data
            
        except Exception as e:
            self.struct_logger.error("Failed to get daily trends", error=str(e))
            raise
    
    def get_monthly_trends(
        self,
        keywords: Union[str, List[str]],
        geo: str = None,
        since_date: str = '2021-01-01'
    ) -> pd.DataFrame:
        """
        Get monthly trends data.
        
        Args:
            keywords: Keyword or list of keywords to analyze
            geo: Geographic region
            since_date: Start date for data collection
            
        Returns:
            DataFrame with monthly trends data
        """
        keywords = validate_keywords(keywords)
        geo = geo or self.config.analyzer.default_geo
        geo = validate_geo(geo)
        
        self.struct_logger.info(
            "Getting monthly trends data",
            keywords=keywords,
            geo=geo,
            since_date=since_date
        )
        
        try:
            monthly_data = self.collector.collect_monthly_data(
                keywords=keywords,
                geo=geo,
                since_date=since_date
            )
            
            if monthly_data.empty:
                self.struct_logger.warning("No monthly data returned")
                return monthly_data
            
            # Calculate trend indicators for monthly data
            value_columns = [col for col in monthly_data.columns 
                           if col.endswith('_monthly')]
            
            if value_columns:
                monthly_data = self.processor.calculate_trends(
                    data=monthly_data,
                    value_columns=value_columns,
                    window_size=3  # 3-month window for monthly data
                )
            
            # Add metadata
            monthly_data = self.processor.add_metadata(monthly_data, {
                'keywords': keywords,
                'geo': geo,
                'analysis_type': 'monthly_trends',
                'since_date': since_date
            })
            
            self.struct_logger.info("Successfully retrieved monthly trends", 
                                   records=len(monthly_data))
            return monthly_data
            
        except Exception as e:
            self.struct_logger.error("Failed to get monthly trends", error=str(e))
            raise
    
    def get_comprehensive_analysis(
        self,
        keywords: Union[str, List[str]],
        geo: str = None,
        since_date: str = None,
        include_related: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Get comprehensive analysis combining daily, monthly, and related data.
        
        Args:
            keywords: Keyword or list of keywords to analyze
            geo: Geographic region
            since_date: Start date for data collection
            include_related: Whether to include related queries/topics
            
        Returns:
            Dictionary containing different analysis results
        """
        keywords = validate_keywords(keywords)
        geo = geo or self.config.analyzer.default_geo
        since_date = since_date or '2021-01-01'
        
        self.struct_logger.info(
            "Starting comprehensive analysis",
            keywords=keywords,
            geo=geo,
            since_date=since_date
        )
        
        results = {}
        
        try:
            # Generate time ranges for daily data
            time_ranges = self.collector.generate_monthly_periods(since_date)
            
            # Collect daily data
            daily_data = self.collector.collect_daily_data(
                keywords=keywords,
                time_ranges=time_ranges,
                geo=geo
            )
            
            # Collect monthly data
            monthly_data = self.collector.collect_monthly_data(
                keywords=keywords,
                geo=geo,
                since_date=since_date
            )
            
            # Merge daily and monthly data
            if not daily_data.empty and not monthly_data.empty:
                merged_data = self.processor.merge_daily_monthly(
                    daily_data=daily_data,
                    monthly_data=monthly_data,
                    keywords=keywords
                )
                
                # Calculate comprehensive trend indicators
                value_columns = [col for col in merged_data.columns 
                               if col.endswith('_daily')]
                
                if value_columns:
                    merged_data = self.processor.calculate_trends(
                        data=merged_data,
                        value_columns=value_columns
                    )
                    
                    # Detect anomalies
                    merged_data = self.processor.detect_anomalies(
                        data=merged_data,
                        value_columns=value_columns
                    )
                
                results['comprehensive'] = merged_data
            
            # Store individual datasets
            results['daily'] = daily_data
            results['monthly'] = monthly_data
            
            # Collect related data if requested
            if include_related:
                related_queries = self.collector.get_related_queries(
                    keywords=keywords,
                    geo=geo
                )
                related_topics = self.collector.get_related_topics(
                    keywords=keywords,
                    geo=geo
                )
                
                results['related_queries'] = related_queries
                results['related_topics'] = related_topics
            
            self.struct_logger.info("Comprehensive analysis completed")
            return results
            
        except Exception as e:
            self.struct_logger.error("Failed comprehensive analysis", error=str(e))
            raise
    
    def analyze_batch(
        self,
        keyword_list: List[str],
        geo: str = None,
        timeframe: str = None,
        batch_size: int = 5
    ) -> Dict[str, pd.DataFrame]:
        """
        Analyze multiple keywords in batches.
        
        Args:
            keyword_list: List of keywords to analyze
            geo: Geographic region
            timeframe: Time range for analysis
            batch_size: Number of keywords per batch (max 5 for Google Trends)
            
        Returns:
            Dictionary mapping keywords to their trend data
        """
        geo = geo or self.config.analyzer.default_geo
        timeframe = timeframe or self.config.analyzer.default_timeframe
        
        # Validate batch size
        if batch_size > 5:
            batch_size = 5
            self.struct_logger.warning("Batch size limited to 5 for Google Trends API")
        
        self.struct_logger.info(
            "Starting batch analysis",
            total_keywords=len(keyword_list),
            batch_size=batch_size
        )
        
        results = {}
        
        try:
            # Process keywords in batches
            for i in range(0, len(keyword_list), batch_size):
                batch_keywords = keyword_list[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                
                self.struct_logger.info(f"Processing batch {batch_num}", 
                                       keywords=batch_keywords)
                
                # Get trends for this batch
                batch_data = self.get_trends(
                    keywords=batch_keywords,
                    timeframe=timeframe,
                    geo=geo
                )
                
                # Store results for each keyword
                for keyword in batch_keywords:
                    if keyword in batch_data.columns:
                        keyword_data = batch_data[['date', keyword]].copy()
                        keyword_data = self.processor.add_metadata(keyword_data, {
                            'keyword': keyword,
                            'batch_number': batch_num
                        })
                        results[keyword] = keyword_data
            
            self.struct_logger.info(f"Batch analysis completed: {len(results)} keywords")
            return results
            
        except Exception as e:
            self.struct_logger.error("Failed batch analysis", error=str(e))
            raise
    
    def compare_keywords(
        self,
        keywords: List[str],
        timeframe: str = None,
        geo: str = None,
        normalize: bool = True
    ) -> pd.DataFrame:
        """
        Compare multiple keywords side by side.
        
        Args:
            keywords: List of keywords to compare
            timeframe: Time range for comparison
            geo: Geographic region
            normalize: Whether to normalize the data for better comparison
            
        Returns:
            DataFrame with comparison data
        """
        keywords = validate_keywords(keywords)
        timeframe = timeframe or self.config.analyzer.default_timeframe
        geo = geo or self.config.analyzer.default_geo
        
        self.struct_logger.info("Comparing keywords", keywords=keywords)
        
        try:
            # Get trends data for all keywords
            comparison_data = self.get_trends(
                keywords=keywords,
                timeframe=timeframe,
                geo=geo
            )
            
            if comparison_data.empty:
                return comparison_data
            
            # Normalize data if requested
            if normalize:
                comparison_data = self.processor.normalize_data(
                    data=comparison_data,
                    columns=keywords,
                    method='minmax'
                )
            
            # Calculate correlation matrix
            if len(keywords) > 1:
                correlation_matrix = comparison_data[keywords].corr()
                comparison_data.attrs['correlation_matrix'] = correlation_matrix
            
            # Add metadata
            comparison_data = self.processor.add_metadata(comparison_data, {
                'keywords': keywords,
                'analysis_type': 'keyword_comparison',
                'normalized': normalize
            })
            
            self.struct_logger.info("Keyword comparison completed")
            return comparison_data
            
        except Exception as e:
            self.struct_logger.error("Failed keyword comparison", error=str(e))
            raise
    
    def get_summary_stats(
        self,
        data: pd.DataFrame,
        value_columns: List[str] = None
    ) -> pd.DataFrame:
        """
        Generate summary statistics for trends data.
        
        Args:
            data: Input DataFrame
            value_columns: Columns to analyze (auto-detected if None)
            
        Returns:
            DataFrame with summary statistics
        """
        if data.empty:
            return pd.DataFrame()
        
        # Auto-detect value columns if not provided
        if value_columns is None:
            value_columns = [col for col in data.columns 
                           if col not in ['date', 'geo', 'timeframe', 'collection_date',
                                        'processed_date', 'processor_version']]
        
        value_columns = [col for col in value_columns if col in data.columns]
        
        if not value_columns:
            self.struct_logger.warning("No value columns found for summary stats")
            return pd.DataFrame()
        
        try:
            summary_stats = data[value_columns].describe()
            
            # Add additional statistics
            additional_stats = pd.DataFrame({
                col: {
                    'variance': data[col].var(),
                    'skewness': data[col].skew(),
                    'kurtosis': data[col].kurtosis(),
                    'median_abs_deviation': (data[col] - data[col].median()).abs().median()
                } for col in value_columns
            }).T
            
            # Combine all statistics
            summary_stats = pd.concat([summary_stats.T, additional_stats], axis=1)
            
            self.struct_logger.info(f"Generated summary statistics for {len(value_columns)} columns")
            return summary_stats
            
        except Exception as e:
            self.struct_logger.error("Failed to generate summary stats", error=str(e))
            return pd.DataFrame()