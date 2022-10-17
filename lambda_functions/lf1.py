import json
import re
from datetime import datetime
from lex_response import LexResponse
import boto3
import json

CITIES = set(["manhattan"])
CUISINES = set(["japanese", "italian",
                "mexican", "chinese",
                "indpak", "french",
                "thai", "irish"])

OPEN_TIME = datetime.strptime("09:00", "%H:%M")
CLOSE_TIME = datetime.strptime("22:00", "%H:%M")

CURRENT_TIME = datetime.strptime(datetime.now().strftime("%H:%M"), "%H:%M")


def lambda_handler(event, context):

    response = LexResponse(event)

    print(event)

    if response.intent == "DiningSuggestionsIntent":
        if response.event["invocationSource"] == "DialogCodeHook":
            return dining_suggestion_validate(response)
        print("first if")
        if response.event["invocationSource"] == "FulfillmentCodeHook":
            print("Second if")
            return dining_suggestion(response)

    if response.intent == "GreetingIntent":
        return greeting_intent(response)

    if response.intent == "ThankYouIntent":
        return thankyou_intent(response)

    return response.confirm_intent(message="Do you want Dining Suggestions?")


def get_slots(response):
    return response.event["currentIntent"]["slots"]["Location"],  response.event["currentIntent"]["slots"]["Cuisine"], response.event["currentIntent"]["slots"]["Dine_Time"], response.event["currentIntent"]["slots"]["Party_Size"], response.event["currentIntent"]["slots"]["Contact"]


def slots_validation_response(validation_response, message, slotToElicit):
    return {"isValid": validation_response, "slotToElicit": slotToElicit} if not message else {"isValid": validation_response, "slotToElicit": slotToElicit, "message": {"contentType": "PlainText", "content": message}}


def slots_validation(city, cuisine, time, people, email):

    if city is not None and city.lower() not in CITIES:
        return slots_validation_response(False, f"We do not serve this city try {', '.join(list(CITIES))}", "Location")

    if cuisine is not None and cuisine.lower() not in CUISINES:
        return slots_validation_response(False, f"Choose one of the cuisines {', '.join(list(CUISINES))}", "Cuisine")

    # MM-DD-YYYY HH:MM
    if time is not None:
        if len(time) != 5:
            return slots_validation_response(False, f"Please specify time in following format, with am or pm.", "Dine_Time")
        else:
            try:
                response_time = datetime.strptime(time, "%H:%M")
                if response_time < OPEN_TIME or response_time > CLOSE_TIME or response_time < CURRENT_TIME:
                    raise Exception("A error occured!")
            except Exception as ex:
                return slots_validation_response(False, f"We serve between {OPEN_TIME.strftime('%H:%M')} and {CLOSE_TIME.strftime('%H:%M')}. Also time should be in the future", "Dine_Time")

    if people is not None and (int(people) >= 20 or int(people) <= 0):
        return slots_validation_response(False, f"Choose people in between 1 and 16", "Party_Size")

    email_regex = re.compile(
        r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    if email is not None and not email_regex.fullmatch(email):
        print("email invalid")
        return slots_validation_response(False, "Please enter a valid email address.", "Contact")

    print(slots_validation_response(True, None, None))
    return slots_validation_response(True, None, None)


def dining_suggestion_validate(response):
    city, cuisine, time, people, email = get_slots(response)
    slot_validation_res = slots_validation(city, cuisine, time, people, email)

    if not slot_validation_res["isValid"]:
        return response.elecit_slot(slotToElicit=slot_validation_res["slotToElicit"], message=slot_validation_res["message"])
    print(f"#### {response.delegate()}")
    return response.delegate()


def dining_suggestion(response):
    city, cuisine, time, people, email = get_slots(response)

    print(city, cuisine, time, people, email)
    message = {
        "Location": {
            "Datatype": "String",
            "StringValue": response.slots["Location"]
        },
        "Cuisine": {
            "Datatype": "String",
            "StringValue": response.slots["Cuisine"]
        },
        "Dine_Time": {
            "Datatype": "String",
            "StringValue": response.slots["Dine_Time"]
        },
        "Party_Size": {
            "Datatype": "String",
            "StringValue": str(response.slots["Party_Size"])
        },
        "Contact": {
            "Datatype": "String",
            "StringValue": response.slots["Contact"]
        },

    }

    print(message)

    send_message_to_sqs(message)
    print(response.close(message="Expect an email shortly, Thanks!",
          fulfillmentState="Fulfilled"))
    return response.close(message="Expect an email shortly, Thanks!", fulfillmentState="Fulfilled")


def send_message_to_sqs(message):
    sqs_client = boto3.client("sqs", region_name="us-east-1")

    response = sqs_client.send_message(
        QueueUrl="",  # TODO
        MessageBody=json.dumps(message)
    )


def greeting_intent(response):
    print(response.elecit_intent(message="Try saying dining suggestions!"))
    return response.elecit_intent(message="Try saying dining suggestions!")


def thankyou_intent(response):
    return response.elecit_intent(message="Your Welcome! Come back soon!")
