from django.urls import path
from .views import (
    WhatsAppWebhookVerifyView,
    WhatsAppWebhookView,
    WhatsAppSendMessageView,
    WhatsAppMessageListCreateView,
    WhatsAppMessageDetailView
)

app_name = 'whatsapp'

urlpatterns = [
    # Webhook URLs
    path('webhook/', WhatsAppWebhookVerifyView.as_view(), name='webhook-verify'),
    path('webhook/receive/', WhatsAppWebhookView.as_view(), name='webhook-receive'),
    path('messages/send/', WhatsAppSendMessageView.as_view(), name='send-message'),
    
    # Message management URLs
    path('messages/', WhatsAppMessageListCreateView.as_view(), name='message-list'),
    path('messages/<int:pk>/', WhatsAppMessageDetailView.as_view(), name='message-detail'),
] 