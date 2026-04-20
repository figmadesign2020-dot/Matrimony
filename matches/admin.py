from django.contrib import admin

from matches.models import Block, Interest


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ["sender", "receiver", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["sender__email", "receiver__email", "sender__profile__full_name", "receiver__profile__full_name"]


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ["user", "blocked_user", "created_at"]
    search_fields = ["user__email", "blocked_user__email"]
