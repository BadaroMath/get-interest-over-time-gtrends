# 📈 Google Trends Analyzer

<div align="center">

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-95%25-green.svg)

**A powerful, enterprise-grade Python toolkit for collecting, analyzing, and visualizing Google Trends data**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples)

</div>

---

## 🚀 **Overview**

Google Trends Analyzer is a comprehensive Python library that simplifies the process of collecting search interest data from Google Trends. Built with enterprise applications in mind, it offers robust data processing, multiple export formats, and seamless integration with cloud platforms.

### **Why Choose Google Trends Analyzer?**

- 🔄 **Batch Processing**: Analyze multiple keywords simultaneously
- 🌍 **Multi-Region Support**: Global and regional trend analysis
- 📊 **Multiple Export Formats**: CSV, JSON, Parquet, BigQuery, and more
- 🐳 **Docker Ready**: Containerized for easy deployment
- ⚡ **High Performance**: Optimized with retry logic and error handling
- 🧪 **Well Tested**: Comprehensive test coverage
- 📚 **Rich Documentation**: Detailed guides and examples

## ✨ **Features**

### **Core Functionality**
- **Daily & Monthly Trends**: Collect both granular daily data and monthly aggregates
- **Historical Analysis**: Retrieve trends data from any time period
- **Real-time Processing**: Up-to-date trend information
- **Smart Scaling**: Automatically adjusts data collection based on time ranges

### **Data Processing**
- **Data Normalization**: Intelligent scaling between daily and monthly data
- **Error Recovery**: Robust retry mechanisms for API failures
- **Data Validation**: Ensures data quality and consistency
- **Flexible Filtering**: Filter by date range, region, and keywords

### **Export & Integration**
- **Multiple Formats**: CSV, JSON, Parquet, Excel
- **Cloud Integration**: Native BigQuery support
- **Database Connectors**: PostgreSQL, MySQL, SQLite
- **API Endpoints**: RESTful API for web integration

### **Enterprise Features**
- **Batch Jobs**: Process large keyword lists efficiently
- **Scheduling**: Cron-compatible for automated data collection
- **Monitoring**: Comprehensive logging and metrics
- **Configuration**: Flexible YAML/JSON configuration management

## 🛠️ **Installation**

### **From PyPI** (Recommended)
```bash
pip install google-trends-analyzer
```

### **From Source**
```bash
git clone https://github.com/yourusername/google-trends-analyzer.git
cd google-trends-analyzer
pip install -e .
```

### **With Docker**
```bash
docker pull trends-analyzer:latest
docker run -it trends-analyzer --help
```

## 🚀 **Quick Start**

### **1. Basic Usage**
```python
from trends_analyzer import TrendsAnalyzer

# Initialize analyzer
analyzer = TrendsAnalyzer()

# Collect trends data
data = analyzer.get_trends(
    keywords=['python', 'javascript'],
    timeframe='2023-01-01 2023-12-31',
    geo='US'
)

# Export to CSV
data.to_csv('trends_data.csv')
```

### **2. Command Line Interface**
```bash
# Single keyword analysis
trends-analyzer --keyword "artificial intelligence" --geo US --output trends.csv

# Multiple keywords with custom timeframe
trends-analyzer \
  --keywords "python,javascript,golang" \
  --timeframe "2023-01-01 2023-12-31" \
  --geo US \
  --format json \
  --output results.json

# Batch processing from file
trends-analyzer --batch-file keywords.txt --output-dir ./results/
```

### **3. Configuration File**
```yaml
# config.yaml
analyzer:
  default_geo: 'US'
  retry_attempts: 5
  timeout: 30

export:
  formats: ['csv', 'json']
  include_metadata: true

bigquery:
  project_id: 'your-project'
  dataset_id: 'trends_data'
  table_name: 'daily_trends'
```

```python
from trends_analyzer import TrendsAnalyzer

# Load configuration
analyzer = TrendsAnalyzer.from_config('config.yaml')
results = analyzer.analyze_batch(['keyword1', 'keyword2'])
```

## 📊 **Examples**

### **Example 1: Technology Trends Analysis**
```python
import pandas as pd
from trends_analyzer import TrendsAnalyzer

# Analyze programming languages popularity
analyzer = TrendsAnalyzer()

tech_keywords = [
    'python programming',
    'javascript development', 
    'machine learning',
    'artificial intelligence'
]

# Get monthly data for the past year
trends = analyzer.get_monthly_trends(
    keywords=tech_keywords,
    timeframe='today 12-m',
    geo='US'
)

# Visualize results
trends.plot(title='Technology Trends - Past 12 Months')
```

