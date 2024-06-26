# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 14:53:53 2024

@author: chodo
"""

from sec_api import QueryApi# limited number of requests - unsustainable :(
from sec_api import XbrlApi

import const

# import xmltodict
from sec_edgar_api import EdgarClient

import screener_information_picker as picky

import pickle

import yfinance as yf

def __experimenting():
    queryApi = QueryApi(api_key=const.EDGAR_API_KEY)
    xbrlApi = XbrlApi(api_key=const.EDGAR_API_KEY)
    query = {
      "query": "ticker:MSFT AND filedAt:[2020-01-01 TO 2024-12-31] AND formType:\"10-Q\"",
      "from": "0",
      "size": "10",
      "sort": [{ "filedAt": { "order": "desc" } }]
    }
    filings = queryApi.get_filings(query)
    
    results = picky.find_info_in_doc(document=filings, find=["revenue", "gross", "margin", "financial", "msft-20240331", "17,080", "778", "cik", "htm"])
    # cik = int(results["cik"][0])
    
    
    
    fil_url = results["msft-20240331"][-1]
    
    fil_url = 'https://www.sec.gov/Archives/edgar/data/789019/000095017024048288/msft-20240331.htm'
    xbrl_json = xbrlApi.xbrl_to_json(htm_url = fil_url)
    company_ticker = "MSFT"
    #with open(company_ticker+".json", 'wb') as f:
    #    pickle.dump(xbrl_json, f)
    
    #income_statement    = xbrl_json["StatementsOfIncome"]"BalanceSheets","StatementsOfCashFlows"
    


def calculate_PE(company_ticker):
    with open(company_ticker+".json", 'rb') as f:
        xbrl_json = pickle.load(f)
    earning_per_share = xbrl_json["StatementsOfIncome"]["EarningsPerShareDiluted"]
    earnings_data = {"date":[],
                     "value":[]}
    
    earnings_data_separated = {}
    for earning in earning_per_share:
        period_start = earning["period"]["startDate"]
        period_end = earning["period"]["endDate"]
        earning_per_period = float(earning["value"])
        earnings_data_separated[earning["value"]] = {"date":[], "value":[]}
        
        data_period = yf.download(company_ticker, start=period_start, end=period_end)
        for date in data_period.index:
            close_price = data_period["Close"][date]
            pe = price_earning_ratio(share_price=close_price, earnings_per_share=earning_per_period)
            earnings_data["date"].append(date)
            earnings_data["value"].append(pe)
            
            earnings_data_separated[earning["value"]]["date"].append(date)
            earnings_data_separated[earning["value"]]["value"].append(pe)
    with open(company_ticker+"_PE"+".json", 'wb') as f:
        pickle.dump(earnings_data, f)
    with open(company_ticker+"D_PE"+".json", 'wb') as f:
        pickle.dump(earnings_data_separated, f)
    

def wrapper_sec_edgar_api_experiment():
    edgar = EdgarClient(user_agent="<Sample Company Name> <Admin Contact>@<Sample Company Domain>")
    
    cik = str(789019)#MSFT
    submission = edgar.get_submissions(cik=cik)
    edgar.get_frames(taxonomy="us-gaap", tag="AccountsPayableCurrent", unit="USD", year="2019", quarter=1)
    
    # https://data.sec.gov/submissions/CIK##########.json# Central Index Key 
    
    # time to crawl the shit out of it
    #fil_url = 'https://www.sec.gov/Archives/edgar/data/789019/000095017024048288/msft-20240331.htm'
    
    import requests
    cik = str(789019)
    cik_10digs = ((10-len(cik))*"0")+cik
    submissions_history_url = "https://data.sec.gov/submissions/CIK"+cik_10digs+".json"
    companyconcept_url  = "https://data.sec.gov/api/xbrl/companyconcept/CIK"+cik_10digs+"/us-gaap/AccountsPayableCurrent.json"
    companyfacts_url    = "https://data.sec.gov/api/xbrl/companyfacts/CIK"+cik_10digs+".json"
    
    Year = 2019
    Quartal = 1
    CY = "msft-20230331"
    frames_url          = "https://data.sec.gov/api/xbrl/frames/us-gaap/AccountsPayableCurrent/USD/CY"+CY+".json"
    frames_url_2        = "https://data.sec.gov/api/xbrl/frames/us-gaap/AccountsPayableCurrent/USD/CY2019Q1I.json"
    
    
    accession_number = "0001193125-24-118081"
    
    response = requests.get(submissions_history_url, headers={"User-Agent": "Mozilla/5.0"})
    
    json_response = response.json()# here I get the 10-Q
    
    results = picky.find_info_in_doc(json_response, find=["CY"])


def price_earning_ratio(share_price, earnings_per_share):
    return share_price / earnings_per_share





