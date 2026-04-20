from django import forms

from profiles.models import MatrimonialProfile, PartnerPreference


class ProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    class Meta:
        model = MatrimonialProfile
        exclude = ["user", "profile_completed", "is_approved", "is_blocked", "created_at", "updated_at"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "religion": forms.TextInput(attrs={"class": "form-control"}),
            "caste": forms.TextInput(attrs={"class": "form-control"}),
            "mother_tongue": forms.TextInput(attrs={"class": "form-control"}),
            "height": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "education": forms.TextInput(attrs={"class": "form-control"}),
            "profession": forms.TextInput(attrs={"class": "form-control"}),
            "annual_income": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "about_me": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "marital_status": forms.Select(attrs={"class": "form-select"}),
        }


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = PartnerPreference
        exclude = ["user", "created_at", "updated_at"]
        widgets = {
            "minimum_age": forms.NumberInput(attrs={"class": "form-control"}),
            "maximum_age": forms.NumberInput(attrs={"class": "form-control"}),
            "religion": forms.TextInput(attrs={"class": "form-control"}),
            "caste": forms.TextInput(attrs={"class": "form-control"}),
            "mother_tongue": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "education": forms.TextInput(attrs={"class": "form-control"}),
            "profession": forms.TextInput(attrs={"class": "form-control"}),
        }


class PhotoUploadForm(forms.Form):
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={"class": "form-control"}))
    is_primary = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