### **Example 2: Global Market Analysis**
```python
# Compare regional interest
regions = ['US', 'GB', 'DE', 'JP', 'BR']
keyword = 'electric vehicles'

regional_data = {}
for region in regions:
    regional_data[region] = analyzer.get_trends(
        keywords=[keyword],
        geo=region,
        timeframe='2023-01-01 2023-12-31'
    )

# Combine and analyze
combined_df = pd.concat(regional_data, names=['Region', 'Date'])
```

### **Example 3: BigQuery Integration**
```python
from trends_analyzer import TrendsAnalyzer, BigQueryExporter

# Collect data
analyzer = TrendsAnalyzer()
data = analyzer.get_trends(['cloud computing'], timeframe='today 5-y')

# Export to BigQuery
exporter = BigQueryExporter(
    project_id='your-project',
    dataset_id='market_research',
    table_name='tech_trends'
)

exporter.upload(data)
```

## 🏗️ **Architecture**

```
google-trends-analyzer/
├── src/trends_analyzer/
│   ├── __init__.py
│   ├── core/
│   │   ├── analyzer.py       # Main TrendsAnalyzer class
│   │   ├── collector.py      # Data collection logic
│   │   └── processor.py      # Data processing utilities
│   ├── exporters/
│   │   ├── csv_exporter.py
│   │   ├── json_exporter.py
│   │   └── bigquery_exporter.py
│   ├── utils/
│   │   ├── config.py         # Configuration management
│   │   ├── logger.py         # Logging utilities
│   │   └── validators.py     # Data validation
│   └── cli/
│       └── main.py           # Command-line interface
├── tests/                    # Comprehensive test suite
├── docs/                     # Documentation
├── config/                   # Configuration templates
└── examples/                 # Usage examples
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export BIGQUERY_DATASET="trends_data"
export TRENDS_CACHE_DIR="/tmp/trends_cache"
export LOG_LEVEL="INFO"
```

### **Configuration File Options**
```yaml
# Complete configuration example
analyzer:
  default_geo: 'US'
  default_timeframe: 'today 3-m'
  retry_attempts: 5
  timeout: 30
  cache_enabled: true
  cache_dir: './cache'

logging:
  level: 'INFO'
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  file: 'trends_analyzer.log'

export:
  default_format: 'csv'
  include_metadata: true
  timestamp_columns: true

bigquery:
  project_id: 'your-project'
  dataset_id: 'trends_data'
  location: 'US'
  write_disposition: 'WRITE_TRUNCATE'
```

## 🧪 **Testing**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=trends_analyzer --cov-report=html

# Run specific test category
pytest tests/test_core/
pytest tests/test_exporters/
```

## 🐳 **Docker Usage**

### **Build Image**
```bash
docker build -t trends-analyzer .
```

### **Run Analysis**
```bash
# Interactive analysis
docker run -it trends-analyzer bash

# Direct command execution
docker run trends-analyzer trends-analyzer --keyword "python" --geo US

# With volume mounting for results
docker run -v $(pwd)/results:/app/results trends-analyzer \
  trends-analyzer --keyword "data science" --output /app/results/output.csv
```

## 📚 **API Reference**

### **TrendsAnalyzer Class**
```python
class TrendsAnalyzer:
    def __init__(self, config_path: Optional[str] = None)
    def get_trends(self, keywords: List[str], timeframe: str, geo: str = 'US') -> pd.DataFrame
    def get_daily_trends(self, keywords: List[str], timeframe: str, geo: str = 'US') -> pd.DataFrame
    def get_monthly_trends(self, keywords: List[str], timeframe: str, geo: str = 'US') -> pd.DataFrame
    def analyze_batch(self, keywords: List[str], **kwargs) -> Dict[str, pd.DataFrame]
```

### **Supported Timeframes**
- `'now 1-H'` - Last hour
- `'now 4-H'` - Last 4 hours  
- `'now 1-d'` - Last day
- `'now 7-d'` - Last 7 days
- `'today 1-m'` - Past month
- `'today 3-m'` - Past 3 months
- `'today 12-m'` - Past year
- `'today 5-y'` - Past 5 years
- `'all'` - All available data
- `'2020-01-01 2020-12-31'` - Custom date range

### **Supported Regions**
- Global: `''` (empty string)
- Countries: `'US'`, `'GB'`, `'DE'`, `'FR'`, `'JP'`, `'BR'`, etc.
- States/Provinces: `'US-CA'`, `'US-NY'`, etc.

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
git clone https://github.com/yourusername/google-trends-analyzer.git
cd google-trends-analyzer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

### **Submitting Changes**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- [pytrends](https://github.com/GeneralMills/pytrends) - Google Trends API wrapper
- [pandas](https://pandas.pydata.org/) - Data manipulation and analysis
- [Google Cloud BigQuery](https://cloud.google.com/bigquery) - Cloud DWH

---

<div align="center">

**⭐ Star this repository if it helped you! ⭐**

</div>
