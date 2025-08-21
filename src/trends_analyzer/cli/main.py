"""Command Line Interface for Google Trends Analyzer."""

import click
import pandas as pd
import json
from pathlib import Path
from typing import List, Optional

from ..core.analyzer import TrendsAnalyzer
from ..exporters.csv_exporter import CSVExporter
from ..exporters.json_exporter import JSONExporter
from ..exporters.bigquery_exporter import BigQueryExporter
from ..utils.config import Config
from ..utils.logger import setup_logger
from ..utils.validators import validate_keywords, validate_geo, validate_timeframe


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--output-dir', '-o', default='./results', help='Output directory')
@click.pass_context
def cli(ctx, config, verbose, output_dir):
    """Google Trends Analyzer - Collect and analyze Google Trends data."""
    ctx.ensure_object(dict)
    
    # Set up logging
    log_level = 'DEBUG' if verbose else 'INFO'
    setup_logger(level=log_level, console=True)
    
    # Load configuration
    if config:
        ctx.obj['config'] = Config(config)
    else:
        ctx.obj['config'] = Config()
    
    ctx.obj['output_dir'] = output_dir
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)


@cli.command()
@click.option('--keyword', '-k', multiple=True, required=True, help='Keywords to analyze (can be used multiple times)')
@click.option('--geo', '-g', default='US', help='Geographic region (e.g., US, GB, DE)')
@click.option('--timeframe', '-t', default='today 3-m', help='Time frame for analysis')
@click.option('--format', '-f', 'output_format', default='csv', 
              type=click.Choice(['csv', 'json', 'bigquery']), help='Output format')
@click.option('--output', help='Output filename (without extension)')
@click.option('--include-related', is_flag=True, help='Include related queries and topics')
@click.pass_context
def analyze(ctx, keyword, geo, timeframe, output_format, output, include_related):
    """Analyze Google Trends for specified keywords."""
    try:
        # Initialize analyzer
        analyzer = TrendsAnalyzer(config=ctx.obj['config'])
        
        # Validate inputs
        keywords = list(keyword)
        keywords = validate_keywords(keywords)
        geo = validate_geo(geo)
        timeframe = validate_timeframe(timeframe)
        
        click.echo(f"🔍 Analyzing trends for: {', '.join(keywords)}")
        click.echo(f"📍 Region: {geo}")
        click.echo(f"📅 Timeframe: {timeframe}")
        
        # Get trends data
        with click.progressbar(length=100, label='Collecting data') as bar:
            bar.update(20)
            data = analyzer.get_trends(
                keywords=keywords,
                timeframe=timeframe,
                geo=geo,
                include_related=include_related
            )
            bar.update(80)
        
        if data.empty:
            click.echo("❌ No data returned. Please check your keywords and parameters.")
            return
        
        # Prepare output filename
        if not output:
            keyword_str = '_'.join(keywords[:3])  # Use first 3 keywords
            output = f"trends_{keyword_str}_{geo}_{timeframe.replace(' ', '_')}"
        
        # Export data
        click.echo(f"💾 Exporting data in {output_format} format...")
        
        if output_format == 'csv':
            exporter = CSVExporter(output_dir=ctx.obj['output_dir'])
            file_path = exporter.export(data, output)
            
        elif output_format == 'json':
            exporter = JSONExporter(output_dir=ctx.obj['output_dir'])
            file_path = exporter.export_structured(data, output)
            
        elif output_format == 'bigquery':
            if not ctx.obj['config'].bigquery.project_id:
                click.echo("❌ BigQuery project_id not configured. Please set GOOGLE_CLOUD_PROJECT environment variable.")
                return
            
            exporter = BigQueryExporter(
                project_id=ctx.obj['config'].bigquery.project_id,
                dataset_id=ctx.obj['config'].bigquery.dataset_id,
                credentials_path=ctx.obj['config'].bigquery.credentials_path,
                credentials_json=ctx.obj['config'].bigquery.credentials_json
            )
            file_path = exporter.export(data, table_name=output.replace('-', '_'))
        
        click.echo(f"✅ Successfully exported to: {file_path}")
        click.echo(f"📊 Records: {len(data)}")
        
        # Show sample data
        if not data.empty:
            click.echo("\n🔍 Sample data:")
            click.echo(data.head().to_string())
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise click.Abort()


