#!/usr/bin/env python3
"""
Advanced usage examples for Google Trends Analyzer.

This script demonstrates advanced features and customization options.
"""

import pandas as pd
from datetime import datetime, timedelta
from trends_analyzer import TrendsAnalyzer, Config
from trends_analyzer.exporters import BigQueryExporter, JSONExporter
from trends_analyzer.core import DataProcessor


def custom_configuration():
    """Example 1: Using custom configuration."""
    print("⚙️ Example 1: Custom configuration")
    
    # Create custom configuration
    config = Config()
    config.analyzer.default_geo = 'GB'
    config.analyzer.retry_attempts = 10
    config.analyzer.delay_between_requests = 2.0
    config.logging.level = 'DEBUG'
    
    # Initialize analyzer with custom config
    analyzer = TrendsAnalyzer(config=config)
    
    data = analyzer.get_trends(
        keywords=['brexit'],
        timeframe='today 5-y'
    )
    
    print(f"Retrieved {len(data)} records with custom config")
    return data


def advanced_data_processing():
    """Example 2: Advanced data processing and analysis."""
    print("\n🔬 Example 2: Advanced data processing")
    
    analyzer = TrendsAnalyzer()
    processor = DataProcessor()
    
    # Get comprehensive data
    results = analyzer.get_comprehensive_analysis(
        keywords=['electric vehicles'],
        geo='US',
        since_date='2020-01-01'
    )
    
    if 'comprehensive' in results:
        data = results['comprehensive']
        
        # Apply advanced processing
        value_columns = [col for col in data.columns if col.endswith('_daily')]
        
        # Normalize data
        normalized_data = processor.normalize_data(
            data=data,
            columns=value_columns,
            method='zscore'
        )
        
        # Detect anomalies
        anomaly_data = processor.detect_anomalies(
            data=normalized_data,
            value_columns=value_columns,
            method='iqr',
            threshold=2.0
        )
        
        # Aggregate by month
        monthly_agg = processor.aggregate_data(
            data=anomaly_data,
            groupby_columns=['year', 'month'],
            value_columns=value_columns,
            agg_functions={col: ['mean', 'max', 'std'] for col in value_columns}
        )
        
        print(f"Processed data: {len(anomaly_data)} records")
        print(f"Monthly aggregation: {len(monthly_agg)} records")
        
        # Export processed data
        exporter = JSONExporter()
        exporter.export_structured(anomaly_data, 'ev_processed')
        exporter.export_structured(monthly_agg, 'ev_monthly_agg')
        
        return anomaly_data, monthly_agg


def bigquery_integration():
    """Example 3: BigQuery integration."""
    print("\n☁️ Example 3: BigQuery integration")
    
    # Note: This requires Google Cloud credentials
    try:
        analyzer = TrendsAnalyzer()
        
        # Get trends data
        data = analyzer.get_trends(
            keywords=['sustainable technology'],
            timeframe='today 12-m',
            geo='US'
        )
        
        # Export to BigQuery (requires credentials)
        # exporter = BigQueryExporter(
        #     project_id='your-project-id',
        #     dataset_id='trends_analysis',
        #     table_name='sustainable_tech_trends'
        # )
        # 
        # table_ref = exporter.export(data)
        # print(f"Data exported to BigQuery table: {table_ref}")
        
        print("BigQuery integration example (requires credentials setup)")
        return data
        
    except Exception as e:
        print(f"BigQuery example skipped: {e}")
        return None


def time_series_analysis():
    """Example 4: Time series analysis with trend detection."""
    print("\n📊 Example 4: Time series analysis")
    
    analyzer = TrendsAnalyzer()
    processor = DataProcessor()
    
    # Get daily data for detailed time series analysis
    data = analyzer.get_daily_trends(
        keywords=['climate change'],
        since_date='2021-01-01',
        geo='US'
    )
    
    if not data.empty:
        # Extract value columns
        value_columns = [col for col in data.columns 
                        if any(keyword in col for keyword in ['climate change']) 
                        and not col.endswith(('_ma_7', '_std_7', '_pct_change'))]
        
        # Calculate additional trend indicators
        enhanced_data = processor.calculate_trends(
            data=data,
            value_columns=value_columns,
            window_size=14  # 2-week window
        )
        
        # Detect seasonal patterns (simplified)
        if 'date' in enhanced_data.columns:
            enhanced_data['date'] = pd.to_datetime(enhanced_data['date'])
            enhanced_data['month'] = enhanced_data['date'].dt.month
            enhanced_data['quarter'] = enhanced_data['date'].dt.quarter
            enhanced_data['day_of_year'] = enhanced_data['date'].dt.dayofyear
        
        # Calculate seasonal averages
        seasonal_stats = processor.aggregate_data(
            data=enhanced_data,
            groupby_columns=['month'],
            value_columns=value_columns,
            agg_functions={col: ['mean', 'std'] for col in value_columns}
        )
        
        print(f"Time series data: {len(enhanced_data)} records")
        print(f"Seasonal patterns: {len(seasonal_stats)} months")
        
        # Export time series analysis
        exporter = JSONExporter()
        exporter.export_structured(enhanced_data, 'climate_timeseries')
        exporter.export_structured(seasonal_stats, 'climate_seasonal')
        
        return enhanced_data, seasonal_stats


