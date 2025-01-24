import logging
import requests
from django.conf import settings
from .models import WhatsAppMessage

logger = logging.getLogger(__name__)


class WhatsAppService:

    def __init__(self):
        self.base_url = settings.WHATSAPP_BASE_URL
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def send_message(self, to_phone: str, message: str = None, template_name: str = "hello_world",
                     language_code: str = "en_US") -> WhatsAppMessage:
        """Send a WhatsApp message and store it in the database."""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"

            # Base payload
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
            }

            # use template messages
            if message is not None:
                payload.update({
                    "type": "text",
                    "text": {"body": message}
                })
                message_type = 'text'
                content = message
            else:
                payload.update({
                    "type": "template",
                    "template": {
                        "name": template_name,
                        "language": {
                            "code": language_code
                        }
                    }
                })
                message_type = 'template'
                content = f"Template: {template_name}"

            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()

            # Create message record
            whatsapp_message = WhatsAppMessage.objects.create(
                sender=self.phone_number_id,
                receiver=to_phone,
                content=content,
                message_type=message_type,
                whatsapp_message_id=response.json().get('messages', [{}])[0].get('id')
            )

            logger.info(f"Message sent successfully: {whatsapp_message.whatsapp_message_id}")
            return whatsapp_message

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            # Create failed message record but preserve the content and type
            whatsapp_message = WhatsAppMessage.objects.create(
                sender=self.phone_number_id,
                receiver=to_phone,
                content=str(e),
                message_type="",
                status='failed'
            )
            return whatsapp_message

    def handle_webhook(self, data: dict) -> None:
        """Handle incoming webhook data from WhatsApp."""
        try:
            # Handle incoming messages
            if 'messages' in data:
                for message in data['messages']:
                    WhatsAppMessage.objects.create(
                        sender=message.get('from'),
                        receiver=self.phone_number_id,
                        content=message.get('text', {}).get('body', ''),
                        message_type='text',
                        whatsapp_message_id=message.get('id')
                    )
                    logger.info(f"Incoming message processed: {message.get('id')}")

            if 'statuses' in data:
                for status in data['statuses']:
                    message_id = status.get('id')
                    try:
                        message = WhatsAppMessage.objects.get(whatsapp_message_id=message_id)
                        message.status = status.get('status', 'sent')
                        message.save()
                        logger.info(f"Status updated for message {message_id}: {message.status}")
                    except WhatsAppMessage.DoesNotExist:
                        logger.warning(f"Message not found for status update: {message_id}")

        except Exception as e:
            logger.error(f"Error processing webhook data: {str(e)}")
            raise
