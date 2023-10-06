# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for an assistant that schedules reminders and
# reacts to external events.

from typing import Any, Text, Dict, List
import datetime
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ReminderScheduled, ReminderCancelled, SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionSetReminder(Action):
    """Schedules a reminder, supplied with the last message's entities."""

    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("I will remind you in 5 seconds.")

        date = datetime.datetime.now() + datetime.timedelta(seconds=5)
        entities = tracker.latest_message.get("entities")

        reminder = ReminderScheduled(
            "EXTERNAL_reminder",
            trigger_date_time=date,
            entities=entities,
            name="my_reminder",
            kill_on_user_message=False,
        )

        return [reminder]


class ActionReactToReminder(Action):
    """Reminds the user to call someone."""

    def name(self) -> Text:
        return "action_react_to_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        name = next(tracker.get_slot("PERSON"), "someone")
        dispatcher.utter_message(f"Remember to call {name}!")

        return []


class ActionTellID(Action):
    """Informs the user about the conversation ID."""

    def name(self) -> Text:
        return "action_tell_id"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        conversation_id = tracker.sender_id

        dispatcher.utter_message(f"The ID of this conversation is '{conversation_id}'.")
        dispatcher.utter_message(
            f"Trigger an intent with: \n"
            f'curl -H "Content-Type: application/json" '
            f'-X POST -d \'{{"name": "EXTERNAL_dry_plant", '
            f'"entities": {{"plant": "Orchid"}}}}\' '
            f'"http://localhost:5005/conversations/{conversation_id}'
            f'/trigger_intent?output_channel=latest"'
        )

        return []


class ActionWarnDry(Action):
    """Informs the user that a plant needs water."""

    def name(self) -> Text:
        return "action_warn_dry"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        plant = next(tracker.get_latest_entity_values("plant"), "someone")
        dispatcher.utter_message(f"Your {plant} needs some water!")

        return []


class ForgetReminders(Action):
    """Cancels all reminders."""

    def name(self) -> Text:
        return "action_forget_reminders"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("Okay, I'll cancel all your reminders.")

        # Cancel all reminders
        return [ReminderCancelled()]

class ActionExtractProductCode(Action):
    def name(self):
        return "action_extract_product_code"

    def run(self, dispatcher, tracker, domain):
        product_code = tracker.get_slot("productcode")
        return [SlotSet("productcode", product_code)]


class ActionGetProductInfo(Action):
    def name(self):
        return "action_get_product_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        product_code = tracker.get_slot("productcode")
        # Gửi yêu cầu đến API dựa trên product_code
        api_url = f"https://hacom.vn/ajax/get_json.php?action=product&action_type=info&sku={product_code}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            product_id = data.get("productId")
            product_sku = data.get("productSKU")
            product_name = data.get("productName")
            product_price = data.get("price")
            product_brand = data.get("brand", {}).get("name")
            product_url = data.get("productUrl")
            market_price = data.get("marketPrice")
            warranty = data.get("warranty")
            shipping = data.get("shipping")
            description = data.get("productSummary")

        message = domain["responses"]["utter_product_info"][0]["text"].format(
            product_id=product_id,
            product_sku=product_sku,
            product_name=product_name,
            product_price=product_price,
            product_brand=product_brand,
            product_url=product_url,
            market_price=market_price,
            warranty=warranty,
            shipping=shipping,
            description=description,
        )

        dispatcher.utter_message(message)
        return []
