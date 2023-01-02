import platform
import aiohttp
import asyncio
from datetime import datetime, timedelta
import json, os

currencies = ["USD", "EUR"]
FILE_PATH = "currencies.json"


def create_dates():
    days = int(input("Enter max 10 days: "))
    if days > 10:
        print("Too many days, try again")
        return create_dates()
    today: datetime = datetime.today()
    return [(today - timedelta(day)).strftime("%d.%m.%Y") for day in range(days)]


def searched_currencies(result, day):
    result_fin = []
    searching_currencies = [
        currencie
        for currencie in result["exchangeRate"]
        if currencie["currency"] in currencies
    ]
    for currencie in searching_currencies:
        result_fin.append(
            {
                day: {
                    currencie["currency"]: {
                        "sale": currencie["saleRateNB"],
                        "purchase": currencie["purchaseRateNB"],
                    }
                }
            }
        )
    return write_to_json(result_fin)


def write_to_json(data):
    if os.path.exists(FILE_PATH):
        load_data = json.load(open(FILE_PATH))
        load_data.append(data)
    else:
        load_data = [data]
    with open(FILE_PATH, "w") as fh:
        json.dump(load_data, fh, indent=4)
        print("Json file was updated")


async def make_request(day):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.privatbank.ua/p24api/exchange_rates?json&date={day}"
        ) as response:
            result = await response.json()
            return searched_currencies(result, day)


async def main(futures):
    await asyncio.gather(*futures)


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    dates = create_dates()
    futures = [make_request(day) for day in dates]
    asyncio.run(main(futures))
