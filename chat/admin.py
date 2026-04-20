from django.contrib import admin

from chat.models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["participant_one", "participant_two", "updated_at"]
    search_fields = ["participant_one__email", "participant_two__email"]
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["conversation", "sender", "created_at", "is_read"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["sender__email", "content"]
