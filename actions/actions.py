import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionExtractProductCode(Action):
    def name(self):
        return "action_extract_product_code"

    def run(self, dispatcher, tracker, domain):
        # Trích xuất giá trị entity "productcode" từ NLU
        product_code = tracker.get_slot("productcode")

        # Gán giá trị entity vào slot "product_code"
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

        # Sử dụng template từ responses để tạo thông điệp và điền giá trị vào placeholders
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
