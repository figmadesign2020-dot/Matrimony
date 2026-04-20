from rest_framework import serializers

from chat.models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source="sender.email", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "sender_email", "content", "is_read", "created_at"]
        read_only_fields = ["sender", "is_read"]


class ConversationSerializer(serializers.ModelSerializer):
    participant_one_email = serializers.EmailField(source="participant_one.email", read_only=True)
    participant_two_email = serializers.EmailField(source="participant_two.email", read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "participant_one",
            "participant_two",
            "participant_one_email",
            "participant_two_email",
            "last_message",
            "created_at",
            "updated_at",
        ]

    def get_last_message(self, obj):
        message = obj.messages.order_by("-created_at").first()
        if not message:
            return None
        return MessageSerializer(message).data
