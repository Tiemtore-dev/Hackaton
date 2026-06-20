import logging
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.api_url = f"https://graph.facebook.com/{settings.WHATSAPP_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json",
        }

    async def send_text_message(self, to: str, text: str) -> bool:
        """
        Sends a simple text message to a WhatsApp number.
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
        
        # If API token is default/fake, just mock-send to stdout
        if "fake" in settings.WHATSAPP_API_TOKEN or "fake" in settings.WHATSAPP_PHONE_NUMBER_ID:
            logger.info(f"[MOCK WHATSAPP SEND to {to}]: {text}")
            print(f"\n📢 [MOCK WHATSAPP TO {to}]:\n{text}\n")
            return True

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=10.0
                )
                if response.status_code in [200, 201]:
                    logger.info(f"Message sent to {to} successfully.")
                    return True
                else:
                    logger.error(
                        f"Failed to send message to {to}. Code: {response.status_code}, Response: {response.text}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Error calling Meta WhatsApp API for {to}: {str(e)}")
            return False

    async def send_interactive_buttons(self, to: str, text: str, buttons: list[dict]) -> bool:
        """
        Sends an interactive message with buttons (max 3 buttons).
        Each button in the list should be a dict: {"id": "button_id", "title": "Button Title"}
        """
        if len(buttons) > 3:
            buttons = buttons[:3]

        formatted_buttons = []
        for btn in buttons:
            formatted_buttons.append({
                "type": "reply",
                "reply": {
                    "id": btn["id"],
                    "title": btn["title"]
                }
            })

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": text},
                "action": {
                    "buttons": formatted_buttons
                }
            }
        }

        if "fake" in settings.WHATSAPP_API_TOKEN or "fake" in settings.WHATSAPP_PHONE_NUMBER_ID:
            btn_titles = ", ".join([f"[{b['title']}]" for b in buttons])
            logger.info(f"[MOCK WHATSAPP BTN to {to}]: {text} | Buttons: {btn_titles}")
            print(f"\n📢 [MOCK WHATSAPP TO {to} with Buttons]:\n{text}\n🔘 {btn_titles}\n")
            return True

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=10.0
                )
                if response.status_code in [200, 201]:
                    logger.info(f"Interactive message sent to {to} successfully.")
                    return True
                else:
                    logger.error(
                        f"Failed to send interactive message to {to}. Code: {response.status_code}, Response: {response.text}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Error calling Meta WhatsApp API for interactive message to {to}: {str(e)}")
            return False

    async def send_interactive_list(
        self,
        to: str,
        text: str,
        button_label: str,
        sections: list[dict],
        title: str | None = None
    ) -> bool:
        """
        Sends an interactive list message (dropdown menu).
        sections should be a list of sections, each having:
        {"title": "Section Title", "rows": [{"id": "row_id", "title": "Row Title", "description": "optional description"}]}
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": text},
                "action": {
                    "button": button_label,
                    "sections": sections
                }
            }
        }
        if title:
            payload["interactive"]["header"] = {"type": "text", "text": title}

        if "fake" in settings.WHATSAPP_API_TOKEN or "fake" in settings.WHATSAPP_PHONE_NUMBER_ID:
            btn_titles = ", ".join([f"{r['title']}" for s in sections for r in s["rows"]])
            logger.info(f"[MOCK WHATSAPP LIST to {to}]: {text} | Options: {btn_titles}")
            print(f"\n📢 [MOCK WHATSAPP TO {to} with List]:\n{text}\n📋 Options: {btn_titles}\n")
            return True

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=10.0
                )
                if response.status_code in [200, 201]:
                    logger.info(f"Interactive list message sent to {to} successfully.")
                    return True
                else:
                    logger.error(
                        f"Failed to send list message to {to}. Code: {response.status_code}, Response: {response.text}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Error calling Meta WhatsApp API for list message to {to}: {str(e)}")
            return False

whatsapp_service = WhatsAppService()
