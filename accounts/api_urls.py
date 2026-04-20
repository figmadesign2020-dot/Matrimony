from django.urls import path

from accounts.views import EmailTokenObtainPairView, MeAPIView, SignupAPIView, token_refresh_view


urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="api-signup"),
    path("token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", token_refresh_view, name="token_refresh"),
    path("me/", MeAPIView.as_view(), name="api-me"),
]
