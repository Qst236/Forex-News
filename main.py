import os
import re
import json
import pytz
import time
import random
import discord
import requests
from discord import SyncWebhook
from datetime import datetime, timedelta
from scraper import start
from config import WEEK, MONTH

# news = [{'title': 'BusinessNZ Services Index', 'country': 'NZD', 'date': '2024-08-19T05:30:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': '40.2'}, {'title': 'Rightmove HPI m/m', 'country': 'GBP', 'date': '2024-08-19T06:01:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': '-0.4%'}, {'title': 'Core Machinery Orders m/m', 'country': 'JPY', 'date': '2024-08-19T06:50:00+07:00', 'impact': 'Low', 'forecast': '0.9%', 'previous': '-3.2%'}, {'title': 'FOMC Member Waller Speaks', 'country': 'USD', 'date': '2024-08-19T20:15:00+07:00', 'impact': 'Medium', 'forecast': '', 'previous': ''}, {'title': 'CB Leading Index m/m', 'country': 'USD', 'date': '2024-08-19T21:00:00+07:00', 'impact': 'Low', 'forecast': '-0.4%', 'previous': '-0.2%'}, {'title': 'Trade Balance', 'country': 'NZD', 'date': '2024-08-20T05:45:00+07:00', 'impact': 'Low', 'forecast': '331M', 'previous': '699M'}, {'title': '1-y Loan Prime Rate', 'country': 'CNY', 'date': '2024-08-20T08:15:00+07:00', 'impact': 'Medium', 'forecast': '3.35%', 'previous': '3.35%'}, {'title': '5-y Loan Prime Rate', 'country': 'CNY', 'date': '2024-08-20T08:15:00+07:00', 'impact': 'Medium', 'forecast': '3.85%', 'previous': '3.85%'}, {'title': 'Monetary Policy Meeting Minutes', 'country': 'AUD', 'date': '2024-08-20T08:30:00+07:00', 'impact': 'Medium', 'forecast': '', 'previous': ''}, {'title': 'Trade Balance', 'country': 'CHF', 'date': '2024-08-20T13:00:00+07:00', 'impact': 'Low', 'forecast': '5.44B', 'previous': '6.18B'}, {'title': 'German PPI m/m', 'country': 'EUR', 'date': '2024-08-20T13:00:00+07:00', 'impact': 'Low', 'forecast': '0.2%', 'previous': '0.2%'}, {'title': 'Foreign Direct Investment ytd/y', 'country': 'CNY', 'date': '2024-08-20T13:02:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': '-29.1%'}, {'title': 'Current Account', 'country': 'EUR', 'date': '2024-08-20T15:00:00+07:00', 'impact': 'Low', 'forecast': '37.0B', 'previous': '36.7B'}, {'title': 'Final Core CPI y/y', 'country': 'EUR', 'date': '2024-08-20T16:00:00+07:00', 'impact': 'Low', 'forecast': '2.9%', 'previous': '2.9%'}, {'title': 'Final CPI y/y', 'country': 'EUR', 'date': '2024-08-20T16:00:00+07:00', 'impact': 'Low', 'forecast': '2.6%', 'previous': '2.6%'}, {'title': 'SNB Chairman Jordan Speaks', 'country': 'CHF', 'date': '2024-08-20T16:30:00+07:00', 'impact': 'Medium', 'forecast': '', 'previous': ''}, {'title': 'German Buba Monthly Report', 'country': 'EUR', 'date': '2024-08-20T17:03:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': ''}, {'title': 'CPI m/m', 'country': 'CAD', 'date': '2024-08-20T19:30:00+07:00', 'impact': 'High', 'forecast': '0.4%', 'previous': '-0.1%'}, {'title': 'Median CPI y/y', 'country': 'CAD', 'date': '2024-08-20T19:30:00+07:00', 'impact': 'High', 'forecast': '2.5%', 'previous': '2.6%'}, {'title': 'Trimmed CPI y/y', 'country': 'CAD', 'date': '2024-08-20T19:30:00+07:00', 'impact': 'High', 'forecast': '2.8%', 'previous': '2.9%'}, {'title': 'Common CPI y/y', 'country': 'CAD', 'date': '2024-08-20T19:30:00+07:00', 'impact': 'Medium', 'forecast': '2.2%', 'previous': '2.3%'}, {'title': 'Core CPI m/m', 'country': 'CAD', 'date': '2024-08-20T19:30:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': '-0.1%'}, {'title': 'NHPI m/m', 'country': 'CAD', 'date': '2024-08-20T19:30:00+07:00', 'impact': 'Low', 'forecast': '0.0%', 'previous': '-0.2%'}, {'title': 'GDT Price Index', 'country': 'NZD', 'date': '2024-08-20T21:50:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': '0.5%'}, {'title': 'FOMC Member Bostic Speaks', 'country': 'USD', 'date': '2024-08-21T00:35:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': ''}, {'title': 'FOMC Member Barr Speaks', 'country': 'USD', 'date': '2024-08-21T01:45:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': ''}, {'title': 'Trade Balance', 'country': 'JPY', 'date': '2024-08-21T06:50:00+07:00', 'impact': 'Low', 'forecast': '-0.73T', 'previous': '-0.82T'}, {'title': 'MI Leading Index m/m', 'country': 'AUD', 'date': '2024-08-21T07:30:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': '0.0%'}, {'title': 'Credit Card Spending y/y', 'country': 'NZD', 'date': '2024-08-21T10:00:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': '-3.1%'}, {'title': 'Public Sector Net Borrowing', 'country': 'GBP', 'date': '2024-08-21T13:00:00+07:00', 'impact': 'Low', 'forecast': '0.5B', 'previous': '13.6B'}, {'title': 'German 10-y Bond Auction', 'country': 'EUR', 'date': '2024-08-21T16:42:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': '2.43|1.8'}, {'title': 'IPPI m/m', 'country': 'CAD', 'date': '2024-08-21T19:30:00+07:00', 'impact': 'Low', 'forecast': '-0.5%', 'previous': '0.0%'}, {'title': 'RMPI m/m', 'country': 'CAD', 'date': '2024-08-21T19:30:00+07:00', 'impact': 'Low', 'forecast': '-0.9%', 'previous': '-1.4%'}, {'title': 'Crude Oil Inventories', 'country': 'USD', 'date': '2024-08-21T21:30:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': '1.4M'}, {'title': 'FOMC Meeting Minutes', 'country': 'USD', 'date': '2024-08-22T01:00:00+07:00', 'impact': 'High', 'forecast': '', 'previous': ''}, {'title': 'Flash Manufacturing PMI', 'country': 'AUD', 'date': '2024-08-22T06:00:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': '47.4'}, {'title': 'Flash Services PMI', 'country': 'AUD', 'date': '2024-08-22T06:00:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': '50.8'}, {'title': 'Flash Manufacturing PMI', 'country': 'JPY', 'date': '2024-08-22T07:30:00+07:00', 'impact': 'Low', 'forecast': '49.8', 'previous': '49.2'}, {'title': 'French Flash Manufacturing PMI', 'country': 'EUR', 'date': '2024-08-22T14:15:00+07:00', 'impact': 'High', 'forecast': '44.2', 'previous': '44.1'}, {'title': 'French Flash Services PMI', 'country': 'EUR', 'date': '2024-08-22T14:15:00+07:00', 'impact': 'High', 'forecast': '50.2', 'previous': '50.7'}, {'title': 'German Flash Manufacturing PMI', 'country': 'EUR', 'date': '2024-08-22T14:30:00+07:00', 'impact': 'High', 'forecast': '43.4', 'previous': '42.6'}, {'title': 'German Flash Services PMI', 'country': 'EUR', 'date': '2024-08-22T14:30:00+07:00', 'impact': 'High', 'forecast': '52.3', 'previous': '52.0'}, {'title': 'Flash Manufacturing PMI', 'country': 'EUR', 'date': '2024-08-22T15:00:00+07:00', 'impact': 'Medium', 'forecast': '45.7', 'previous': '45.6'}, {'title': 'Flash Services PMI', 'country': 'EUR', 'date': '2024-08-22T15:00:00+07:00', 'impact': 'Medium', 'forecast': '51.7', 'previous': '51.9'}, {'title': 'Flash Manufacturing PMI', 'country': 'GBP', 'date': '2024-08-22T15:30:00+07:00', 'impact': 'High', 'forecast': '52.1', 'previous': '51.8'}, {'title': 'Flash Services PMI', 'country': 'GBP', 'date': '2024-08-22T15:30:00+07:00', 'impact': 'High', 'forecast': '52.7', 'previous': '52.4'}, {'title': 'CBI Industrial Order Expectations', 'country': 'GBP', 'date': '2024-08-22T17:00:00+07:00', 'impact': 'Low', 'forecast': '-23', 'previous': '-32'}, {'title': 'ECB Monetary Policy Meeting Accounts', 'country': 'EUR', 'date': '2024-08-22T18:30:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': ''}, {'title': 'Unemployment Claims', 'country': 'USD', 'date': '2024-08-22T19:30:00+07:00', 'impact': 'High', 'forecast': '233K', 'previous': '227K'}, {'title': 'Flash Manufacturing PMI', 'country': 'USD', 'date': '2024-08-22T20:45:00+07:00', 'impact': 'High', 'forecast': '49.8', 'previous': '49.5'}, {'title': 'Flash Services PMI', 'country': 'USD', 'date': '2024-08-22T20:45:00+07:00', 'impact': 'High', 'forecast': '54.0', 'previous': '56.0'}, {'title': 'Consumer Confidence', 'country': 'EUR', 'date': '2024-08-22T21:00:00+07:00', 'impact': 'Low', 'forecast': '-13', 'previous': '-13'}, {'title': 'Existing Home Sales', 'country': 'USD', 'date': '2024-08-22T21:00:00+07:00', 'impact': 'Medium', 'forecast': '3.92M', 'previous': '3.89M'}, {'title': 'Natural Gas Storage', 'country': 'USD', 'date': '2024-08-22T21:30:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': '-6B'}, {'title': 'Jackson Hole Symposium', 'country': 'All', 'date': '2024-08-22T23:15:00+07:00', 'impact': 'Medium', 'forecast': '', 'previous': ''}, {'title': 'Retail Sales q/q', 'country': 'NZD', 'date': '2024-08-23T05:45:00+07:00', 'impact': 'Medium', 'forecast': '-1.0%', 'previous': '0.5%'}, {'title': 'Core Retail Sales q/q', 'country': 'NZD', 'date': '2024-08-23T05:45:00+07:00', 'impact': 'Low', 'forecast': '-0.8%', 'previous': '0.4%'}, {'title': 'GfK Consumer Confidence', 'country': 'GBP', 'date': '2024-08-23T06:01:00+07:00', 'impact': 'Low', 'forecast': '-12', 'previous': '-13'}, {'title': 'National Core CPI y/y', 'country': 'JPY', 'date': '2024-08-23T06:30:00+07:00', 'impact': 'Low', 'forecast': '2.7%', 'previous': '2.6%'}, {'title': 'Core Retail Sales m/m', 'country': 'CAD', 'date': '2024-08-23T19:30:00+07:00', 'impact': 'High', 'forecast': '-0.4%', 'previous': '-1.3%'}, {'title': 'Retail Sales m/m', 'country': 'CAD', 'date': '2024-08-23T19:30:00+07:00', 'impact': 'High', 'forecast': '-0.3%', 'previous': '-0.8%'}, {'title': 'Corporate Profits q/q', 'country': 'CAD', 'date': '2024-08-23T19:30:00+07:00', 'impact': 'Low', 'forecast': '', 'previous': '0.6%'}, {'title': 'Fed Chair Powell Speaks', 'country': 'USD', 'date': '2024-08-23T21:00:00+07:00', 'impact': 'High', 'forecast': '', 'previous': ''}, {'title': 'New Home Sales', 'country': 'USD', 'date': '2024-08-23T21:00:00+07:00', 'impact': 'Medium', 'forecast': '628K', 'previous': '617K'}, {'title': 'Jackson Hole Symposium', 'country': 'All', 'date': '2024-08-23T23:15:00+07:00', 'impact': 'High', 'forecast': '', 'previous': ''}, {'title': 'BOE Gov Bailey Speaks', 'country': 'GBP', 'date': '2024-08-24T02:00:00+07:00', 'impact': 'High', 'forecast': '', 'previous': ''}, {'title': 'Jackson Hole Symposium', 'country': 'All', 'date': '2024-08-24T23:15:00+07:00', 'impact': 'Medium', 'forecast': '', 'previous': ''}]

