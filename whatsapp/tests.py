from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import WhatsAppMessage
from .services import WhatsAppService


class WhatsAppMessageModelTests(TestCase):
    def test_create_message(self):
        """whatsApp message creation"""
        message = WhatsAppMessage.objects.create(
            sender="+1234567890",
            receiver="+0987654321",
            content="Template: hello_world",
            message_type="template",
            status="sent"
        )
        self.assertEqual(message.content, "Template: hello_world")
        self.assertEqual(message.status, "sent")


class WhatsAppAPITests(APITestCase):
    def setUp(self):
        """Set up test data and authentication"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.message_data = {
            "to": "+1234567890",
            "template_name": "hello_world"
        }

        # Create a test message
        self.test_message = WhatsAppMessage.objects.create(
            sender="+1234567890",
            receiver="+0987654321",
            content="Template: hello_world",
            message_type="template",
            status="sent"
        )

    def test_webhook_verification(self):
        """Test webhook verification endpoint"""
        url = reverse('whatsapp:webhook-verify')
        params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'your-verify-token',
            'hub.challenge': '1234567890'
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), '1234567890')

    def test_webhook_receive(self):
        """Test webhook receive endpoint"""
        url = reverse('whatsapp:webhook-receive')
        webhook_data = {
            "messages": [{
                "from": "+1234567890",
                "id": "test-message-id",
                "text": {"body": "Test incoming message"}
            }]
        }
        response = self.client.post(url, webhook_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_message(self):
        """Test message sending endpoint"""
        url = reverse('whatsapp:send-message')
        response = self.client.post(url, self.message_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['content'], "Template: hello_world")

    def test_list_messages(self):
        """Test message listing endpoint"""
        url = reverse('whatsapp:message-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_retrieve_message(self):
        """Test message detail endpoint"""
        url = reverse('whatsapp:message-detail', args=[self.test_message.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Template: hello_world')

    def test_update_message(self):
        """Test message update endpoint"""
        url = reverse('whatsapp:message-detail', args=[self.test_message.id])
        update_data = {'status': 'delivered'}
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'delivered')

    def test_delete_message(self):
        """Test message deletion endpoint"""
        url = reverse('whatsapp:message-detail', args=[self.test_message.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(WhatsAppMessage.objects.filter(id=self.test_message.id).exists())


class WhatsAppServiceTests(TestCase):
    def setUp(self):
        self.service = WhatsAppService()

    def test_message_creation(self):
        """Test message creation through service"""
        message = self.service.send_message("+1234567890")
        self.assertIsInstance(message, WhatsAppMessage)
        self.assertEqual(message.content, "Template: hello_world")
        self.assertEqual(message.message_type, "template")

    def test_webhook_handling(self):
        """Test webhook data handling"""
        webhook_data = {
            "messages": [{
                "from": "+1234567890",
                "id": "test-message-id",
                "text": {"body": "Test incoming message"}
            }]
        }
        self.service.handle_webhook(webhook_data)
        message = WhatsAppMessage.objects.get(whatsapp_message_id="test-message-id")
        self.assertEqual(message.content, "Test incoming message")