def market_research_workflow():
    """Example 5: Complete market research workflow."""
    print("\n📈 Example 5: Market research workflow")
    
    analyzer = TrendsAnalyzer()
    
    # Define market research parameters
    base_keyword = 'plant based meat'
    competitor_keywords = [
        'beyond meat',
        'impossible burger',
        'plant based protein',
        'meat alternatives'
    ]
    
    all_keywords = [base_keyword] + competitor_keywords
    
    # Step 1: Get comprehensive market data
    print("Step 1: Collecting market trends...")
    market_results = {}
    
    for keyword in all_keywords:
        print(f"  Analyzing: {keyword}")
        
        data = analyzer.get_comprehensive_analysis(
            keywords=[keyword],
            geo='US',
            since_date='2020-01-01',
            include_related=True
        )
        
        market_results[keyword] = data
    
    # Step 2: Compare all keywords
    print("Step 2: Comparing keywords...")
    comparison_data = analyzer.compare_keywords(
        keywords=all_keywords,
        timeframe='today 3-y',
        geo='US',
        normalize=True
    )
    
    # Step 3: Regional analysis
    print("Step 3: Regional analysis...")
    regions = ['US', 'CA', 'GB', 'AU']
    regional_results = {}
    
    for region in regions:
        regional_data = analyzer.get_trends(
            keywords=[base_keyword],
            timeframe='today 2-y',
            geo=region
        )
        regional_results[region] = regional_data
    
    # Step 4: Export comprehensive market research
    print("Step 4: Exporting results...")
    exporter = JSONExporter(output_dir='./market_research')
    
    # Export market results
    for keyword, results in market_results.items():
        safe_name = keyword.replace(' ', '_')
        exporter.export_analysis_results(results, f'market_{safe_name}')
    
    # Export comparison and regional data
    exporter.export_structured(comparison_data, 'keyword_comparison')
    exporter.export_multiple(regional_results, 'regional_analysis')
    
    print("Market research workflow completed!")
    return market_results, comparison_data, regional_results


def custom_filtering_and_analysis():
    """Example 6: Custom data filtering and analysis."""
    print("\n🔍 Example 6: Custom filtering and analysis")
    
    analyzer = TrendsAnalyzer()
    processor = DataProcessor()
    
    # Get data for analysis
    data = analyzer.get_daily_trends(
        keywords=['renewable energy'],
        since_date='2021-01-01',
        geo='US'
    )
    
    if not data.empty:
        # Apply custom filters
        # Filter 1: Last 6 months only
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_data = processor.filter_data(
            data=data,
            date_range=(six_months_ago.strftime('%Y-%m-%d'), 
                       datetime.now().strftime('%Y-%m-%d'))
        )
        
        # Filter 2: High interest periods (above median)
        value_cols = [col for col in data.columns if 'renewable energy' in col]
        if value_cols:
            median_value = data[value_cols[0]].median()
            high_interest = processor.filter_data(
                data=data,
                filters={value_cols[0]: lambda x: x > median_value}
            )
        
        # Custom analysis: Find peak periods
        if value_cols and 'date' in data.columns:
            data_sorted = data.sort_values(value_cols[0], ascending=False)
            top_10_periods = data_sorted.head(10)[['date'] + value_cols]
            
            print("Top 10 peak interest periods:")
            print(top_10_periods.to_string())
        
        # Export filtered results
        exporter = JSONExporter()
        exporter.export_structured(recent_data, 'renewable_recent')
        
        return recent_data


if __name__ == '__main__':
    print("🚀 Google Trends Analyzer - Advanced Examples")
    print("=" * 60)
    
    try:
        # Run advanced examples
        custom_configuration()
        advanced_data_processing()
        bigquery_integration()
        time_series_analysis()
        market_research_workflow()
        custom_filtering_and_analysis()
        
        print("\n✅ All advanced examples completed!")
        print("📁 Check output directories for results.")
        
    except Exception as e:
        print(f"\n❌ Error running advanced examples: {e}")
        raise