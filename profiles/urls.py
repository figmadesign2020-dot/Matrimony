from django.urls import path

from profiles.views import dashboard_view, edit_profile_view, my_profile_view, preference_view, public_profile_view


app_name = "profiles"

urlpatterns = [
    path("dashboard/", dashboard_view, name="dashboard"),
    path("me/", my_profile_view, name="my-profile"),
    path("edit/", edit_profile_view, name="edit-profile"),
    path("preferences/", preference_view, name="preferences"),
    path("<int:pk>/", public_profile_view, name="public-profile"),
]
