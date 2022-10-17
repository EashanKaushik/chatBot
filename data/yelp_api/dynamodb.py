import boto3
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
CATEGORIES = ["japanese, All", "italian, All",
              "mexican, All", "chinese, All",
              "indpak, All", "french, All",
              "thai, All", "irish, All"]

CURRENT_DIR = os.getcwd()
SEEN_ID = set()


def make_dynamo_item(buisness, cuisine):
    item = dict()
    if "id" in buisness and buisness["id"] not in SEEN_ID:
        SEEN_ID.add(buisness["id"])

        item["restaurantId"] = {"S": buisness["id"]}
    else:
        return False

    item["insertedAtTimestamp"] = {
        "S": datetime.now().strftime("%d-%m-%Y %H:%M:%S")}

    if "name" in buisness:
        item["name"] = {"S": buisness["name"]}

    if "location" in buisness:
        if "display_address" in buisness["location"]:
            item["address"] = {"S": ", ".join(
                buisness["location"]["display_address"])}

    if "coordinates" in buisness:
        item["coordinates"] = {"L": [{"N": str(buisness["coordinates"]["latitude"])}, {
            "N": str(buisness["coordinates"]["longitude"])}]}

    if "review_count" in buisness:
        item["review_count"] = {"N": str(buisness["review_count"])}

    if "rating" in buisness:
        item["rating"] = {"N": str(buisness["rating"])}

    item["cuisine"] = {"S": cuisine}

    return item


client = boto3.client(
    'dynamodb',
    aws_access_key_id=os.getenv('ACCESS_KEY'),
    aws_secret_access_key=os.getenv('SECRET_KEY'),
    region_name='us-east-1')


for category in CATEGORIES:
    cuisine = category.split(",")[0]

    cuisine_path = os.path.join(CURRENT_DIR, cuisine)
    count = 0
    print(f"{cuisine} has started!")
    for file in os.listdir(cuisine_path):
        with open(os.path.join(cuisine_path, file)) as f:
            data = json.load(f)

            print(data.keys(), file)
            try:
                count += len(data["businesses"])
                for buisness in data["businesses"]:
                    item = make_dynamo_item(buisness, cuisine)
                                        
                    if not item:
                        print("Duplicated Seen")
                        continue

                    response = client.put_item(TableName="yelp-restaurants",
                                               Item=item)
            except Exception as ex:
                continue

    print(f"{cuisine} has ended: {count}")
