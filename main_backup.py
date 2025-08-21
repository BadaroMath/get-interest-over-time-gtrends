"""
Getting interest over time daily from google trends.
author: jose.badaro@raccoon.ag

Script that collects and transforms data from Google Trends and saves it to BigQuery tables. 
It includes functions for configuring the logging settings, getting the payload from a 
cloud scheduler, collecting daily and monthly data from Google Trends using the pytrends 
package, and saving the data to BigQuery using the google-cloud-bigquery package.

Payload example:

{
    "message": {
        "config": {
        "project_id": "<project_id>",
        "dataset_id": "<dataset_id>",
        "table_name": "<table_name>",
        "keyword": "<keyword>",
        "since": "<since_date>"
        }
    }
}
"""
import pandas as pd
from datetime import date, datetime
from pytrends.request import TrendReq
import logging
from dateutil.relativedelta import relativedelta
import logging as log
from google.cloud import bigquery


def config_log():

    """
    Configure logging level, output format and sends it to a file.
    """

    today = datetime.today().strftime("%Y%m%d")
    logging_level = 20
    # log_filename = f'logs/instagram_organic_{today}.log'
    log.basicConfig(
        # filename=log_filename,
        level=logging_level,
        format=f'[%(asctime)s.%(msecs)03d] %(levelname)s: %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True)
    


def payload(request_json):
    """
    Retrieves the payload from the cloud scheduler and returns the configuration 
    needed for saving the data to BigQuery.

    Arguments:
        request {payload body} -- payload body from cloud scheduler.

    Returns:
        config {dict} -- transformed report result
    """    
    if request_json and 'message' in request_json:
        config = request_json['message']["config"]

        return config
    else:
        return ("Payload error", 400)

def get_hits(time_ranges, config):
    '''
    Collects daily interest over time from Google Trends for a given time range and 
    returns a pandas dataframe with the results. It uses the pytrends package to build 
    a payload with the specified keyword and time range and collects the interest over time data. 
    If there is an error, it retries up to 5 times.
    '''
    logging.info('Collecting interest over time:')
    pytrend = TrendReq()
    trends = pd.DataFrame()     
    for timerange in time_ranges:
        attempts=0
        logging.info(f"Collecting interest over time from timerange {timerange}")
        print(f"Collecting interest over time from timerange {timerange}")
        if datetime.strptime(timerange.split()[0], "%Y-%m-%d") <= datetime.today():    
            while attempts <= 5:
                try:
                    pytrend.build_payload(kw_list=[config["keyword"]],timeframe=timerange, geo='BR')
                    hits = pytrend.interest_over_time()                    
                    trends = pd.concat([trends, hits])
                    break
                except:
                    attempts = attempts + 1
                    print(f"pytrends Error")
                else:
                    attempts = attempts + 1
        else:
            print(f"skip {timerange}")
    if not trends.empty:
        trends.reset_index(inplace = True)
        trends = trends.drop("isPartial", axis=1)
        trends["month"] = pd.to_datetime(trends["date"], format = "%Y-%m-%d").dt.month
        trends["year"] = pd.to_datetime(trends["date"], format = "%Y-%m-%d").dt.year
    return trends

def get_monthly(config):
    '''
    Collects monthly interest over time from Google Trends for all time and returns a 
    pandas dataframe with the results. It uses the pytrends package to build a payload 
    with the specified keyword and collects the interest over time data. If there is an 
    error, it retries up to 5 times.
    '''
    logging.info('Collecting interest over time all time:')
    pytrend = TrendReq()
    hits_all = None
    t=0
    while t <= 5:
        try:
            pytrend.build_payload(kw_list=[config["keyword"]],timeframe='all', geo='BR')
            hits_all = pytrend.interest_over_time()
            break
        except:
            t = t + 1
            print(f"pytrends Error")
        else:
            t = t + 1      
    if hits_all is not None:
        hits_all.reset_index(inplace = True)
        hits_all = hits_all.drop("isPartial", axis=1)
        hits_all = hits_all[(hits_all['date'] >= '2021-01-01')]
        hits_all = hits_all.rename(columns={f'{config["keyword"]}': f'{config["keyword"]}_monthly'})
        hits_all["month"] = pd.to_datetime(hits_all["date"], format = "%Y-%m-%d").dt.month
        hits_all["year"] = pd.to_datetime(hits_all["date"], format = "%Y-%m-%d").dt.year
        hits_all = hits_all.drop("date", axis=1)
        
    return hits_all 


def bigquery_save_data(data, config):
    """
    Function saves the data to a BigQuery table. 
    It uses the google-cloud-bigquery package to load the dataframe 
    to the specified table in BigQuery.

    Arguments:
        config {dict} -- configuration with BigQuery params
        data {df} -- df data to be loaded
    """

    log.info(f"Loading data to {config['table_name']}")

    bigquery_client = bigquery.Client(config["project_id"])
    dataset = bigquery_client.dataset(config["dataset_id"])
    table_ref = dataset.table(config["table_name"])

    job_config = bigquery.LoadJobConfig()
    job_config.create_disposition = "CREATE_IF_NEEDED"
    #job_config.time_partitioning = bigquery.table.TimePartitioning()
    #job_config.schema = schema
    job_config.autodetect = True
    job_config.write_disposition = "WRITE_TRUNCATE"

    job = bigquery_client.load_table_from_dataframe(
        data,
        table_ref,
        job_config=job_config
    )

    try:
        job.result()
    except Exception:
        log.error(job.errors)



def save_data(daily, monthly, config):
    """
    function saves the daily and monthly data to BigQuery tables. 
    It first merges the daily and monthly dataframes and then saves the merged 
    dataframe to a BigQuery table using the bigquery_save_data() function.

    Arguments:
        daily {df} -- daily data from grends
        monthly {df} -- monthly data from gtrends
        config {dict} -- configuration with BigQuery params
    """    
    logging.info(f"Transform and save data into {config['table_name']}")
    kw = config['keyword']
    df = pd.merge(daily, monthly, how="left", on=["year", "month"])
    df = df.drop(["month", "year"], axis=1)
    df[f"{kw}_daily"] = df[kw]*df[f"{kw}_monthly"]/100
    df = df.drop([kw], axis=1)
    print(df)
    bigquery_save_data(df, config)

    return f'Saved'


def etl(config):
    '''
    Performs the Extract, Transform and Load (ETL) process on the data 
    based on the input configuration config.
    
    The function first generates a list of monthly periods from config["since"] 
    until the current month using the pd.date_range() function from the pandas library. 
    It then iterates through this list and transforms each period to a string representing 
    the first and last day of that month.

    Next, the function calls the get_hits() and get_monthly() functions to extract data from 
    an external source and transform it into pandas DataFrames. These DataFrames are then passed
    to the save_data() function to be loaded into a database or file, as specified in the config 
    parameter.
    '''
    PERIODOS = pd.date_range(
        config["since"],
        date.today().strftime(
            "%Y-%m-%d"
        ),
        freq='MS'
    ).strftime(
        "%Y-%m-%d"
    ).tolist()

    for i in range(len(PERIODOS)):
        first_date = PERIODOS[i]
        last_day = (
            datetime.strptime(
                first_date, 
                "%Y-%m-%d"
            ) + relativedelta(months=+1) + relativedelta(days=-1)
            ).strftime(
            "%Y-%m-%d"
        )
        PERIODOS[i] = first_date + " " + last_day
        
    daily = get_hits(PERIODOS, config)
    monthly = get_monthly(config)
    #print(daily.head(3), monthly.head(3))
    save_data(daily, monthly, config)

    return ("ok", 200)


def main(request):
    request_json = request.get_json()
    config = payload(request_json)
    status_code = etl(config)

    if status_code == 500:
        return ("not ok", 500)
    return ("ok", 200)
