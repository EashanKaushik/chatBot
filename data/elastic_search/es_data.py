import boto3
import os
import json
from datetime import datetime
from dotenv import load_dotenv

CATEGORIES = ["japanese, All", "italian, All",
              "mexican, All", "chinese, All",
              "indpak, All", "french, All",
              "thai, All", "irish, All"]

CURRENT_DIR = os.getcwd()
SEEN_ID = set()

if not os.path.isdir(os.path.join(CURRENT_DIR, "es-data")):
    os.mkdir(os.path.join(CURRENT_DIR, "es-data"))

DATA_DIR = os.path.join(CURRENT_DIR, "es-data")

current_id = 1

for category in CATEGORIES:
    cuisine = category.split(",")[0]
    cuisine_path = os.path.join(CURRENT_DIR, cuisine)

    print(f"{cuisine} has started!")

    for file in os.listdir(cuisine_path):
        with open(os.path.join(cuisine_path, file)) as f:
            data = json.load(f)
            try:
                for buisness in data["businesses"]:
                    if buisness["id"] in SEEN_ID:
                        continue

                    SEEN_ID.add(buisness["id"])

                    id_dict = {
                        "index": {"_index": "restaurants", "_id": str(current_id)}}
                    current_id += 1

                    f1 = open(os.path.join(DATA_DIR, "esdata.txt"), "a")
                    f1.write(json.dumps(id_dict))
                    f1.write("\n")
                    f1.write(
                        json.dumps({"restaurantId": buisness["id"], "cuisine": cuisine}))
                    f1.write("\n")
                    f1.close()
            except Exception as ex:
                print("Exception")
                continue
