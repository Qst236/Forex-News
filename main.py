import os
import json
import pytz
import time
import discord
import requests
from discord import SyncWebhook
from datetime import datetime

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

            # Extract dates from first and last elements
            firstDateStr = data[0]["date"]
            lastDateStr = data[-1]["date"]

            # Convert dates to datetime objects
            first_date = datetime.strptime(firstDateStr, "%Y-%m-%dT%H:%M:%S%z")
            last_date = datetime.strptime(lastDateStr, "%Y-%m-%dT%H:%M:%S%z")

            # Format dates as "DD Ags - DD Ags"
            first_date_formatted = first_date.strftime("%d %b")
            last_date_formatted = last_date.strftime("%d %b")

            # Combine formatted dates with hyphen
            dateRange = f"{first_date_formatted} - {last_date_formatted}"

            with open("news.json", "w") as outfile:
                json.dump(data, outfile, indent=2)

            return data, dateRange
    except Exception:
        print("Mengulang pengambilan news")
        time.sleep(5)
        return getNewsApi()

def changeTimezone(date):
    utc7 = datetime.fromisoformat(date).astimezone(pytz.timezone("Asia/Jakarta"))
    return utc7.isoformat()  # Kembalikan ke format ISO 8601


def formatJsonData(data):
    """Formats JSON data into the desired text string."""
    data_by_date = {}
    for item in data:
        date_str = item["date"][:10]
        date = datetime.strptime(date_str, "%Y-%m-%d")
        day = date.strftime("%A, %d %B")
        time = (
            "  All Day ` "
            if item["impact"] == "Holiday"
            else f"   {item['date'][11:16]}  ` "
        )
        if day not in data_by_date:
            data_by_date[day] = []
        data_by_date[day].append(
            f":flag_{item['country'][:2].lower()}:  `{item['country']}{time}**{item['title']}**\n"
        )

    text_output = ""
    for day, events in data_by_date.items():
        text_output += f"**{day}**\n"
        text_output += "".join(events) + "\n"
    return text_output

def filterNews(data):
    filtered_data = []
    for item in data:
        if item["impact"] != "Low" and item["impact"] != "Medium":
            # Copy item dictionary to avoid modifying original data
            filtered_item = item.copy()

            filtered_item["date"] = changeTimezone(filtered_item["date"])

            # del filtered_item['forecast']
            # del filtered_item['previous']
            # del filtered_item['url']
            filtered_data.append(filtered_item)
    return filtered_data

def sendWebhook(dateRange, text):
    try:
        webhook = SyncWebhook.from_url(
            os.environ.get('WEBHOOK_URL')
        )
        webhook.send(embed=discord.Embed(title=f"Economic Calendar  :date:  {dateRange}", description=text, color=0x00ff00))

    except Exception:
        print("Gagal mengirim webhook")
        time.sleep(5)
        return sendWebhook()

# Format and print the text
def main():
    JsonData = getNewsApi()
    text = formatJsonData(filterNews(JsonData[0]))
    print(text)
    sendWebhook(JsonData[1], text)

main()
