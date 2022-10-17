import json
import datetime
import boto3


def lambda_handler(event, context):

    print(event)  # logging event in cloudwatch logs

    client = boto3.client('lex-runtime')

    botResponse = {"messages": list()}
    botRequest = event.copy()
    messageFromClient = botRequest["messages"]

    for message in messageFromClient:

        current_message = message["unstructured"]["text"]
        # do something on the current message to get response

        current_message_response = client.post_text(
            botName='chatBot',
            botAlias='chatBotDiningSuggestions',
            userId='user03',
            inputText=current_message,
            activeContexts=[]
        )

        print(current_message_response)

        # current_message_response = "Application under development. Search functionality will be implemented in Assignment 2"

        botResponse["messages"].append({
            "type": message["type"],
            "unstructured": {
                "id": message["unstructured"]["id"],
                "text": current_message_response["message"],
                "timestamp": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            }
        })

    print(f"#####{botResponse}")

    return botResponse
