from django.urls import path

from chat.views import conversation_list_view, start_chat_view


app_name = "chat"

urlpatterns = [
    path("", conversation_list_view, name="chat"),
    path("start/<int:user_id>/", start_chat_view, name="start-chat"),
]
