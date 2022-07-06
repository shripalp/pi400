#This is a Canadian TSX listed stock advisor. Program ask user for stock symbol or company name.
#Looks upthe stocks currrent data on yahoo finance Canada.
#Prints output with the current price and advice to buy or hold the stock
#creates a JSON file with stock data


import pandas as pd
import re
import requests
import json
from bs4 import BeautifulSoup

def main():

    url = "https://en.wikipedia.org/wiki/S%26P/TSX_Composite_Index"
    #get list of canadian stock tickers and company names
    tsx_list = get_tsx_list(url)


    #accept user input with validation
    while True:
        try:
            stock = input("Enter stock ticker or Company name: ").rstrip().lstrip()
            if re.search(r"^[a-zA-Z]+\.*\s*[a-zA-Z]*\s*[a-zA-Z]*\.*$", stock):
                #validate stock and if valid, return a dict
                ticker_dict = is_valid(stock, tsx_list)
                if len(ticker_dict) == 0:
                    continue
                else:
                    break
        except (IndexError,TypeError) as e:
            pass


    #select the stock now from list presented
    i = 1
    for key, value in ticker_dict.items():
        print(f"{i}. {value} symbol is {key}")
        i = i + 1
    print(" ")
    #if more than one results returned then ask user again
    if len(ticker_dict) > 1:
        while True:
            ticker_symbol = input("Enter stock ticker from list provided: ").rstrip().lstrip().upper()
            if ticker_symbol in ticker_dict:
                company_name = ticker_dict[ticker_symbol]
                break
    else:
        ticker_symbol = [key for key in ticker_dict][0]
        company_name = ticker_dict[ticker_symbol]


    #get stock data from given ticker symbol
    stockdata = (getData(ticker_symbol))

    with open('stockdata.json', 'w') as f:
        json.dump(stockdata, f)


    print("{symbol} : {company} current price is {price}".format(company=company_name, symbol=stockdata['symbol'], price=stockdata['price']))
    print(f"Based on 52-week-range average of {stockdata['average']:.2f}.... my recommendation is a {stockdata['rating']}!!")


#this function takes user input (stock name or ticker) and returns stock ticker if valid
def is_valid(stock, tsx):

#checks for stock ticker including .UN or .A and return dict
    for i in range(len(tsx[0])):
        if str(stock.upper()).split('.')[0] == str(tsx[0][i]).split('.')[0]:
            return {tsx[0][i]:tsx[1][i]}
        else:
            continue
#check full name of stock and return possible values as dict
    stock_list = []
    for s in tsx[1]:
        if re.search(rf"^.*{stock}.*$", s, re.IGNORECASE):
            stock_list.append(s)

    stock_dict = {}
    for s in stock_list:
        for i in range(len(tsx[0])):
            if s == tsx[1][i]:
                stock_dict[tsx[0][i]] = s

    return stock_dict


#this function returns the list of TSX listed companies from wiki table
def get_tsx_list(url):

    try:
        req = requests.get(url)
        req.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise e

    dfs = pd.read_html(req.url)

    try:
        df = dfs[1]
    except ValueError as e:
        raise e

    ticker_list = df['Ticker'].tolist()
    company_list = df['Company'].tolist()

    return ticker_list, company_list
    ...
#outputs a JSON file and return a dict of stock parameters
def getData(stock):
    #make ticker compatible with yahoo finanance cabada
    stock = stock.split('.')
    if len(stock) > 1:
        stock = stock[0] + "-" + stock[1] + ".TO"
    else:
        stock = stock[0] + ".TO"

    url = f"https://ca.finance.yahoo.com/quote/{stock}"

    try:
        #load html page using get method
        page = requests.get(url)
        page.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise e


    #create soup object using html-parser
    soup = BeautifulSoup(page.content, "html.parser")

    try:
        stock_data = {
            "symbol":stock,
            "price":soup.find("div", class_="D(ib) Mend(20px)").find_all("fin-streamer")[0].text,
            "change":soup.find("div", class_="D(ib) Mend(20px)").find_all("fin-streamer")[1].text,
            "percent_change":soup.find("div", class_="D(ib) Mend(20px)").find_all("fin-streamer")[2].text,
            "year_range":soup.find("table", class_="W(100%)").find_all("td")[11].text,

        }
    except (TypeError, AttributeError) as e:
        raise e

    #determine stock rating based on 52 week average
    x = stock_data["year_range"].split("-")
    y = (float(x[0].lstrip()) + float(x[1].rstrip()))/2
    stock_data["average"] = y
    if float(stock_data["price"]) > float(stock_data["average"]):
        stock_data["rating"] = "SELL"
    else:
        stock_data["rating"] = "BUY"


    return stock_data


if __name__ == "__main__":
    main()