import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
url = f"https://api.yelp.com/v3/businesses/search"

client_id = os.getenv('CLIENT_ID')
API_KEY = os.getenv('API_KEY')

CATEGORIES = ["japanese, All", "italian, All",
              "mexican, All", "chinese, All",
              "indpak, All", "french, All",
              "thai, All", "irish, All"]

HEADERS = {"Authorization": f"bearer {API_KEY}"}
LIMIT = 50


def get_data(current_offset, category, category_dir):
    PARAMETERS = {
        "term": "food",
        "location": "manhattan",
        "categories": category,
        "limit": LIMIT,
        "offset": current_offset
    }

    response = requests.get(url=url, params=PARAMETERS, headers=HEADERS).json()

    file = os.path.join(
        category_dir, f'{category.split(",")[0]} - {current_offset}.json')

    with open(file, 'w') as fp:
        json.dump(response, fp, sort_keys=True, indent=4)

    return response


currentDirectory = os.getcwd()

for category in CATEGORIES:

    current_offset = 0

    category_dir = os.path.join(currentDirectory, category.split(",")[0])

    if not os.path.isdir(category_dir):
        os.mkdir(category_dir)

    response = get_data(current_offset, category, category_dir)

    total = response["total"]

    while current_offset < total:
        _ = get_data(current_offset, category, category_dir)
        current_offset += 50