db = False
def debug(text):
    if db:
        print(text)

file_path = ".json"
def read():
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        debug(f"read: {e}")
        return {}

def write(data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)

def change_language(date):
    d = date.replace(',', '').split(' ')
    return f"{WEEK[ d[0] ]}, {d[1]} {MONTH[ d[2] ]}"

def user_agent_choice():
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    ]
    return random.choice(user_agent_list)

def get_news_api():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        headers = {
            "User-Agent": user_agent_choice()
        }

        response = requests.get(url, headers=headers)
        debug(f"get_news_api: {response}")

        if response.status_code == 200:
            data = response.json()

            for item in data:
                item["date"] = change_timezone(item["date"])

            return data
    except Exception as e:
        debug(f"get_news_api: {e}")
        time.sleep(5)
        return get_news_api()

def change_timezone(date):
    utc_plus_7 = datetime.fromisoformat(date).astimezone(pytz.timezone("Asia/Jakarta"))
    return utc_plus_7.isoformat()

def create_flag(currency):
    if currency == "All":
        return "‎ " * 7
    return f":flag_{currency[:2].lower()}:"

def formatJsonData(data):
    data_by_date = {}
    last = ""

    temp_data = []
    while len(data) != len(temp_data):
        temp_data = start()

    
    for x in range(len(data)):
        if data[x]["title"] == temp_data[x]["event"]:
            data[x]["time"] = temp_data[x]["time"]

    for item in data:
        date_str = item["date"][:10]
        date = datetime.strptime(date_str, "%Y-%m-%d")
        day = change_language (date.strftime("%a, %d %b") )

        if day not in data_by_date:
            data_by_date[day] = []
    
        if re.search(":", item["time"]):
            time_str = item['date'][11:16]
            timed = datetime.strptime(time_str, "%H:%M")
            time = timed.strftime("%-H:%M").center(8, " ")
        else:
            time = item["time"].center(8, " ")
        
        if item["impact"] != "Low" and item["impact"] != "Medium":
            if time == last:
                time = " " * 8
            else:
                last = time

            data_by_date[day].append(
                f"`{time}`{create_flag(item['country'])}  **{item['country'].upper()}** - **{item['title']}**"
            )

    # Berita harian
    title = f":date: **{today}**\n\n"
    content = ""
    date_content = True
    for events in data_by_date.get(today, []):
        if events[2:4] >= " 4":
            if date_content:
                content += title
                date_content = False
            
            content += f"{events}\n"

    if today.split(",")[0] == "Sabtu" or today.split(",")[0] == "Minggu":
        content += title
        content += "market belum buka."
    elif content == "":
        content += title
        content += "tidak ada news hari ini.\n"

    date_content = True
    for events in data_by_date.get(tomorrow, []):
        if events[2:4] < " 4":
            if date_content:
                content += "\n﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋"
                content += f"\n:date: **{tomorrow}**\n\n"
                date_content = False
            content += f"{events}\n"
            
    weekly = []
    start_day = False
    for day, events in data_by_date.items():
        if re.search("Sabtu", day) and not events:
            weekly.append("Update berikutnya hari minggu jam 1 siang.")
            break

        if today == day or start_day:
            weekly.append(f":date: **{day}**\n")
            if not events:
                weekly.append("tidak ada news. :pepemoney1:")
            else:
                weekly.extend(events)
            weekly.append("\n﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋")

            start_day == True

    cweekly = "\n".join(weekly[:-1])
    debug(f"formatJsonData: {content, cweekly}")
    return content, cweekly

