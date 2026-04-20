from rest_framework import serializers

from profiles.models import MatrimonialProfile, PartnerPreference, ProfilePhoto


class ProfilePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePhoto
        fields = ["id", "image", "is_primary", "created_at"]


class MatrimonialProfileSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    photos = ProfilePhotoSerializer(many=True, read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = MatrimonialProfile
        fields = [
            "id",
            "email",
            "phone",
            "full_name",
            "gender",
            "date_of_birth",
            "age",
            "religion",
            "caste",
            "mother_tongue",
            "height",
            "education",
            "profession",
            "annual_income",
            "city",
            "state",
            "country",
            "about_me",
            "marital_status",
            "profile_completed",
            "is_approved",
            "is_blocked",
            "photos",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["profile_completed", "is_approved", "is_blocked"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.update_completion_status()
        instance.save()
        return instance


class PublicProfileSerializer(MatrimonialProfileSerializer):
    class Meta(MatrimonialProfileSerializer.Meta):
        fields = MatrimonialProfileSerializer.Meta.fields


class PartnerPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerPreference
        fields = [
            "id",
            "minimum_age",
            "maximum_age",
            "religion",
            "caste",
            "mother_tongue",
            "city",
            "state",
            "country",
            "education",
            "profession",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        min_age = attrs.get("minimum_age", getattr(self.instance, "minimum_age", None))
        max_age = attrs.get("maximum_age", getattr(self.instance, "maximum_age", None))
        if min_age and max_age and min_age > max_age:
            raise serializers.ValidationError("Minimum age cannot be greater than maximum age.")
        return attrs