@cli.command()
@click.option('--keyword', '-k', multiple=True, required=True, help='Keywords to analyze')
@click.option('--geo', '-g', default='US', help='Geographic region')
@click.option('--since-date', default='2021-01-01', help='Start date (YYYY-MM-DD)')
@click.option('--format', '-f', 'output_format', default='csv',
              type=click.Choice(['csv', 'json', 'bigquery']), help='Output format')
@click.option('--output', help='Output filename base')
@click.pass_context
def daily(ctx, keyword, geo, since_date, output_format, output):
    """Get detailed daily trends data."""
    try:
        analyzer = TrendsAnalyzer(config=ctx.obj['config'])
        keywords = validate_keywords(list(keyword))
        geo = validate_geo(geo)
        
        click.echo(f"📈 Getting daily trends for: {', '.join(keywords)}")
        click.echo(f"📅 Since: {since_date}")
        
        with click.progressbar(length=100, label='Collecting daily data') as bar:
            bar.update(10)
            data = analyzer.get_daily_trends(
                keywords=keywords,
                geo=geo,
                since_date=since_date
            )
            bar.update(90)
        
        if data.empty:
            click.echo("❌ No daily data returned.")
            return
        
        # Export data
        if not output:
            output = f"daily_trends_{'_'.join(keywords[:2])}"
        
        _export_data(ctx, data, output, output_format)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise click.Abort()


@cli.command()
@click.option('--keyword', '-k', multiple=True, required=True, help='Keywords to analyze')
@click.option('--geo', '-g', default='US', help='Geographic region')
@click.option('--since-date', default='2021-01-01', help='Start date (YYYY-MM-DD)')
@click.option('--format', '-f', 'output_format', default='json',
              type=click.Choice(['csv', 'json', 'bigquery']), help='Output format')
@click.option('--output', help='Output filename base')
@click.pass_context
def comprehensive(ctx, keyword, geo, since_date, output_format, output):
    """Get comprehensive analysis with daily, monthly, and related data."""
    try:
        analyzer = TrendsAnalyzer(config=ctx.obj['config'])
        keywords = validate_keywords(list(keyword))
        geo = validate_geo(geo)
        
        click.echo(f"🔬 Comprehensive analysis for: {', '.join(keywords)}")
        
        with click.progressbar(length=100, label='Running comprehensive analysis') as bar:
            bar.update(10)
            results = analyzer.get_comprehensive_analysis(
                keywords=keywords,
                geo=geo,
                since_date=since_date,
                include_related=True
            )
            bar.update(90)
        
        if not results:
            click.echo("❌ No results returned.")
            return
        
        # Export results
        if not output:
            output = f"comprehensive_{'_'.join(keywords[:2])}"
        
        if output_format == 'json':
            exporter = JSONExporter(output_dir=ctx.obj['output_dir'])
            file_path = exporter.export_analysis_results(results, output)
            click.echo(f"✅ Comprehensive analysis exported to: {file_path}")
        else:
            # Export each dataset separately for CSV/BigQuery
            for analysis_type, data in results.items():
                if isinstance(data, pd.DataFrame) and not data.empty:
                    filename = f"{output}_{analysis_type}"
                    _export_data(ctx, data, filename, output_format)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise click.Abort()


@cli.command()
@click.argument('keywords_file', type=click.File('r'))
@click.option('--geo', '-g', default='US', help='Geographic region')
@click.option('--timeframe', '-t', default='today 3-m', help='Time frame for analysis')
@click.option('--batch-size', default=5, help='Batch size (max 5)')
@click.option('--format', '-f', 'output_format', default='csv',
              type=click.Choice(['csv', 'json']), help='Output format')
