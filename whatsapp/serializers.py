from rest_framework import serializers
from .models import WhatsAppMessage

class WhatsAppMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppMessage
        fields = [
            'id',
            'sender',
            'receiver',
            'content',
            'message_type',
            'whatsapp_message_id',
            'status',
            'timestamp',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'whatsapp_message_id',
            'timestamp',
            'updated_at'
        ]