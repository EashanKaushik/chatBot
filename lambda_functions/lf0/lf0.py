import json
import datetime


def lambda_handler(event, context):

    print(event)  # logging event in cloudwatch logs

    botResponse = {"messages": list()}
    botRequest = event.copy()
    messageFromClient = botRequest["messages"]

    for message in messageFromClient:

        current_message = message["unstructured"]["text"]
        # do something on the current message to get response
        current_message_response = "Application under development. Search functionality will be implemented in Assignment 2 - ek3575"

        botResponse["messages"].append({
            "type": message["type"],
            "unstructured": {
                "id": message["unstructured"]["id"],
                "text": current_message_response,
                "timestamp": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            }
        })

    return botResponse
