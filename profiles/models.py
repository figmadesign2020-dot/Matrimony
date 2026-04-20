from datetime import date

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class MatrimonialProfile(TimeStampedModel):
    GENDER_CHOICES = (("male", "Male"), ("female", "Female"), ("other", "Other"))
    MARITAL_STATUS_CHOICES = (
        ("never_married", "Never Married"),
        ("divorced", "Divorced"),
        ("widowed", "Widowed"),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    religion = models.CharField(max_length=100, blank=True)
    caste = models.CharField(max_length=100, blank=True)
    mother_tongue = models.CharField(max_length=100, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    education = models.CharField(max_length=200, blank=True)
    profession = models.CharField(max_length=200, blank=True)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True, default="India")
    about_me = models.TextField(blank=True)
    marital_status = models.CharField(max_length=30, choices=MARITAL_STATUS_CHOICES, blank=True)
    profile_completed = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.full_name or self.user.email

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def update_completion_status(self):
        required_fields = [
            self.full_name,
            self.gender,
            self.date_of_birth,
            self.religion,
            self.mother_tongue,
            self.education,
            self.profession,
            self.city,
            self.country,
            self.about_me,
        ]
        self.profile_completed = all(required_fields)


def profile_photo_upload_path(instance, filename):
    return f"profile_photos/user_{instance.profile.user_id}/{filename}"


class ProfilePhoto(TimeStampedModel):
    profile = models.ForeignKey(MatrimonialProfile, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to=profile_photo_upload_path)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "-created_at"]

    def __str__(self):
        return f"Photo for {self.profile}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_primary:
            self.profile.photos.exclude(pk=self.pk).update(is_primary=False)


class PartnerPreference(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="preference")
    minimum_age = models.PositiveIntegerField(null=True, blank=True)
    maximum_age = models.PositiveIntegerField(null=True, blank=True)
    religion = models.CharField(max_length=100, blank=True)
    caste = models.CharField(max_length=100, blank=True)
    mother_tongue = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)
    education = models.CharField(max_length=200, blank=True)
    profession = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Preferences for {self.user.email}"
