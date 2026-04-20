from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Conversation(TimeStampedModel):
    participant_one = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversation_starts")
    participant_two = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversation_receives")

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ("participant_one", "participant_two")

    def __str__(self):
        return f"{self.participant_one.email} & {self.participant_two.email}"

    def save(self, *args, **kwargs):
        if self.participant_one_id and self.participant_two_id and self.participant_one_id > self.participant_two_id:
            self.participant_one_id, self.participant_two_id = self.participant_two_id, self.participant_one_id
        super().save(*args, **kwargs)


class Message(TimeStampedModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages_sent")
    content = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message by {self.sender.email}"
