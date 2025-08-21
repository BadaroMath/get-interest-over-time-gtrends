"""BigQuery exporter for Google Trends data."""

import pandas as pd
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path

from .base_exporter import BaseExporter

# Import BigQuery components with fallback
try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    bigquery = None
    service_account = None


class BigQueryExporter(BaseExporter):
    """Export trends data to Google BigQuery."""
    
    def __init__(
        self,
        project_id: str,
        dataset_id: str = 'trends_data',
        table_name: str = 'trends',
        location: str = 'US',
        credentials_path: Optional[str] = None,
        credentials_json: Optional[str] = None,
        write_disposition: str = 'WRITE_TRUNCATE'
    ):
        """
        Initialize BigQuery exporter.
        
        Args:
            project_id: Google Cloud project ID
            dataset_id: BigQuery dataset ID
            table_name: BigQuery table name
            location: BigQuery location
            credentials_path: Path to service account JSON file
            credentials_json: Service account JSON as string
            write_disposition: How to handle existing data
        """
        super().__init__()
        
        if not BIGQUERY_AVAILABLE:
            raise ImportError(
                "Google Cloud BigQuery is not installed. "
                "Install with: pip install google-cloud-bigquery"
            )
        
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_name = table_name
        self.location = location
        self.write_disposition = write_disposition
        
        # Initialize BigQuery client
        self.client = self._initialize_client(credentials_path, credentials_json)
        
        # Create dataset if it doesn't exist
        self._create_dataset_if_not_exists()
    
    def _initialize_client(
        self,
        credentials_path: Optional[str],
        credentials_json: Optional[str]
    ) -> bigquery.Client:
        """Initialize BigQuery client with credentials."""
        try:
            if credentials_path and Path(credentials_path).exists():
                # Use service account file
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                client = bigquery.Client(
                    credentials=credentials,
                    project=self.project_id
                )
            elif credentials_json:
                # Use service account JSON string
                credentials_dict = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_dict
                )
                client = bigquery.Client(
                    credentials=credentials,
                    project=self.project_id
                )
            else:
                # Use default credentials (environment variable or gcloud)
                client = bigquery.Client(project=self.project_id)
            
            self.logger.info(f"Initialized BigQuery client for project: {self.project_id}")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to initialize BigQuery client: {e}")
            raise
    
    def _create_dataset_if_not_exists(self) -> None:
        """Create BigQuery dataset if it doesn't exist."""
        try:
            dataset_ref = self.client.dataset(self.dataset_id)
            
            try:
                # Try to get the dataset
                self.client.get_dataset(dataset_ref)
                self.logger.info(f"Dataset {self.dataset_id} already exists")
            except Exception:
                # Dataset doesn't exist, create it
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = self.location
                dataset.description = "Google Trends analysis data"
                
                self.client.create_dataset(dataset)
                self.logger.info(f"Created dataset: {self.dataset_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to create dataset: {e}")
            raise
    
    def export(
        self,
        data: pd.DataFrame,
        filename: str = None,  # Not used for BigQuery, kept for interface compatibility
        table_name: Optional[str] = None,
        write_disposition: Optional[str] = None,
        create_disposition: str = 'CREATE_IF_NEEDED',
        **kwargs
    ) -> str:
        """
        Export DataFrame to BigQuery.
        
        Args:
            data: DataFrame to export
            filename: Not used (kept for interface compatibility)
            table_name: Override default table name
            write_disposition: How to handle existing data
            create_disposition: Whether to create table if not exists
            **kwargs: Additional BigQuery job configuration parameters
            
        Returns:
            Table reference string
        """
        self._validate_data(data)
        
        # Use provided table name or default
        target_table = table_name or self.table_name
        target_write_disposition = write_disposition or self.write_disposition
        
        # Prepare data
        export_data = self._add_export_metadata(data)
        
        # Clean data for BigQuery
        export_data = self._prepare_data_for_bigquery(export_data)
        
        try:
            # Configure job
            job_config = bigquery.LoadJobConfig(
                create_disposition=create_disposition,
                write_disposition=target_write_disposition,
                autodetect=True,
                **kwargs
            )
            
            # Get table reference
            table_ref = self.client.dataset(self.dataset_id).table(target_table)
            
            # Load data
            job = self.client.load_table_from_dataframe(
                export_data,
                table_ref,
                job_config=job_config
            )
            
            # Wait for job to complete
            job.result()
            
            table_full_name = f"{self.project_id}.{self.dataset_id}.{target_table}"
            
            self.logger.info(
                f"Successfully exported to BigQuery",
                table=table_full_name,
                records=len(export_data),
                write_disposition=target_write_disposition
            )
            
            return table_full_name
            
        except Exception as e:
            self.logger.error(f"Failed to export to BigQuery: {e}")
            if hasattr(e, 'errors'):
                for error in e.errors:
                    self.logger.error(f"BigQuery error: {error}")
            raise
    
    def _prepare_data_for_bigquery(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare DataFrame for BigQuery upload."""
        data_copy = data.copy()
        
        # Handle datetime columns
        for col in data_copy.columns:
            if data_copy[col].dtype == 'object':
                # Try to convert string dates to datetime
                try:
                    data_copy[col] = pd.to_datetime(data_copy[col], errors='ignore')
                except:
                    pass
        
        # Replace NaN values with None for proper BigQuery handling
        data_copy = data_copy.where(pd.notnull(data_copy), None)
        
        # Ensure column names are BigQuery compatible
        data_copy.columns = [self._clean_column_name(col) for col in data_copy.columns]
        
        return data_copy
    
    def _clean_column_name(self, column_name: str) -> str:
        """Clean column name for BigQuery compatibility."""
        # Replace invalid characters with underscores
        import re
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', str(column_name))
        
        # Ensure it starts with a letter or underscore
        if not cleaned[0].isalpha() and cleaned[0] != '_':
            cleaned = f"col_{cleaned}"
        
        return cleaned
    
    def export_with_schema(
        self,
        data: pd.DataFrame,
        schema: list,
        table_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Export data with explicit schema definition.
        
        Args:
            data: DataFrame to export
            schema: BigQuery schema definition
            table_name: Target table name
            **kwargs: Additional parameters
            
        Returns:
            Table reference string
        """
        # Configure job with explicit schema
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition=self.write_disposition,
            create_disposition='CREATE_IF_NEEDED'
        )
        
        return self.export(
            data,
            table_name=table_name,
            **job_config.to_api_repr(),
            **kwargs
        )
    
    def query_table(
        self,
        query: str,
        to_dataframe: bool = True
    ) -> pd.DataFrame:
        """
        Query BigQuery table and return results.
        
        Args:
            query: SQL query string
            to_dataframe: Whether to return as DataFrame
            
        Returns:
            Query results as DataFrame or BigQuery result set
        """
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            if to_dataframe:
                return results.to_dataframe()
            else:
                return results
                
        except Exception as e:
            self.logger.error(f"Failed to query BigQuery: {e}")
            raise
    
    def delete_table(self, table_name: Optional[str] = None) -> bool:
        """
        Delete BigQuery table.
        
        Args:
            table_name: Table to delete (uses default if None)
            
        Returns:
            True if successful
        """
        target_table = table_name or self.table_name
        
        try:
            table_ref = self.client.dataset(self.dataset_id).table(target_table)
            self.client.delete_table(table_ref)
            
            self.logger.info(f"Deleted table: {self.project_id}.{self.dataset_id}.{target_table}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete table: {e}")
            return False
    
    def get_table_info(self, table_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about BigQuery table.
        
        Args:
            table_name: Table to inspect
            
        Returns:
            Dictionary with table information
        """
        target_table = table_name or self.table_name
        
        try:
            table_ref = self.client.dataset(self.dataset_id).table(target_table)
            table = self.client.get_table(table_ref)
            
            return {
                'table_id': table.table_id,
                'project': table.project,
                'dataset_id': table.dataset_id,
                'created': table.created,
                'modified': table.modified,
                'num_rows': table.num_rows,
                'num_bytes': table.num_bytes,
                'schema': [{'name': field.name, 'type': field.field_type} for field in table.schema]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get table info: {e}")
            return {}