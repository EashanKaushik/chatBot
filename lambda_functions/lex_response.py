# this file is present with LF1 lambda function
class LexResponse:
    def __init__(self, event):
        self._event = event
        self._intent = self._event["currentIntent"]["name"]
        self._slots = self._event["currentIntent"]["slots"]

    def close(self, message, fulfillmentState="Fulfilled"):  # or Failed
        return {
            # "sessionAttributes": self._event["session_attributes"],
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": fulfillmentState,
                "message":  {
                    'contentType': 'PlainText',
                    'content': message
                }
            }
        }

    # delegate next course of action based on the bot configuration
    def delegate(self):
        if "session_attributes" in self._event:
            return {
                "sessionAttributes": self._event["session_attributes"],
                "dialogAction": {
                    "type": "Delegate",
                    "slots": self._slots
                }
            }
        else:
            return {
                "sessionAttributes": {},
                "dialogAction": {
                    "type": "Delegate",
                    "slots": self._slots
                }
            }

    # if the validation fails we need to ask for a new value of the slot
    def elecit_slot(self, slotToElicit, message):
        return {
            # "sessionAttributes": self._event["session_attributes"],
            'dialogAction': {
                'type': 'ElicitSlot',
                'intentName': self._intent,
                'slots': self._slots,
                'slotToElicit': slotToElicit,
                'message': message
            }
        }

    def elecit_intent(self, message):
        return {
            "dialogAction": {
                "type": "ElicitIntent",
                "message": {
                    'contentType': 'PlainText',
                    'content': message
                }
            }
        }

    def confirm_intent(self, message):
        return {
            "dialogAction": {
                "type": "ConfirmIntent",
                "message": {
                    'contentType': 'PlainText',
                    'content': message
                },
                "intentName": "DiningSuggestionsIntent",
                "slots": {}
            }
        }

    @property
    def event(self):
        return self._event

    @property
    def intent(self):
        return self._intent

    @property
    def slots(self):
        return self._slots
