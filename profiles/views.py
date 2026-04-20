from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import permissions, response, status, viewsets
from rest_framework.decorators import action

from core.utils.matching import get_excluded_user_ids
from profiles.forms import PhotoUploadForm, PreferenceForm, ProfileForm
from profiles.models import MatrimonialProfile, PartnerPreference, ProfilePhoto
from profiles.serializers import MatrimonialProfileSerializer, PartnerPreferenceSerializer, ProfilePhotoSerializer, PublicProfileSerializer


class PublicProfileViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PublicProfileSerializer
    filterset_fields = ["gender", "religion", "caste", "mother_tongue", "city", "state", "country", "education", "profession"]
    search_fields = ["full_name", "religion", "caste", "mother_tongue", "city", "state", "country", "education", "profession"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        excluded_ids = get_excluded_user_ids(self.request.user)
        return MatrimonialProfile.objects.filter(is_approved=True, is_blocked=False).exclude(user_id__in=excluded_ids).select_related("user").prefetch_related("photos")

    def get_serializer_class(self):
        if self.action in ["me", "update", "partial_update"]:
            return MatrimonialProfileSerializer
        return PublicProfileSerializer

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        profile = request.user.profile
        if request.method == "GET":
            return response.Response(MatrimonialProfileSerializer(profile).data)

        serializer = MatrimonialProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)


class PartnerPreferenceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PartnerPreferenceSerializer

    def get_queryset(self):
        return PartnerPreference.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user.preference)
        return response.Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user.preference, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user.preference, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user.preference)
        return response.Response(serializer.data)

    def get_object(self):
        return self.request.user.preference


class ProfilePhotoViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfilePhotoSerializer

    def get_queryset(self):
        return ProfilePhoto.objects.filter(profile=self.request.user.profile)

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)


def dashboard_view(request):
    profile = request.user.profile
    total_matches = MatrimonialProfile.objects.filter(is_approved=True, is_blocked=False).exclude(user=request.user).count()
    recent_profiles = (
        MatrimonialProfile.objects.filter(is_approved=True, is_blocked=False)
        .exclude(Q(user=request.user) | Q(user_id__in=get_excluded_user_ids(request.user)))
        .select_related("user")
        .prefetch_related("photos")[:6]
    )
    return render(
        request,
        "profiles/dashboard.html",
        {"profile": profile, "total_matches": total_matches, "recent_profiles": recent_profiles},
    )


@login_required
def my_profile_view(request):
    return render(request, "profiles/profile.html", {"profile": request.user.profile, "is_self": True})


@login_required
def public_profile_view(request, pk):
    profile = get_object_or_404(
        MatrimonialProfile.objects.select_related("user").prefetch_related("photos"),
        pk=pk,
        is_approved=True,
        is_blocked=False,
    )
    return render(request, "profiles/profile.html", {"profile": profile, "is_self": profile.user == request.user})


@login_required
def edit_profile_view(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        photo_form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            updated_profile = form.save(commit=False)
            updated_profile.update_completion_status()
            updated_profile.save()
            if request.FILES.get("image") and photo_form.is_valid():
                photo = ProfilePhoto.objects.create(
                    profile=profile,
                    image=photo_form.cleaned_data["image"],
                    is_primary=photo_form.cleaned_data["is_primary"],
                )
                if photo.is_primary:
                    profile.photos.exclude(pk=photo.pk).update(is_primary=False)
            messages.success(request, "Profile updated successfully.")
            return redirect("profiles:my-profile")
    else:
        form = ProfileForm(instance=profile)
        photo_form = PhotoUploadForm()
    return render(request, "profiles/edit_profile.html", {"form": form, "photo_form": photo_form, "profile": profile})


@login_required
def preference_view(request):
    preference = request.user.preference
    if request.method == "POST":
        form = PreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, "Partner preferences saved.")
            return redirect("profiles:preferences")
    else:
        form = PreferenceForm(instance=preference)
    return render(request, "profiles/preferences.html", {"form": form})
