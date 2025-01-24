from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import WhatsAppMessage
from .services import WhatsAppService

@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = [
        'sender',
        'receiver',
        'content',
        'message_type',
        'status',
        'timestamp',
        'updated_at'
    ]
    list_filter = ['status', 'message_type', 'timestamp']
    search_fields = ['sender', 'receiver', 'content']
    readonly_fields = ['whatsapp_message_id', 'timestamp', 'updated_at']
    ordering = ['-timestamp']
    
    actions = ['resend_message']
    change_list_template = 'admin/whatsapp/whatsappmessage/change_list.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-test-message/', 
                 self.admin_site.admin_view(self.send_test_message_view),
                 name='send-test-message'),
        ]
        return custom_urls + urls
    
    def send_test_message_view(self, request):
        """View for sending test messages from admin."""
        if request.method == 'POST':
            receiver = request.POST.get('receiver')
            message_type = request.POST.get('message_type')
            
            if not receiver:
                messages.error(request, 'Receiver phone number is required.')
                return redirect('admin:whatsapp_whatsappmessage_changelist')

            try:
                whatsapp_service = WhatsAppService()
                
                if message_type == 'text':
                    content = request.POST.get('content')
                    if not content:
                        messages.error(request, 'Message content is required for text messages.')
                        return redirect('admin:whatsapp_whatsappmessage_changelist')
                    message = whatsapp_service.send_message(receiver, message=content)
                else:  # template message
                    template_name = request.POST.get('template_name', 'hello_world')
                    language_code = request.POST.get('language_code', 'en_US')
                    message = whatsapp_service.send_message(
                        receiver,
                        template_name=template_name,
                        language_code=language_code
                    )

                if message.status != 'failed':
                    messages.success(request, 'Message sent successfully!')
                else:
                    messages.error(request, 'Failed to send message.')
            except Exception as e:
                messages.error(request, f'Error sending message: {str(e)}')
            
            return redirect('admin:whatsapp_whatsappmessage_changelist')
        
        context = {
            'title': 'Send Test Message',
            'app_label': 'whatsapp',
            'opts': self.model._meta,
        }
        return render(request, 'admin/whatsapp/whatsappmessage/send_test_message.html', context)
    
    def resend_message(self, request, queryset):
        """Action to resend failed messages."""
        whatsapp_service = WhatsAppService()
        success_count = 0
        
        for message in queryset:
            if message.status == 'failed':
                try:
                    whatsapp_service.send_message(
                        message.receiver,
                        message.content
                    )
                    success_count += 1
                except Exception:
                    continue
        
        self.message_user(
            request,
            f"Successfully resent {success_count} out of {queryset.count()} messages."
        )
    
    resend_message.short_description = "Resend failed messages"
