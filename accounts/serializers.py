from django.contrib.auth import authenticate, password_validation
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import User
from core.utils.otp import set_user_otp


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "phone", "is_verified", "created_at"]


class SignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "phone", "password", "confirm_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        password_validation.validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(
            email=validated_data["email"],
            phone=validated_data["phone"],
            password=validated_data["password"],
            is_active=True,
            is_verified=False,
        )
        set_user_otp(user, purpose="signup")
        return user


class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(choices=[("signup", "signup"), ("reset_password", "reset_password")])

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs["email"])
        except User.DoesNotExist as exc:
            raise serializers.ValidationError({"email": "User not found."}) from exc

        if not user.otp_is_valid(attrs["otp"], attrs["purpose"]):
            raise serializers.ValidationError({"otp": "Invalid or expired OTP."})

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        if self.validated_data["purpose"] == "signup":
            user.is_verified = True
        user.otp_code = ""
        user.otp_purpose = ""
        user.otp_created_at = None
        user.save(update_fields=["is_verified", "otp_code", "otp_purpose", "otp_created_at"])
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email.")
        return value

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data["email"])
        set_user_otp(user, purpose="reset_password")
        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        password_validation.validate_password(attrs["new_password"])
        try:
            user = User.objects.get(email=attrs["email"])
        except User.DoesNotExist as exc:
            raise serializers.ValidationError({"email": "User not found."}) from exc

        if not user.otp_is_valid(attrs["otp"], "reset_password"):
            raise serializers.ValidationError({"otp": "Invalid or expired OTP."})

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.otp_code = ""
        user.otp_purpose = ""
        user.otp_created_at = None
        user.save()
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        credentials = {
            "email": attrs.get("email"),
            "password": attrs.get("password"),
        }
        user = authenticate(request=self.context.get("request"), **credentials)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_verified:
            raise serializers.ValidationError("Please verify your account first.")
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
