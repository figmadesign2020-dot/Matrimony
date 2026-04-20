from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import permissions, response, status, viewsets
from rest_framework.decorators import action

from core.utils.matching import get_excluded_user_ids, score_profile_against_preferences
from matches.models import Block, Interest
from matches.serializers import BlockSerializer, InterestSerializer, MatchSuggestionSerializer
from profiles.models import MatrimonialProfile


def users_are_matched(user_one, user_two):
    return Interest.objects.filter(
        (
            Q(sender=user_one, receiver=user_two)
            | Q(sender=user_two, receiver=user_one)
        ),
        status=Interest.STATUS_ACCEPTED,
    ).exists()


class MatchSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MatchSuggestionSerializer
    filterset_fields = ["gender", "religion", "caste", "mother_tongue", "city", "state", "country", "education", "profession"]
    search_fields = ["full_name", "religion", "caste", "mother_tongue", "city", "state", "country", "education", "profession"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        excluded_ids = get_excluded_user_ids(self.request.user)
        queryset = (
            MatrimonialProfile.objects.filter(is_approved=True, is_blocked=False)
            .exclude(user_id__in=excluded_ids)
            .select_related("user")
            .prefetch_related("photos")
        )
        preference = self.request.user.preference

        if preference.religion:
            queryset = queryset.filter(religion__iexact=preference.religion)
        if preference.caste:
            queryset = queryset.filter(caste__iexact=preference.caste)
        if preference.mother_tongue:
            queryset = queryset.filter(mother_tongue__iexact=preference.mother_tongue)
        if preference.country:
            queryset = queryset.filter(country__iexact=preference.country)
        if preference.state:
            queryset = queryset.filter(state__iexact=preference.state)
        if preference.city:
            queryset = queryset.filter(city__iexact=preference.city)
        if preference.education:
            queryset = queryset.filter(education__icontains=preference.education)
        if preference.profession:
            queryset = queryset.filter(profession__icontains=preference.profession)
        return queryset

    @action(detail=False, methods=["get"], url_path="suggested")
    def suggested(self, request):
        queryset = list(self.get_queryset())
        queryset.sort(key=lambda item: score_profile_against_preferences(item, request.user.preference), reverse=True)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class InterestViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InterestSerializer

    def get_queryset(self):
        user = self.request.user
        return Interest.objects.filter(Q(sender=user) | Q(receiver=user)).select_related(
            "sender", "receiver", "sender__profile", "receiver__profile"
        ).prefetch_related("sender__profile__photos", "receiver__profile__photos")

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=["get"])
    def sent(self, request):
        queryset = self.get_queryset().filter(sender=request.user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["get"])
    def received(self, request):
        queryset = self.get_queryset().filter(receiver=request.user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        interest = self.get_object()
        if interest.receiver != request.user:
            return response.Response({"detail": "Only receiver can accept."}, status=status.HTTP_403_FORBIDDEN)
        interest.status = Interest.STATUS_ACCEPTED
        interest.save(update_fields=["status", "updated_at"])
        return response.Response(self.get_serializer(interest).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        interest = self.get_object()
        if interest.receiver != request.user:
            return response.Response({"detail": "Only receiver can reject."}, status=status.HTTP_403_FORBIDDEN)
        interest.status = Interest.STATUS_REJECTED
        interest.save(update_fields=["status", "updated_at"])
        return response.Response(self.get_serializer(interest).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        interest = self.get_object()
        if interest.sender != request.user:
            return response.Response({"detail": "Only sender can cancel."}, status=status.HTTP_403_FORBIDDEN)
        interest.status = Interest.STATUS_CANCELLED
        interest.save(update_fields=["status", "updated_at"])
        return response.Response(self.get_serializer(interest).data)


class BlockViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BlockSerializer

    def get_queryset(self):
        return Block.objects.filter(user=self.request.user).select_related("blocked_user")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@login_required
def matches_view(request):
    viewset = MatchSuggestionViewSet()
    viewset.request = request
    profiles = list(viewset.get_queryset())
    profiles.sort(key=lambda item: score_profile_against_preferences(item, request.user.preference), reverse=True)
    return render(request, "matches/matches.html", {"profiles": profiles})


@login_required
def send_interest_view(request, profile_id):
    profile = get_object_or_404(MatrimonialProfile, pk=profile_id, is_approved=True, is_blocked=False)
    Interest.objects.update_or_create(
        sender=request.user,
        receiver=profile.user,
        defaults={"status": Interest.STATUS_PENDING},
    )
    messages.success(request, f"Interest sent to {profile.full_name or profile.user.email}.")
    return redirect("matches:matches")


@login_required
def sent_interests_view(request):
    interests = Interest.objects.filter(sender=request.user).select_related("receiver__profile").prefetch_related("receiver__profile__photos")
    return render(request, "matches/sent_interests.html", {"interests": interests})


@login_required
def received_interests_view(request):
    interests = Interest.objects.filter(receiver=request.user).select_related("sender__profile").prefetch_related("sender__profile__photos")
    return render(request, "matches/received_interests.html", {"interests": interests})


@login_required
def accept_interest_view(request, pk):
    interest = get_object_or_404(Interest, pk=pk, receiver=request.user)
    interest.status = Interest.STATUS_ACCEPTED
    interest.save(update_fields=["status", "updated_at"])
    messages.success(request, "Interest accepted. You can now chat.")
    return redirect("matches:received-interests")


@login_required
def reject_interest_view(request, pk):
    interest = get_object_or_404(Interest, pk=pk, receiver=request.user)
    interest.status = Interest.STATUS_REJECTED
    interest.save(update_fields=["status", "updated_at"])
    messages.info(request, "Interest rejected.")
    return redirect("matches:received-interests")


@login_required
def cancel_interest_view(request, pk):
    interest = get_object_or_404(Interest, pk=pk, sender=request.user)
    interest.status = Interest.STATUS_CANCELLED
    interest.save(update_fields=["status", "updated_at"])
    messages.info(request, "Interest cancelled.")
    return redirect("matches:sent-interests")
