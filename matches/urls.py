from django.urls import path

from matches.views import (
    accept_interest_view,
    cancel_interest_view,
    matches_view,
    received_interests_view,
    reject_interest_view,
    send_interest_view,
    sent_interests_view,
)


app_name = "matches"

urlpatterns = [
    path("", matches_view, name="matches"),
    path("send-interest/<int:profile_id>/", send_interest_view, name="send-interest"),
    path("sent/", sent_interests_view, name="sent-interests"),
    path("received/", received_interests_view, name="received-interests"),
    path("accept/<int:pk>/", accept_interest_view, name="accept-interest"),
    path("reject/<int:pk>/", reject_interest_view, name="reject-interest"),
    path("cancel/<int:pk>/", cancel_interest_view, name="cancel-interest"),
]
