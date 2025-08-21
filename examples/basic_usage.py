#!/usr/bin/env python3
"""
Basic usage examples for Google Trends Analyzer.

This script demonstrates the most common use cases for the library.
"""

import pandas as pd
from trends_analyzer import TrendsAnalyzer
from trends_analyzer.exporters import CSVExporter, JSONExporter


def basic_trend_analysis():
    """Example 1: Basic trend analysis for a single keyword."""
    print("🔍 Example 1: Basic trend analysis")
    
    # Initialize analyzer
    analyzer = TrendsAnalyzer()
    
    # Get trends data
    data = analyzer.get_trends(
        keywords=['python programming'],
        timeframe='today 12-m',
        geo='US'
    )
    
    print(f"Retrieved {len(data)} records")
    print(data.head())
    
    # Export to CSV
    exporter = CSVExporter()
    exporter.export(data, 'python_trends')
    
    return data


def multiple_keywords_comparison():
    """Example 2: Compare multiple keywords."""
    print("\n⚖️ Example 2: Keyword comparison")
    
    analyzer = TrendsAnalyzer()
    
    # Compare programming languages
    data = analyzer.compare_keywords(
        keywords=['python', 'javascript', 'java'],
        timeframe='today 5-y',
        geo='',  # Worldwide
        normalize=True
    )
    
    print(f"Comparison data: {len(data)} records")
    
    # Show correlation matrix
    if hasattr(data, 'attrs') and 'correlation_matrix' in data.attrs:
        print("Correlation Matrix:")
        print(data.attrs['correlation_matrix'])
    
    return data


def daily_trends_analysis():
    """Example 3: Detailed daily trends analysis."""
    print("\n📈 Example 3: Daily trends analysis")
    
    analyzer = TrendsAnalyzer()
    
    # Get daily trends with trend indicators
    data = analyzer.get_daily_trends(
        keywords=['artificial intelligence'],
        since_date='2023-01-01',
        geo='US'
    )
    
    print(f"Daily trends: {len(data)} records")
    
    # Show columns with trend indicators
    trend_columns = [col for col in data.columns if 'trend' in col.lower()]
    print(f"Trend indicators: {trend_columns}")
    
    return data


def comprehensive_analysis():
    """Example 4: Comprehensive analysis with all data types."""
    print("\n🔬 Example 4: Comprehensive analysis")
    
    analyzer = TrendsAnalyzer()
    
    # Get comprehensive analysis
    results = analyzer.get_comprehensive_analysis(
        keywords=['machine learning'],
        geo='US',
        since_date='2022-01-01',
        include_related=True
    )
    
    print("Analysis results:")
    for analysis_type, data in results.items():
        if isinstance(data, pd.DataFrame):
            print(f"  {analysis_type}: {len(data)} records")
        else:
            print(f"  {analysis_type}: {type(data)}")
    
    # Export comprehensive results
    exporter = JSONExporter()
    exporter.export_analysis_results(results, 'ml_comprehensive')
    
    return results


def batch_keyword_analysis():
    """Example 5: Batch analysis of multiple keywords."""
    print("\n🔄 Example 5: Batch keyword analysis")
    
    analyzer = TrendsAnalyzer()
    
    # List of tech keywords to analyze
    keywords = [
        'cloud computing',
        'blockchain',
        'quantum computing',
        'edge computing',
        'serverless'
    ]
    
    # Analyze in batches
    results = analyzer.analyze_batch(
        keyword_list=keywords,
        timeframe='today 12-m',
        geo='US',
        batch_size=5
    )
    
    print(f"Analyzed {len(results)} keywords")
    
    # Export each keyword's data
    exporter = CSVExporter(output_dir='./batch_results')
    for keyword, data in results.items():
        safe_filename = keyword.replace(' ', '_')
        exporter.export(data, safe_filename)
    
    return results


def regional_comparison():
    """Example 6: Compare same keyword across regions."""
    print("\n🌍 Example 6: Regional comparison")
    
    analyzer = TrendsAnalyzer()
    
    regions = ['US', 'GB', 'DE', 'JP', 'BR']
    keyword = 'cryptocurrency'
    
    regional_data = {}
    
    for region in regions:
        print(f"Collecting data for {region}...")
        
        data = analyzer.get_trends(
            keywords=[keyword],
            timeframe='today 12-m',
            geo=region
        )
        
        if not data.empty:
            # Rename the keyword column to include region
            data = data.rename(columns={keyword: f'{keyword}_{region}'})
            regional_data[region] = data
    
    print(f"Collected data for {len(regional_data)} regions")
    
    # Export regional comparison
    exporter = JSONExporter()
    exporter.export_multiple(regional_data, f'{keyword}_regional')
    
    return regional_data


if __name__ == '__main__':
    print("🚀 Google Trends Analyzer - Usage Examples")
    print("=" * 50)
    
    try:
        # Run examples
        basic_trend_analysis()
        multiple_keywords_comparison()
        daily_trends_analysis()
        comprehensive_analysis()
        batch_keyword_analysis()
        regional_comparison()
        
        print("\n✅ All examples completed successfully!")
        print("📁 Check the './results' directory for exported files.")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        raise