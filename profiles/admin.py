from django.contrib import admin

from profiles.models import MatrimonialProfile, PartnerPreference, ProfilePhoto


class ProfilePhotoInline(admin.TabularInline):
    model = ProfilePhoto
    extra = 0


@admin.register(MatrimonialProfile)
class MatrimonialProfileAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "user",
        "gender",
        "religion",
        "city",
        "country",
        "profile_completed",
        "is_approved",
        "is_blocked",
    ]
    list_filter = ["gender", "religion", "country", "profile_completed", "is_approved", "is_blocked"]
    search_fields = ["full_name", "user__email", "city", "state", "country", "profession", "education"]
    inlines = [ProfilePhotoInline]


@admin.register(ProfilePhoto)
class ProfilePhotoAdmin(admin.ModelAdmin):
    list_display = ["profile", "is_primary", "created_at"]
    list_filter = ["is_primary"]
    search_fields = ["profile__full_name", "profile__user__email"]


@admin.register(PartnerPreference)
class PartnerPreferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "minimum_age", "maximum_age", "religion", "city", "country", "updated_at"]
    search_fields = ["user__email", "religion", "city", "state", "country"]
    list_filter = ["country", "religion"]