@click.option('--output-dir', help='Output directory for batch results')
@click.pass_context
def batch(ctx, keywords_file, geo, timeframe, batch_size, output_format, output_dir):
    """Analyze multiple keywords from a file in batches."""
    try:
        # Read keywords from file
        keywords = [line.strip() for line in keywords_file if line.strip()]
        if not keywords:
            click.echo("❌ No keywords found in file.")
            return
        
        analyzer = TrendsAnalyzer(config=ctx.obj['config'])
        geo = validate_geo(geo)
        timeframe = validate_timeframe(timeframe)
        
        output_directory = output_dir or ctx.obj['output_dir']
        batch_dir = Path(output_directory) / 'batch_results'
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        click.echo(f"🔄 Processing {len(keywords)} keywords in batches of {batch_size}")
        
        with click.progressbar(keywords, label='Processing keywords') as bar:
            results = analyzer.analyze_batch(
                keyword_list=keywords,
                geo=geo,
                timeframe=timeframe,
                batch_size=batch_size
            )
            
            for keyword in bar:
                pass  # Progress is handled by the analyzer
        
        # Export results
        click.echo(f"💾 Exporting {len(results)} keyword results...")
        
        for keyword, data in results.items():
            if not data.empty:
                safe_filename = keyword.replace(' ', '_').replace('/', '_')
                
                if output_format == 'csv':
                    exporter = CSVExporter(output_dir=str(batch_dir))
                    exporter.export(data, safe_filename)
                else:
                    exporter = JSONExporter(output_dir=str(batch_dir))
                    exporter.export(data, safe_filename)
        
        click.echo(f"✅ Batch processing complete. Results saved to: {batch_dir}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise click.Abort()


@cli.command()
@click.option('--keyword', '-k', multiple=True, required=True, help='Keywords to compare')
@click.option('--geo', '-g', default='US', help='Geographic region')
@click.option('--timeframe', '-t', default='today 12-m', help='Time frame for comparison')
@click.option('--normalize', is_flag=True, help='Normalize data for better comparison')
@click.option('--format', '-f', 'output_format', default='csv',
              type=click.Choice(['csv', 'json']), help='Output format')
@click.option('--output', help='Output filename')
@click.pass_context
def compare(ctx, keyword, geo, timeframe, normalize, output_format, output):
    """Compare multiple keywords side by side."""
    try:
        analyzer = TrendsAnalyzer(config=ctx.obj['config'])
        keywords = validate_keywords(list(keyword))
        geo = validate_geo(geo)
        timeframe = validate_timeframe(timeframe)
        
        click.echo(f"⚖️  Comparing keywords: {', '.join(keywords)}")
        
        with click.progressbar(length=100, label='Comparing keywords') as bar:
            bar.update(20)
            data = analyzer.compare_keywords(
                keywords=keywords,
                geo=geo,
                timeframe=timeframe,
                normalize=normalize
            )
            bar.update(80)
        
        if data.empty:
            click.echo("❌ No comparison data returned.")
            return
        
        # Show correlation matrix if available
        if hasattr(data, 'attrs') and 'correlation_matrix' in data.attrs:
            click.echo("\n📊 Keyword Correlation Matrix:")
            click.echo(data.attrs['correlation_matrix'].to_string())
        
        # Export data
        if not output:
            output = f"comparison_{'_'.join(keywords[:3])}"
        
        _export_data(ctx, data, output, output_format)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise click.Abort()


@cli.command()
@click.option('--template', type=click.Choice(['basic', 'advanced']), default='basic',
              help='Configuration template to generate')
@click.option('--output', '-o', default='config.yaml', help='Output configuration file')
def init_config(template, output):
    """Generate a configuration file template."""
    config = Config()
    
    if template == 'advanced':
        # Set some advanced defaults
        config.analyzer.cache_enabled = True
        config.analyzer.retry_attempts = 10
        config.export.include_metadata = True
        config.bigquery.write_disposition = 'WRITE_APPEND'
    
    config.save_to_file(output)
    click.echo(f"✅ Configuration template saved to: {output}")
    click.echo("📝 Edit the file to customize your settings.")


def _export_data(ctx, data: pd.DataFrame, filename: str, output_format: str):
    """Helper function to export data in specified format."""
    if output_format == 'csv':
        exporter = CSVExporter(output_dir=ctx.obj['output_dir'])
        file_path = exporter.export(data, filename)
    elif output_format == 'json':
        exporter = JSONExporter(output_dir=ctx.obj['output_dir'])
        file_path = exporter.export_structured(data, filename)
    elif output_format == 'bigquery':
        if not ctx.obj['config'].bigquery.project_id:
            click.echo("❌ BigQuery project_id not configured.")
            return
        
        exporter = BigQueryExporter(
            project_id=ctx.obj['config'].bigquery.project_id,
            dataset_id=ctx.obj['config'].bigquery.dataset_id,
            credentials_path=ctx.obj['config'].bigquery.credentials_path,
            credentials_json=ctx.obj['config'].bigquery.credentials_json
        )
        file_path = exporter.export(data, table_name=filename.replace('-', '_'))
    
    click.echo(f"✅ Exported to: {file_path}")
    click.echo(f"📊 Records: {len(data)}")


if __name__ == '__main__':
    cli()