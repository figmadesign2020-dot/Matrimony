from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import permissions, response, status, viewsets
from rest_framework.decorators import action

from chat.models import Conversation, Message
from chat.serializers import ConversationSerializer, MessageSerializer
from matches.views import users_are_matched


def get_or_create_conversation(user_one, user_two):
    first, second = sorted([user_one, user_two], key=lambda user: user.id)
    conversation, _ = Conversation.objects.get_or_create(participant_one=first, participant_two=second)
    return conversation


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(
            Q(participant_one=self.request.user) | Q(participant_two=self.request.user)
        ).prefetch_related("messages")

    @action(detail=False, methods=["post"], url_path="start")
    def start(self, request):
        other_user_id = request.data.get("user_id")
        if not other_user_id:
            return response.Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        from accounts.models import User

        other_user = get_object_or_404(User, pk=other_user_id)
        if not users_are_matched(request.user, other_user):
            return response.Response({"detail": "You can chat only with matched users."}, status=status.HTTP_403_FORBIDDEN)
        conversation = get_or_create_conversation(request.user, other_user)
        return response.Response(self.get_serializer(conversation).data, status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        queryset = Message.objects.filter(
            Q(conversation__participant_one=self.request.user) | Q(conversation__participant_two=self.request.user)
        ).select_related("conversation", "sender")
        conversation_id = self.request.query_params.get("conversation")
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        return queryset

    def perform_create(self, serializer):
        conversation = serializer.validated_data["conversation"]
        participants = [conversation.participant_one, conversation.participant_two]
        if self.request.user not in participants:
            raise permissions.PermissionDenied("Not part of this conversation.")
        other_user = conversation.participant_two if conversation.participant_one == self.request.user else conversation.participant_one
        if not users_are_matched(self.request.user, other_user):
            raise permissions.PermissionDenied("You can chat only with matched users.")
        serializer.save(sender=self.request.user)
        conversation.save(update_fields=["updated_at"])


@login_required
def conversation_list_view(request):
    conversations = Conversation.objects.filter(
        Q(participant_one=request.user) | Q(participant_two=request.user)
    ).prefetch_related("messages")
    selected_conversation = None
    selected_messages = []

    conversation_id = request.GET.get("conversation")
    if conversation_id:
        selected_conversation = get_object_or_404(conversations, pk=conversation_id)
        selected_messages = selected_conversation.messages.select_related("sender")

    if request.method == "POST":
        target_user_id = request.POST.get("target_user_id")
        content = request.POST.get("content", "").strip()

        if target_user_id and content:
            from accounts.models import User

            target_user = get_object_or_404(User, pk=target_user_id)
            if users_are_matched(request.user, target_user):
                conversation = get_or_create_conversation(request.user, target_user)
                Message.objects.create(conversation=conversation, sender=request.user, content=content)
                conversation.save(update_fields=["updated_at"])
                messages.success(request, "Message sent.")
                return redirect(f"/chat/?conversation={conversation.id}")
            messages.error(request, "You can chat only with matched users.")

        if conversation_id and content and selected_conversation:
            Message.objects.create(conversation=selected_conversation, sender=request.user, content=content)
            selected_conversation.save(update_fields=["updated_at"])
            messages.success(request, "Message sent.")
            return redirect(f"/chat/?conversation={selected_conversation.id}")

    return render(
        request,
        "chat/chat.html",
        {
            "conversations": conversations,
            "selected_conversation": selected_conversation,
            "selected_messages": selected_messages,
        },
    )


@login_required
def start_chat_view(request, user_id):
    from accounts.models import User

    other_user = get_object_or_404(User, pk=user_id)
    if not users_are_matched(request.user, other_user):
        messages.error(request, "You can start chat only with matched users.")
        return redirect("matches:received-interests")
    conversation = get_or_create_conversation(request.user, other_user)
    return redirect(f"/chat/?conversation={conversation.id}")