def send_webhook(daily, weekly, data):
    try:
        newData = {}
        webhook = SyncWebhook.from_url(
            os.environ["WEBHOOK_URL"]
            # "https://discord.com/api/webhooks/1274771477941719103/P2dIS_YDdiCvDvATxM47CgfAdL6VKJbkQwokhQ_KU3-oD8TczmHMr9JiFMPIKHNZE5Xe"
        )

        if re.search("Minggu", today):
            if "WEEKLY_ID" in data:
                webhook.delete_message(data["WEEKLY_ID"])

            weekly = webhook.send(
                embed=discord.Embed(description=weekly, color=discord.Color.random()).set_footer(text='*Waktu: WIB (Asia/Jakarta)\n*Khusus berita dampak GEDE'),
                wait=True,
            )

            newData["WEEKLY_ID"] = weekly.id
        else:
            weekly = webhook.edit_message(data["WEEKLY_ID"],
                embed=discord.Embed(description=weekly, color=discord.Color.random()).set_footer(text='*Waktu: WIB (Asia/Jakarta)\n*Khusus berita dampak GEDE')
            )
            newData["WEEKLY_ID"] = data["WEEKLY_ID"]
            
        '''
        if "DAILY_ID" in data:
            webhook.delete_message(data["DAILY_ID"])
        
        daily = webhook.send(
            username="Daily News Schedule"
            embed=discord.Embed(description=daily, color=discord.Color.random()),
            wait=True,
        )

        newData["DAILY_ID"] = daily.id
        '''

        debug(f"send_webhook: {newData}")
        return newData

    except Exception as e:
        debug(f"send_webhook : {e}")
        time.sleep(5)
        return send_webhook(daily, weekly, data)

def main():
    data = read()
    content = formatJsonData(get_news_api())
    # content = formatJsonData(news)
    newData = send_webhook(content[0], content[1], data)
    write(newData)


# now = datetime.now(pytz.timezone('Asia/Jakarta'))
now = datetime.strptime(os.environ["UPDATE_TIME"], "%Y-%m-%d %H:%M")
today = change_language( now.strftime("%a, %d %b") )
tomorrow = change_language( (now + timedelta(days=1)).strftime("%a, %d %b") )
# today = 'Sabtu, 10 Agustus'

main()
