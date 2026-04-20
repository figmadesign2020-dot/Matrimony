from django.urls import path

from accounts.views import ForgotPasswordView, LoginView, LogoutView, SignupView, VerifyOTPView, account_overview


app_name = "accounts"

urlpatterns = [
    path("", account_overview, name="overview"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
]
