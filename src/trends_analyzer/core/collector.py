"""Data collection module for Google Trends API."""

import time
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from pytrends.request import TrendReq
from dateutil.relativedelta import relativedelta

from ..utils.logger import get_logger
from ..utils.validators import validate_keywords, validate_geo, validate_timeframe


class DataCollector:
    """Handles data collection from Google Trends API."""
    
    def __init__(
        self,
        retry_attempts: int = 5,
        delay_between_requests: float = 1.0,
        timeout: int = 30,
        geo: str = 'US'
    ):
        """
        Initialize the data collector.
        
        Args:
            retry_attempts: Number of retry attempts for failed requests
            delay_between_requests: Delay between API requests in seconds
            timeout: Request timeout in seconds
            geo: Default geographic region
        """
        self.retry_attempts = retry_attempts
        self.delay_between_requests = delay_between_requests
        self.timeout = timeout
        self.default_geo = geo
        self.logger = get_logger(__name__)
        self._pytrends = None
    
    @property
    def pytrends(self) -> TrendReq:
        """Lazy initialization of pytrends client."""
        if self._pytrends is None:
            self._pytrends = TrendReq(
                hl='en-US',
                tz=360,
                timeout=self.timeout,
                retries=2,
                backoff_factor=0.1
            )
        return self._pytrends
    
    def collect_interest_over_time(
        self,
        keywords: List[str],
        timeframe: str,
        geo: str = None
    ) -> pd.DataFrame:
        """
        Collect interest over time data for given keywords.
        
        Args:
            keywords: List of keywords to analyze
            timeframe: Time range for data collection
            geo: Geographic region (uses default if None)
            
        Returns:
            DataFrame with interest over time data
            
        Raises:
            Exception: If data collection fails after all retries
        """
        keywords = validate_keywords(keywords)
        timeframe = validate_timeframe(timeframe)
        geo = validate_geo(geo or self.default_geo)
        
        self.logger.info(
            "Collecting interest over time",
            keywords=keywords,
            timeframe=timeframe,
            geo=geo
        )
        
        for attempt in range(self.retry_attempts):
            try:
                # Add delay between requests
                if attempt > 0:
                    time.sleep(self.delay_between_requests * (2 ** attempt))
                
                self.pytrends.build_payload(
                    kw_list=keywords,
                    timeframe=timeframe,
                    geo=geo
                )
                
                data = self.pytrends.interest_over_time()
                
                if data is not None and not data.empty:
                    # Clean up the data
                    data = data.reset_index()
                    if 'isPartial' in data.columns:
                        data = data.drop('isPartial', axis=1)
                    
                    # Add metadata columns
                    data['geo'] = geo
                    data['timeframe'] = timeframe
                    data['collection_date'] = datetime.now()
                    
                    self.logger.info(
                        "Successfully collected data",
                        records=len(data),
                        keywords=keywords
                    )
                    
                    return data
                else:
                    self.logger.warning(f"Empty data returned for attempt {attempt + 1}")
                    
            except Exception as e:
                self.logger.warning(
                    f"Attempt {attempt + 1} failed",
                    error=str(e),
                    keywords=keywords
                )
                
                if attempt == self.retry_attempts - 1:
                    self.logger.error(
                        "All retry attempts failed",
                        keywords=keywords,
                        error=str(e)
                    )
                    raise Exception(f"Failed to collect data after {self.retry_attempts} attempts: {e}")
        
        return pd.DataFrame()
    
    def collect_daily_data(
        self,
        keywords: List[str],
        time_ranges: List[str],
        geo: str = None
    ) -> pd.DataFrame:
        """
        Collect daily data across multiple time ranges.
        
        Args:
            keywords: List of keywords to analyze
            time_ranges: List of time range strings
            geo: Geographic region
            
        Returns:
            Combined DataFrame with daily data
        """
        geo = geo or self.default_geo
        all_data = []
        
        self.logger.info(
            "Collecting daily data",
            keywords=keywords,
            time_ranges_count=len(time_ranges),
            geo=geo
        )
        
        for i, timerange in enumerate(time_ranges):
            self.logger.info(f"Processing time range {i+1}/{len(time_ranges)}: {timerange}")
            
            # Skip future dates
            try:
                start_date_str = timerange.split()[0]
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                if start_date > datetime.now():
                    self.logger.info(f"Skipping future date range: {timerange}")
                    continue
            except (ValueError, IndexError):
                self.logger.warning(f"Invalid timerange format: {timerange}")
                continue
            
            try:
                data = self.collect_interest_over_time(keywords, timerange, geo)
                if not data.empty:
                    all_data.append(data)
                    
                # Add delay between time range requests
                time.sleep(self.delay_between_requests)
                
            except Exception as e:
                self.logger.error(f"Failed to collect data for timerange {timerange}: {e}")
                continue
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            
            # Add derived columns
            if 'date' in combined_data.columns:
                combined_data['month'] = pd.to_datetime(combined_data['date']).dt.month
                combined_data['year'] = pd.to_datetime(combined_data['date']).dt.year
                combined_data['day_of_week'] = pd.to_datetime(combined_data['date']).dt.dayofweek
            
            self.logger.info(f"Combined daily data: {len(combined_data)} records")
            return combined_data
        
        return pd.DataFrame()
    
    def collect_monthly_data(
        self,
        keywords: List[str],
        geo: str = None,
        since_date: str = '2021-01-01'
    ) -> pd.DataFrame:
        """
        Collect monthly data for all time.
        
        Args:
            keywords: List of keywords to analyze
            geo: Geographic region
            since_date: Start date for filtering data
            
        Returns:
            DataFrame with monthly data
        """
        geo = geo or self.default_geo
        keywords = validate_keywords(keywords)
        
        self.logger.info(
            "Collecting monthly data",
            keywords=keywords,
            geo=geo,
            since_date=since_date
        )
        
        for attempt in range(self.retry_attempts):
            try:
                # Add delay between requests
                if attempt > 0:
                    time.sleep(self.delay_between_requests * (2 ** attempt))
                
                self.pytrends.build_payload(
                    kw_list=keywords,
                    timeframe='all',
                    geo=geo
                )
                
                data = self.pytrends.interest_over_time()
                
                if data is not None and not data.empty:
                    data = data.reset_index()
                    
                    # Remove isPartial column
                    if 'isPartial' in data.columns:
                        data = data.drop('isPartial', axis=1)
                    
                    # Filter by date
                    if since_date:
                        data = data[data['date'] >= since_date]
                    
                    # Rename keyword columns to indicate monthly data
                    for keyword in keywords:
                        if keyword in data.columns:
                            data = data.rename(columns={keyword: f'{keyword}_monthly'})
                    
                    # Add derived columns
                    if 'date' in data.columns:
                        data['month'] = pd.to_datetime(data['date']).dt.month
                        data['year'] = pd.to_datetime(data['date']).dt.year
                    
                    # Add metadata
                    data['geo'] = geo
                    data['collection_date'] = datetime.now()
                    
                    self.logger.info(f"Successfully collected monthly data: {len(data)} records")
                    return data
                
            except Exception as e:
                self.logger.warning(f"Monthly data attempt {attempt + 1} failed: {e}")
                
                if attempt == self.retry_attempts - 1:
                    self.logger.error(f"Failed to collect monthly data: {e}")
                    raise Exception(f"Failed to collect monthly data after {self.retry_attempts} attempts: {e}")
        
        return pd.DataFrame()
    
    def generate_monthly_periods(
        self,
        since_date: str,
        end_date: Optional[str] = None
    ) -> List[str]:
        """
        Generate list of monthly periods for data collection.
        
        Args:
            since_date: Start date (YYYY-MM-DD format)
            end_date: End date (defaults to today)
            
        Returns:
            List of time range strings for monthly periods
        """
        if end_date is None:
            end_date = date.today().strftime("%Y-%m-%d")
        
        try:
            periods = pd.date_range(
                since_date,
                end_date,
                freq='MS'  # Month start frequency
            ).strftime("%Y-%m-%d").tolist()
            
            time_ranges = []
            for i in range(len(periods)):
                first_date = periods[i]
                
                # Calculate last day of the month
                first_dt = datetime.strptime(first_date, "%Y-%m-%d")
                last_dt = first_dt + relativedelta(months=1) - relativedelta(days=1)
                last_date = last_dt.strftime("%Y-%m-%d")
                
                time_ranges.append(f"{first_date} {last_date}")
            
            self.logger.info(f"Generated {len(time_ranges)} monthly periods")
            return time_ranges
            
        except Exception as e:
            self.logger.error(f"Failed to generate monthly periods: {e}")
            raise
    
    def get_related_queries(
        self,
        keywords: List[str],
        timeframe: str = 'today 12-m',
        geo: str = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Get related queries for keywords.
        
        Args:
            keywords: List of keywords to analyze
            timeframe: Time range for analysis
            geo: Geographic region
            
        Returns:
            Dictionary mapping keywords to related queries DataFrames
        """
        geo = geo or self.default_geo
        keywords = validate_keywords(keywords)
        
        self.logger.info("Collecting related queries", keywords=keywords)
        
        try:
            self.pytrends.build_payload(
                kw_list=keywords,
                timeframe=timeframe,
                geo=geo
            )
            
            related_queries = self.pytrends.related_queries()
            
            # Process the results
            results = {}
            for keyword in keywords:
                if keyword in related_queries:
                    keyword_data = related_queries[keyword]
                    if keyword_data is not None:
                        results[keyword] = {
                            'top': keyword_data.get('top', pd.DataFrame()),
                            'rising': keyword_data.get('rising', pd.DataFrame())
                        }
            
            self.logger.info(f"Collected related queries for {len(results)} keywords")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to collect related queries: {e}")
            return {}
    
    def get_related_topics(
        self,
        keywords: List[str],
        timeframe: str = 'today 12-m',
        geo: str = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Get related topics for keywords.
        
        Args:
            keywords: List of keywords to analyze
            timeframe: Time range for analysis
            geo: Geographic region
            
        Returns:
            Dictionary mapping keywords to related topics DataFrames
        """
        geo = geo or self.default_geo
        keywords = validate_keywords(keywords)
        
        self.logger.info("Collecting related topics", keywords=keywords)
        
        try:
            self.pytrends.build_payload(
                kw_list=keywords,
                timeframe=timeframe,
                geo=geo
            )
            
            related_topics = self.pytrends.related_topics()
            
            # Process the results
            results = {}
            for keyword in keywords:
                if keyword in related_topics:
                    keyword_data = related_topics[keyword]
                    if keyword_data is not None:
                        results[keyword] = {
                            'top': keyword_data.get('top', pd.DataFrame()),
                            'rising': keyword_data.get('rising', pd.DataFrame())
                        }
            
            self.logger.info(f"Collected related topics for {len(results)} keywords")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to collect related topics: {e}")
            return {}