import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IMS_Barrameda.settings")
    import django

    django.setup()

from django import forms
from django.contrib.auth import get_user_model

from Barrameda_app.models import Pet

SORT_CHOICES = [
    ("", "Default"),
    ("pet_id", "Pet ID"),
    ("pet_name", "Pet Name"),
    ("species", "Species"),
    ("breed", "Breed"),
    ("age", "Age"),
    ("weight", "Weight"),
    ("owner_name", "Owner"),
    ("next_checkup", "Next Checkup"),
    ("date_registered", "Date Registered"),
]

DIRECTION_CHOICES = [
    ("", "Ascending"),
    ("desc", "Descending"),
]


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = [
            "pet_id",
            "pet_name",
            "species",
            "breed",
            "color",
            "age",
            "weight",
            "gender",
            "status",
            "owner_name",
            "health_details",
            "next_checkup",
            "photo",
        ]
        widgets = {
            "pet_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. PET-0001",
                    "autofocus": True,
                }
            ),
            "pet_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Pet name"}
            ),
            "species": forms.Select(attrs={"class": "form-select"}),
            "breed": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Optional"}
            ),
            "color": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Brown"}
            ),
            "age": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "weight": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "step": "0.01"}
            ),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "owner_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Owner full name"}
            ),
            "health_details": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Vaccinations, allergies, notes...",
                }
            ),
            "next_checkup": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "photo": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }
        labels = {
            "pet_id": "Pet ID",
            "pet_name": "Pet Name",
            "owner_name": "Owner Name",
            "health_details": "Health Details",
            "next_checkup": "Next Checkup",
        }

    def clean_pet_id(self):
        pet_id = self.cleaned_data["pet_id"].strip().upper()
        duplicates = Pet.objects.filter(pet_id__iexact=pet_id)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("A pet with this ID already exists.")
        return pet_id

    def clean_pet_name(self):
        return self.cleaned_data["pet_name"].strip()

    def clean_owner_name(self):
        return self.cleaned_data["owner_name"].strip()

    def clean_weight(self):
        weight = self.cleaned_data.get("weight")
        if weight is not None and weight <= 0:
            raise forms.ValidationError("Weight must be greater than zero.")
        return weight


class PetSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "type": "search",
                "placeholder": "Pet ID, name, or owner",
            }
        ),
    )
    species = forms.ChoiceField(
        required=False,
        label="Species",
        choices=[("", "All species")] + list(Pet.Species.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    gender = forms.ChoiceField(
        required=False,
        label="Gender",
        choices=[("", "All genders")] + list(Pet.Gender.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        required=False,
        label="Status",
        choices=[("", "All statuses")] + list(Pet.Status.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort = forms.ChoiceField(
        required=False,
        label="Sort by",
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    dir = forms.ChoiceField(
        required=False,
        label="Direction",
        choices=DIRECTION_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class SignUpForm(forms.ModelForm):
    email = forms.EmailField(
        label="Gmail Address",
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "you@gmail.com",
                "autocomplete": "email",
            }
        ),
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "autocomplete": "new-password"}
        ),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "autocomplete": "new-password"}
        ),
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Choose a username",
                    "autofocus": True,
                }
            )
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not email.endswith("@gmail.com"):
            raise forms.ValidationError("Please use a Gmail address ending in @gmail.com.")
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This Gmail address is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if not password1:
            self.add_error("password1", "Please enter a password.")
        elif password1 != password2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


if __name__ == "__main__":
    print("Forms loaded successfully.")
    for form_class in (PetForm, PetSearchForm, SignUpForm):
        form = form_class()
        print(f"{form_class.__name__}: {', '.join(form.fields)}")
