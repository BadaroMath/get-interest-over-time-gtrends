"""
Google Trends Analyzer - A comprehensive toolkit for Google Trends data analysis
"""

from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

# Version
VERSION = "1.0.0"

setup(
    name="google-trends-analyzer",
    version=VERSION,
    description="A powerful, enterprise-grade Python toolkit for collecting, analyzing, and visualizing Google Trends data",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/google-trends-analyzer",
    author="Your Name",
    author_email="your.email@example.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="google trends, market research, seo, data analysis, search trends",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "pytrends>=4.9.0",
        "python-dateutil>=2.8.0",
        "numpy>=1.21.0",
        "PyYAML>=6.0",
        "pydantic>=1.10.0",
        "click>=8.0.0",
        "rich>=12.0.0",
        "structlog>=22.0.0",
    ],
    extras_require={
        "bigquery": ["google-cloud-bigquery>=3.0.0", "google-auth>=2.0.0"],
        "excel": ["openpyxl>=3.0.9"],
        "parquet": ["pyarrow>=10.0.0"],
        "database": ["sqlalchemy>=1.4.0", "psycopg2-binary>=2.9.0"],
        "mongodb": ["pymongo>=4.0.0"],
        "api": ["fastapi>=0.85.0", "uvicorn>=0.18.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "pre-commit>=2.20.0",
        ],
        "all": [
            "google-cloud-bigquery>=3.0.0",
            "google-auth>=2.0.0",
            "openpyxl>=3.0.9",
            "pyarrow>=10.0.0", 
            "sqlalchemy>=1.4.0",
            "psycopg2-binary>=2.9.0",
            "pymongo>=4.0.0",
            "fastapi>=0.85.0",
            "uvicorn>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "trends-analyzer=trends_analyzer.cli.main:cli",
        ],
    },
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/yourusername/google-trends-analyzer/issues",
        "Source": "https://github.com/yourusername/google-trends-analyzer",
        "Documentation": "https://trends-analyzer.readthedocs.io/",
    },
)