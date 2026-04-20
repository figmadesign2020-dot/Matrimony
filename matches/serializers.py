from rest_framework import serializers

from core.utils.matching import score_profile_against_preferences
from matches.models import Block, Interest
from profiles.models import MatrimonialProfile
from profiles.serializers import PublicProfileSerializer


class InterestSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source="sender.email", read_only=True)
    receiver_email = serializers.EmailField(source="receiver.email", read_only=True)
    sender_profile = serializers.SerializerMethodField()
    receiver_profile = serializers.SerializerMethodField()

    class Meta:
        model = Interest
        fields = [
            "id",
            "sender",
            "receiver",
            "sender_email",
            "receiver_email",
            "sender_profile",
            "receiver_profile",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["sender", "status"]

    def get_sender_profile(self, obj):
        return PublicProfileSerializer(obj.sender.profile).data

    def get_receiver_profile(self, obj):
        return PublicProfileSerializer(obj.receiver.profile).data

    def validate(self, attrs):
        request = self.context["request"]
        receiver = attrs["receiver"]
        if request.user == receiver:
            raise serializers.ValidationError("You cannot send interest to yourself.")
        if not hasattr(receiver, "profile") or not receiver.profile.is_approved or receiver.profile.is_blocked:
            raise serializers.ValidationError("This profile is not available for interest requests.")
        if Interest.objects.filter(sender=request.user, receiver=receiver).exclude(status=Interest.STATUS_CANCELLED).exists():
            raise serializers.ValidationError("Interest already exists for this user.")
        if Block.objects.filter(user=request.user, blocked_user=receiver).exists() or Block.objects.filter(
            user=receiver, blocked_user=request.user
        ).exists():
            raise serializers.ValidationError("Interest cannot be sent because one of the users is blocked.")
        return attrs


class BlockSerializer(serializers.ModelSerializer):
    blocked_user_email = serializers.EmailField(source="blocked_user.email", read_only=True)

    class Meta:
        model = Block
        fields = ["id", "blocked_user", "blocked_user_email", "created_at"]


class MatchSuggestionSerializer(serializers.ModelSerializer):
    match_percentage = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()

    class Meta:
        model = MatrimonialProfile
        fields = [
            "id",
            "full_name",
            "gender",
            "age",
            "religion",
            "caste",
            "mother_tongue",
            "education",
            "profession",
            "city",
            "state",
            "country",
            "about_me",
            "photos",
            "match_percentage",
        ]

    def get_match_percentage(self, obj):
        request = self.context["request"]
        preference = getattr(request.user, "preference", None)
        return score_profile_against_preferences(obj, preference)

    def get_photos(self, obj):
        return PublicProfileSerializer(obj).data["photos"]
