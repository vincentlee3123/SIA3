from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse


class PetQuerySet(models.QuerySet):
    def search(self, query):
        if not query:
            return self
        return self.filter(
            Q(pet_id__icontains=query)
            | Q(pet_name__icontains=query)
            | Q(owner_name__icontains=query)
        )

    def by_species(self, species):
        return self.filter(species=species) if species else self

    def by_gender(self, gender):
        return self.filter(gender=gender) if gender else self

    def by_status(self, status):
        return self.filter(status=status) if status else self


class Pet(models.Model):
    class Species(models.TextChoices):
        DOG = "Dog", "Dog"
        CAT = "Cat", "Cat"
        BIRD = "Bird", "Bird"
        FISH = "Fish", "Fish"
        OTHER = "Other", "Other"

    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ADOPTED = "adopted", "Adopted"
        LOST = "lost", "Lost"
        DECEASED = "deceased", "Deceased"

    pet_id = models.CharField(max_length=20, unique=True, verbose_name="Pet ID")
    pet_name = models.CharField(max_length=100, verbose_name="Pet Name")
    species = models.CharField(max_length=50, choices=Species.choices)
    breed = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    age = models.PositiveIntegerField(help_text="Age in years")
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Weight in kilograms",
    )
    gender = models.CharField(max_length=10, choices=Gender.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    owner_name = models.CharField(max_length=100, verbose_name="Owner Name")
    health_details = models.TextField(blank=True, verbose_name="Health Details")
    next_checkup = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to="pet_photos/", blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pets",
    )
    date_registered = models.DateTimeField(auto_now_add=True)

    objects = PetQuerySet.as_manager()

    class Meta:
        ordering = ["-date_registered"]

    def __str__(self):
        return f"{self.pet_name} ({self.pet_id})"

    def get_absolute_url(self):
        return reverse("pet_detail", kwargs={"pk": self.pk})
