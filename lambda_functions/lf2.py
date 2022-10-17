import json
import boto3
import os
import warnings
import numpy as np
import random
import requests
# from dotenv import load_dotenv

# load_dotenv()

SQS_ENDPOINT = ""  # TODO
ELASTIC_SEARCH_URL = ""  # TODO
ES_INDEX = "restaurants"
ELASTIC_SEARCH_ENDPOINT = ELASTIC_SEARCH_URL + "/" + ES_INDEX + "/_search"
SESSION_CREDENTIALS = boto3.Session().get_credentials()
DYNAMO_TABLE_NAME = "yelp-restaurants"
SENDER_EMAIL = "ek3575@nyu.edu"


def lambda_handler(event, context):

    # try:
    location, cuisine, dine_time, party_size, contact, receipt_handle, if_message = get_sqs_message()

    if not if_message or not verify_identity(contact):
        print("Email not verified or no message in SQS")
        return {
            "statusCode": 404,
            "message": json.dumps("Email not verified or no message in SQS")
        }

    recommendations = elastic_search(cuisine, 5)

    data = get_recommendation_information(recommendations)

    messageId = send_email(data, request=(
        location, cuisine, dine_time, party_size, contact))

    delete_sqs_message(receipt_handle)

    return {
        'statusCode': 200,
        'body': json.dumps(f"Email Sent to {contact}")
    }


def get_sqs_message():
    sqs = boto3.client('sqs', region_name="us-east-1")
    poll_response = sqs.receive_message(
        QueueUrl=SQS_ENDPOINT,
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0)
    print(poll_response)
    if "Messages" not in poll_response:
        return None, None, None, None, None, None, False
    location, cuisine, dine_time, party_size, contact = get_arrtibute_values(
        poll_response)

    return location, cuisine, dine_time, party_size, contact, poll_response['Messages'][0]['ReceiptHandle'], True


def delete_sqs_message(receipt_handle):

    sqs = boto3.client('sqs', region_name="us-east-1")

    delete_response = sqs.delete_message(
        QueueUrl=SQS_ENDPOINT,
        ReceiptHandle=receipt_handle)

    print(delete_response)

    return delete_response


def get_arrtibute_values(response):
    message_attributes = json.loads(response["Messages"][0]["Body"])

    location = message_attributes["Location"]["StringValue"]
    cuisine = message_attributes["Cuisine"]["StringValue"]
    dine_time = message_attributes["Dine_Time"]["StringValue"]
    party_size = message_attributes["Party_Size"]["StringValue"]
    contact = message_attributes["Contact"]["StringValue"]

    return location, cuisine, dine_time, party_size, contact


def elastic_search(cuisine, number_of_recommendations=5):
    query = {
        "query": {
            "match": {
                "cuisine": cuisine
            }
        }
    }

    response = json.loads(requests.get(ELASTIC_SEARCH_ENDPOINT, auth=("chatbotek3575", "Eashan@78542325"),
                          headers={"Content-Type": "application/json"}, data=json.dumps(query)).content.decode('utf-8'))

    hits = response["hits"]["hits"]

    random.shuffle(hits)

    recommendations = list()

    number_of_recommendations = number_of_recommendations if len(
        hits) > number_of_recommendations else len(hits)

    for i in range(number_of_recommendations):
        recommendations.append(hits[i]["_source"]["restaurantId"])

    return recommendations


def get_item(response):
    item = response["Item"]
    print(item)

    restaurantId = item["restaurantId"]["S"]
    insertedAtTimestamp = item["insertedAtTimestamp"]["S"]
    name = item["name"]["S"]
    location = item["address"]["S"]
    coordinates = {"lattitude": item["coordinates"]["L"][0]
                   ["N"], "longitide": item["coordinates"]["L"][1]["N"]}
    review_count = item["review_count"]["N"]
    rating = item["rating"]["N"]
    cuisine = item["cuisine"]["S"]

    return restaurantId, insertedAtTimestamp, name, location, coordinates, review_count, rating, cuisine


def get_recommendation_information(recommendations):

    data = list()

    db = boto3.client("dynamodb", region_name='us-east-1')

    for recommendation in recommendations:
        response = db.get_item(TableName=DYNAMO_TABLE_NAME, Key={
                               "restaurantId": {"S": recommendation}})

        data.append(tuple(get_item(response)))

    return data


def send_email(data, request):

    location, cuisine, dine_time, party_size, contact = request

    ses = boto3.client('ses')

    charset = "UTF-8"

    subject = f"ChatBot Suggestions for {cuisine} restaurants in {location}"
    body_text = f"Dine Time: {dine_time}\nParty size: {party_size}\nSuggestions:\n"

    for item in data:
        restaurantId, insertedAtTimestamp, name, location, coordinates, review_count, rating, cuisine = item
        body_text += f"Name: {name}, Location: {location}, Reviews: {review_count}, rating: {rating}, cuisine: {cuisine}, Lattitude{coordinates['lattitude']}, Longitude: {coordinates['longitide']}\n"

    response = ses.send_email(Source=SENDER_EMAIL,
                              Destination={
                                  'ToAddresses': [
                                      contact,
                                  ],
                              }, Message={
                                  'Subject': {
                                      'Data': subject,
                                      'Charset': charset
                                  },
                                  'Body': {
                                      'Text': {
                                          'Data': body_text,
                                          'Charset': charset
                                      }
                                  }
                              },
                              )

    print(response)

    return response["MessageId"]


def verify_identity(contact):

    ses = boto3.client('ses')
    verified_emails = ses.list_verified_email_addresses()

    print(verified_emails["VerifiedEmailAddresses"])

    if contact in set(verified_emails["VerifiedEmailAddresses"]):
        return True

    response = ses.verify_email_identity(
        EmailAddress=contact)

    return False
