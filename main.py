import os
import json
import pytz
import time
import discord
import requests
from discord import SyncWebhook
from datetime import datetime, timedelta

week = {
    'Mon' : 'Senin',
    'Tue' : 'Selasa',
    'Wed' : 'Rabu',
    'Thu' : 'Kamis',
    'Fri' : 'Jumat',
    'Sat' : 'Sabtu',
    'Sun' : 'Minggu'
}

month = {
    'Jan' : 'Januari',
    'Feb' : 'Februari',
    'Mar' : 'Maret',
    'Apr' : 'April',
    'May' : 'Mei',
    'Jun' : 'Juni',
    'Jul' : 'Juli',
    'Aug' : 'Agustus',
    'Sep' : 'September',
    'Oct' : 'Oktober',
    'Nov' : 'November',
    'Dec' : 'Desember'
}

debug = False
def debug(text):
    if debug:
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

def changeLang(date):
    d = date.replace(',', '').split(' ')
    return f"{week[ d[0] ]}, {d[1]} {month[ d[2] ]}"

def getNewsApi():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()

            for item in data:
                item["date"] = changeTimezone(item["date"])

            debug(f"getNewsApi: {data}")
            return data
    except Exception as e:
        debug(f"getNewsApi: {e}")
        time.sleep(5)
        return getNewsApi()

def changeTimezone(date):
    utc_plus_7 = datetime.fromisoformat(date).astimezone(pytz.timezone("Asia/Jakarta"))
    return utc_plus_7.isoformat()

def formatJsonData(data):
    data_by_date = {}
    last = ""
    for item in data:
        date_str = item["date"][:10]
        date = datetime.strptime(date_str, "%Y-%m-%d")
        day = changeLang (date.strftime("%a, %d %b") )
        time = (
            "  All Day ` "
            if item["impact"] == "Holiday"
            else f"   {item['date'][11:16]}  ` "
        )
        if day not in data_by_date:
            data_by_date[day] = []
    
        data_by_date[day].append(
            f":flag_{item['country'][:2].lower()}:  **{item['country']}**`{time}**{item['title']}**"
        )
        
     

    now = datetime.strptime(os.environ["UPDATE_TIME"], "%Y-%m-%d %H:%M")
    # now = datetime.now(pytz.timezone('Asia/Jakarta'))
    today = changeLang( now.strftime("%a, %d %b") )
    tomorrow = changeLang( (now + timedelta(days=1)).strftime("%a, %d %b") )
    # today = 'Saturday, 10 August 2024'

    title = f":date: **{today}**\n\n"
    content = ""
    date_content = True
    for events in data_by_date.get(today, []):
        if events[22:24] >= "04":
            if date_content:
                content += title
                date_content = False
            
            content += f"{events}\n"

    if today.split(",")[0] == "Sabtu" or today.split(",")[0] == "Minggu":
        content += title
        content += "market hasn't open yet.\nget out from your bed now.\n"
    elif content == "":
        content += title
        content += "nothing news today, go touch some grass.\n"

    date_content = True
    for events in data_by_date.get(tomorrow, []):
        if events[22:24] < "04":
            if date_content:
                content += "\n﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋"
                content += f"\n:date: **{tomorrow}**\n\n"
                date_content = False
            content += f"{events}\n"
            
    weekly = []
    if today.split(",")[0] == "Minggu":
        for day, events in data_by_date.items():
            weekly.append(f":date: **{day}**\n")
            weekly.extend(events)
            weekly.append("\n﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋")

    cweekly = "\n".join(weekly[:-1])
    debug(f"formatJsonData: {content, cweekly}")
    return content, cweekly

def filterNews(data):
    filtered_data = []
    for item in data:
        if item["impact"] != "Low" and item["impact"] != "Medium":
            filtered_item = item.copy()
            filtered_item["date"] = changeTimezone(filtered_item["date"])
            filtered_data.append(filtered_item)

    debug(f"filterNews: {filtered_data}")
    return filtered_data

def sendWebhook(daily, weekly, data):
    try:
        newData = {}
        webhook = SyncWebhook.from_url(
            os.environ["WEBHOOK_URL"]
            # "https://discord.com/api/webhooks/1271664086563946536/c4AnCMnD2c_PNVgHVb3eW49IXNncw-mu9VFkIV-nTi1Y_PW9m_C8HuQdxweCwOsfCUWd"
        )

        if weekly:
            if "WEEKLY_ID" in data:
                webhook.delete_message(data["WEEKLY_ID"])

            weekly = webhook.send(
                embed=discord.Embed(description=weekly, color=discord.Color.random()).set_footer(text='*Waktu: WIB (Asia/Jakarta)\n*Khusus berita dampak GEDE'),
                wait=True,
            )

            newData["WEEKLY_ID"] = weekly.id

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

        debug(f"sendWebhook: {newData}")
        return newData

    except Exception as e:
        debug(f"sendWebhook : {e}")
        time.sleep(5)
        return sendWebhook(daily, weekly, data)

def main():
    data = read()
    content = formatJsonData(filterNews(getNewsApi()))
    newData = sendWebhook(content[0], content[1], data)
    write(newData)

main()
