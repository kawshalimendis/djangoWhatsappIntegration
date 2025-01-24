import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import WhatsAppMessage
from .services import WhatsAppService
from .serializers import WhatsAppMessageSerializer

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookVerifyView(APIView):
    """
    API View for handling WhatsApp webhook verification.
    GET: Verify webhook
    """
    permission_classes = []

    def get(self, request):
        """Handle webhook verification from WhatsApp."""
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
                return HttpResponse(challenge)
            return HttpResponse('Forbidden', status=403)

        return HttpResponse('Bad Request', status=400)


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(APIView):
    """
    API View for handling WhatsApp webhook data.
    POST: Handle incoming webhook data
    """
    permission_classes = []
    whatsapp_service = WhatsAppService()

    def post(self, request):
        """Handle incoming webhook data from WhatsApp."""
        try:
            data = json.loads(request.body.decode('utf-8'))
            self.whatsapp_service.handle_webhook(data)
            return HttpResponse('OK')
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return HttpResponse('Internal Server Error', status=500)


class WhatsAppSendMessageView(APIView):
    """
    API View for sending WhatsApp messages.
    POST: Send a new message (template by default, or text)
    """
    permission_classes = [IsAuthenticated]
    whatsapp_service = WhatsAppService()

    def post(self, request):
        """Send a WhatsApp message (template by default, or text)."""
        try:
            to_phone = request.data.get('to')
            message = request.data.get('message')
            template_name = request.data.get('template_name', 'hello_world')
            language_code = request.data.get('language_code', 'en_US')

            if not to_phone:
                return Response(
                    {'error': 'Phone number (to) is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            whatsapp_message = self.whatsapp_service.send_message(
                to_phone=to_phone,
                message=message,
                template_name=template_name,
                language_code=language_code
            )
            serializer = WhatsAppMessageSerializer(whatsapp_message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return Response(
                {'error': 'Failed to send message'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WhatsAppMessageListCreateView(ListCreateAPIView):
    """
    API View for listing and creating WhatsApp messages.
    GET: List all messages
    POST: Create a new message
    """
    queryset = WhatsAppMessage.objects.all()
    serializer_class = WhatsAppMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter messages based on query parameters."""
        queryset = WhatsAppMessage.objects.all()

        sender = self.request.query_params.get('sender', None)
        receiver = self.request.query_params.get('receiver', None)
        status_param = self.request.query_params.get('status', None)

        if sender:
            queryset = queryset.filter(sender=sender)
        if receiver:
            queryset = queryset.filter(receiver=receiver)
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset


class WhatsAppMessageDetailView(RetrieveUpdateDestroyAPIView):
    """
    API View for retrieving, updating and deleting individual WhatsApp messages.
    GET: Retrieve a message
    PUT/PATCH: Update a message
    DELETE: Delete a message
    """
    queryset = WhatsAppMessage.objects.all()
    serializer_class = WhatsAppMessageSerializer
    permission_classes = [IsAuthenticated]
