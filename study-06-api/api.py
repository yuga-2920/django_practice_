import requests
import urllib
import json
import pandas as pd


def get_api(url, params):
    result = requests.get(url, params=params)
    return result.json()

def set_api_parameter():
    app_id = 1019079537947262807
    params = {
        "format"        : "json",
        "applicationId" : [app_id],
        "formatVersion" : 2,
        }
    return params

def get_item_name(items):
    item_name = []
    for item in items:
        item_name.append(item["itemName"])

def get_item_price(items):
    item_price = []
    for item in items:
        item_price.append(item["itemPrice"])

def get_name_and_price():
    keyword = "鬼滅の刃"
    params = set_api_parameter()
    params["keyword"] = keyword
    
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706?"

    items = get_api(url, params)["Items"]
    
    get_item_name(items)
    get_item_price(items)

def get_max_and_min_item():
    url = "https://app.rakuten.co.jp/services/api/Product/Search/20170426?"
    items = get_api(url, set_api_parameter())["Products"]
    
    max_price = int(items[0]["maxPrice"])
    min_price = int(items[0]["minPrice"])

    print(max_price)
    print(min_price)

def create_csv():
    genreId = 100283
    params = set_api_parameter()
    params["genreId"] = genreId
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20170628?"
    
    item_name = []
    items =  get_api(url, params)["Items"]
    for item in items:
        item_name.append(item["itemName"])

    df = pd.DataFrame({"名前": item_name})
    df.to_csv(f"result_of_{ genreId }.csv", index=False)

get_name_and_price()
get_max_and_min_item()
create_csv()