import requests
import os
from datetime import datetime
from twilio.rest import Client
from newsapi import NewsApiClient

STOCK = "AAPL"
COMPANY_NAME = "Apple Inc"

# ---------------------------- FUNCTIONS ------------------------------- #


def get_stock_price(my_response):
    jdata = my_response.json()
    print(jdata)
    now = datetime.now()
    prior_day = now.day - 1
    day_before = now.day - 2
    yesterday = datetime(year=now.year, month=now.month, day=prior_day).strftime("%Y-%m-%d")
    yesterday = f"{yesterday} 19:00:00"

    day_before_y = datetime(year=now.year, month=now.month, day=day_before).strftime("%Y-%m-%d")
    day_before_y = f"{day_before_y} 19:00:00"

    series_index = "Time Series (60min)"
    close = "4. close"
    closing_price = jdata[series_index][yesterday][close]
    prior_closing_price = jdata[series_index][day_before_y][close]
    difference = float(closing_price) - float(prior_closing_price)
    percentage = round((difference / float(prior_closing_price) * 100))
    return percentage


def format_change_headline(percentage):
    stock_headline = ""
    if percentage < 0:
        stock_headline = f"{STOCK}: 🔻{percentage}%"
    elif percentage > 0:
        stock_headline = f"{STOCK}: 🔺{percentage}%"
    elif percentage == 0:
        stock_headline = f"{STOCK}: -"
    return stock_headline


def format_news(headlines):
    stories = {}
    for i in range(0, 9):
        if i > 0:
            publisher = headlines['articles'][i]['source']['name']
            if len(stories) < 3:
                if publisher != 'YouTube' and publisher != "Tom's Guide":
                    headline = headlines['articles'][i]['title']
                    stories[headline] = headlines['articles'][i]['content']
        else:
            return stories
    return stories


def format_message():
    my_msg = f"{stock_heading}\n"
    for entry in headline_dict:
        my_msg += f"Headline: {entry}\nBrief: {headline_dict[entry]}\n\n"
    return my_msg

# ---------------------------- MAIN OPERATIONS ------------------------------- #


phone_num = os.environ.get("SOME_NUM")
twi_sid = os.environ.get("TWILIO_SID")
t_auth_token = os.environ.get("TWI_AUTH_TOKEN")

av_parameters = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": STOCK,
    "interval": "60min",
    "outputsize": 30,
    "apikey": os.environ.get("AV_API_KEY")
}

av_response = requests.get("https://www.alphavantage.co/query", params=av_parameters, timeout=60)
av_response.raise_for_status()
change = get_stock_price(av_response)

stock_heading = format_change_headline(change)

newsapi = NewsApiClient(api_key=os.environ.get("NEWSAPI_KEY"))
today = str(datetime.now()).split()[0]
start_day = datetime.now().day - 10
start_range = \
    f"{datetime.now().year}-{datetime.now().month}-{start_day}".split()[0]

top_headlines = (
    newsapi.get_top_headlines(
        q='apple', category='technology', language='en'))

headline_dict = format_news(top_headlines)
full_msg = format_message()

client = Client(twi_sid, t_auth_token)
message = client.messages.create(
    body=full_msg, from_=os.environ.get("SOME_NUM"),
    to='+16362845670')

