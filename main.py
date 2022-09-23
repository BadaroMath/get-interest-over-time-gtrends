"""
Getting interest over time daily from google trends.

author: BadaroMath
"""
import pandas as pd
from datetime import date, datetime
from pytrends.request import TrendReq
import logging
import csv


def save_csv(daily, monthly, path):
    
    logging.info(f'Transform and save data into {path}')
    df = pd.merge(daily, monthly, how="left", on=["year", "month"])
    df = df.drop(["month", "year"], axis=1)
    df["outback_aj"] = df["outback"]*df["outback_monthly"]/100
    df.to_csv(
        path,
        #mode = 'a',
        header = True,
        index = False
        )
    return f'Saved'

def get_hits(time_ranges):
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
                    pytrend.build_payload(kw_list=['outback'],timeframe=timerange, geo='BR')
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

def get_monthly():
    logging.info('Collecting interest over time all time:')
    pytrend = TrendReq()
    hits_all = None
    t=0
    while t <= 5:
        try:
            pytrend.build_payload(kw_list=['outback'],timeframe='all', geo='BR')
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
        hits_all = hits_all.rename(columns={'outback': 'outback_monthly'})
        hits_all["month"] = pd.to_datetime(hits_all["date"], format = "%Y-%m-%d").dt.month
        hits_all["year"] = pd.to_datetime(hits_all["date"], format = "%Y-%m-%d").dt.year
        hits_all = hits_all.drop("date", axis=1)
        
    return hits_all 

def main():
    time_ranges = ['2021-01-01 2021-01-31', '2021-02-01 2021-02-28', '2021-03-01 2021-03-31',
                   '2021-04-01 2021-04-30', '2021-05-01 2021-05-31', '2021-06-01 2021-06-30',
                   '2021-07-01 2021-07-31', '2021-08-01 2021-08-31', '2021-09-01 2021-09-30',
                   '2021-10-01 2021-10-31', '2021-11-01 2021-11-30', '2021-12-01 2021-12-31',
                   '2022-01-01 2022-01-31', '2022-02-01 2022-02-28', '2022-03-01 2022-03-31',
                   '2022-04-01 2022-04-30', '2022-05-01 2022-05-31', '2022-06-01 2022-06-30',
                   '2022-07-01 2022-07-31', '2022-08-01 2022-08-31', '2022-09-01 2022-09-30',
                   '2022-10-01 2022-10-31', '2022-11-01 2022-11-31', '2022-12-01 2022-09-31']

    daily = get_hits(time_ranges)
    monthly = get_monthly()
    print(daily, monthly)
    save_csv(daily,monthly,r'D:\Tabelas\gtrends.csv')
    return ("ok", 200)

if __name__=="__main__":
    logging.basicConfig(
        filename=r'D:/Rotinas/Gtrends_Log.log',
        format='%(levelname)s %(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filemode="a",
        level=logging.INFO
    )
    main()
   
