"""
Getting interest over time daily from google trends.

author: BadaroMath
"""
import pandas as pd
from datetime import date, datetime
from pytrends.request import TrendReq
import logging
import csv
from dateutil.relativedelta import relativedelta

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
    
    PERIODOS = pd.date_range(
        '2020-01-01',
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
        
    daily = get_hits(PERIODOS)
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
   
