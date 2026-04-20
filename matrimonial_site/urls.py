from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import OTPVerificationAPIView, PasswordResetAPIView, PasswordResetRequestAPIView
from chat.views import ConversationViewSet, MessageViewSet
from matches.views import BlockViewSet, InterestViewSet, MatchSuggestionViewSet
from profiles.views import PartnerPreferenceViewSet, ProfilePhotoViewSet, PublicProfileViewSet


router = DefaultRouter()
router.register(r"profiles", PublicProfileViewSet, basename="api-profiles")
router.register(r"preferences", PartnerPreferenceViewSet, basename="api-preferences")
router.register(r"photos", ProfilePhotoViewSet, basename="api-photos")
router.register(r"interests", InterestViewSet, basename="api-interests")
router.register(r"blocks", BlockViewSet, basename="api-blocks")
router.register(r"matches", MatchSuggestionViewSet, basename="api-matches")
router.register(r"conversations", ConversationViewSet, basename="api-conversations")
router.register(r"messages", MessageViewSet, basename="api-messages")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("profiles/", include("profiles.urls")),
    path("matches/", include("matches.urls")),
    path("chat/", include("chat.urls")),
    path("api/auth/", include("accounts.api_urls")),
    path("api/auth/verify-otp/", OTPVerificationAPIView.as_view(), name="api-verify-otp"),
    path("api/auth/forgot-password/", PasswordResetRequestAPIView.as_view(), name="api-forgot-password"),
    path("api/auth/reset-password/", PasswordResetAPIView.as_view(), name="api-reset-password"),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
