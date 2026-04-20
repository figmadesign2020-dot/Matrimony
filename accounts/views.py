from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from rest_framework import generics, permissions, response, status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.forms import ForgotPasswordForm, LoginForm, ResetPasswordForm, SignupForm, VerifyOTPForm
from accounts.serializers import (
    EmailTokenObtainPairSerializer,
    OTPVerificationSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    SignupSerializer,
    UserSerializer,
)
from core.utils.otp import set_user_otp


class SignupAPIView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return response.Response(
            {
                "message": "Account created. Verify using the OTP sent in console.",
                "otp": user.otp_code,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class OTPVerificationAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return response.Response({"message": "OTP verified successfully.", "user": UserSerializer(user).data})


class PasswordResetRequestAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return response.Response(
            {"message": "Password reset OTP generated.", "otp": user.otp_code},
            status=status.HTTP_200_OK,
        )


class PasswordResetAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)


class MeAPIView(APIView):
    def get(self, request):
        return response.Response(UserSerializer(request.user).data)


class SignupView(View):
    template_name = "accounts/signup.html"

    def get(self, request):
        return render(request, self.template_name, {"form": SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            serializer = SignupSerializer(data=form.cleaned_data)
            if serializer.is_valid():
                user = serializer.save()
                messages.success(request, f"Account created. Your mock OTP is {user.otp_code}")
                return redirect(f"{reverse_lazy('accounts:verify-otp')}?email={user.email}&purpose=signup")
            form.add_error(None, serializer.errors)
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        return render(request, self.template_name, {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            if user is None:
                form.add_error(None, "Invalid email or password.")
            elif not user.is_verified:
                messages.warning(request, "Please verify your account first.")
                set_user_otp(user, purpose="signup")
                return redirect(f"{reverse_lazy('accounts:verify-otp')}?email={user.email}&purpose=signup")
            else:
                login(request, user)
                messages.success(request, "Welcome back.")
                return redirect("profiles:dashboard")
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("core:home")


class VerifyOTPView(View):
    template_name = "accounts/verify_otp.html"

    def get(self, request):
        initial = {
            "email": request.GET.get("email", ""),
            "purpose": request.GET.get("purpose", "signup"),
        }
        return render(request, self.template_name, {"form": VerifyOTPForm(initial=initial)})

    def post(self, request):
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            serializer = OTPVerificationSerializer(data=form.cleaned_data)
            if serializer.is_valid():
                serializer.save()
                messages.success(request, "Account verification successful. Please log in.")
                return redirect("accounts:login")
            form.add_error(None, serializer.errors)
        return render(request, self.template_name, {"form": form})


class ForgotPasswordView(View):
    template_name = "accounts/forgot_password.html"

    def get(self, request):
        return render(request, self.template_name, {"request_form": ForgotPasswordForm(), "reset_form": ResetPasswordForm()})

    def post(self, request):
        if "request_reset" in request.POST:
            request_form = ForgotPasswordForm(request.POST)
            reset_form = ResetPasswordForm(initial={"email": request.POST.get("email", "")})
            if request_form.is_valid():
                serializer = PasswordResetRequestSerializer(data=request_form.cleaned_data)
                if serializer.is_valid():
                    user = serializer.save()
                    messages.success(request, f"Reset OTP generated. Your mock OTP is {user.otp_code}")
                    reset_form = ResetPasswordForm(initial={"email": user.email})
                else:
                    request_form.add_error(None, serializer.errors)
            return render(
                request,
                self.template_name,
                {"request_form": request_form, "reset_form": reset_form},
            )

        request_form = ForgotPasswordForm(initial={"email": request.POST.get("email", "")})
        reset_form = ResetPasswordForm(request.POST)
        if reset_form.is_valid():
            serializer = PasswordResetSerializer(data=reset_form.cleaned_data)
            if serializer.is_valid():
                serializer.save()
                messages.success(request, "Password reset successful. Please log in.")
                return redirect("accounts:login")
            reset_form.add_error(None, serializer.errors)
        return render(request, self.template_name, {"request_form": request_form, "reset_form": reset_form})


@login_required
def account_overview(request):
    return redirect("profiles:dashboard")


token_refresh_view = TokenRefreshView.as_view()
