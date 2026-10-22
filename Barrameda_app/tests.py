from django.test import TestCase
from django.urls import reverse

from .forms import PetForm
from .models import Pet


class PetModelTests(TestCase):
    def setUp(self):
        self.pet = Pet.objects.create(
            pet_id="PET-0001",
            pet_name="Buddy",
            species="Dog",
            breed="Labrador",
            age=4,
            gender="Male",
            owner_name="Jane Doe",
        )

    def test_str_returns_name_and_id(self):
        self.assertEqual(str(self.pet), "Buddy (PET-0001)")

    def test_get_absolute_url(self):
        self.assertEqual(
            self.pet.get_absolute_url(),
            reverse("pet_detail", kwargs={"pk": self.pet.pk}),
        )

    def test_ordering_is_newest_first(self):
        newer = Pet.objects.create(
            pet_id="PET-0002",
            pet_name="Milo",
            species="Cat",
            age=1,
            gender="Male",
            owner_name="John Doe",
        )
        self.assertEqual(list(Pet.objects.all()), [newer, self.pet])


class PetFormTests(TestCase):
    def test_valid_form(self):
        form = PetForm(
            data={
                "pet_id": "PET-0100",
                "pet_name": "Rex",
                "species": "Dog",
                "breed": "",
                "age": 3,
                "gender": "Male",
                "owner_name": "Owner",
                "health_details": "",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_duplicate_pet_id_is_invalid(self):
        Pet.objects.create(
            pet_id="PET-0001",
            pet_name="Buddy",
            species="Dog",
            age=4,
            gender="Male",
            owner_name="Jane Doe",
        )
        form = PetForm(
            data={
                "pet_id": "PET-0001",
                "pet_name": "Other",
                "species": "Cat",
                "breed": "",
                "age": 2,
                "gender": "Female",
                "owner_name": "Someone",
                "health_details": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("pet_id", form.errors)


class PetViewTests(TestCase):
    def setUp(self):
        self.pet = Pet.objects.create(
            pet_id="PET-0001",
            pet_name="Buddy",
            species="Dog",
            breed="Labrador",
            age=4,
            gender="Male",
            owner_name="Jane Doe",
        )

    def test_list_view(self):
        response = self.client.get(reverse("pet_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Buddy")
        self.assertIn("pets", response.context)

    def test_list_view_search(self):
        response = self.client.get(reverse("pet_list"), {"q": "Jane"})
        self.assertContains(response, "Buddy")

        response = self.client.get(reverse("pet_list"), {"q": "Nonexistent"})
        self.assertNotContains(response, "Buddy")

    def test_list_view_pagination(self):
        for i in range(15):
            Pet.objects.create(
                pet_id=f"PET-1{i:03d}",
                pet_name=f"Pet {i}",
                species="Dog",
                age=1,
                gender="Male",
                owner_name="Owner",
            )
        response = self.client.get(reverse("pet_list"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["pets"]), 10)

    def test_detail_view(self):
        response = self.client.get(
            reverse("pet_detail", kwargs={"pk": self.pet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Buddy")

    def test_create_view(self):
        response = self.client.post(
            reverse("pet_create"),
            {
                "pet_id": "PET-0002",
                "pet_name": "Milo",
                "species": "Cat",
                "breed": "",
                "age": 2,
                "gender": "Male",
                "owner_name": "John",
                "health_details": "",
            },
        )
        self.assertRedirects(response, reverse("pet_list"))
        self.assertTrue(Pet.objects.filter(pet_id="PET-0002").exists())

    def test_update_view(self):
        response = self.client.post(
            reverse("pet_update", kwargs={"pk": self.pet.pk}),
            {
                "pet_id": self.pet.pet_id,
                "pet_name": "Buddy Updated",
                "species": "Dog",
                "breed": "Labrador",
                "age": 5,
                "gender": "Male",
                "owner_name": "Jane Doe",
                "health_details": "",
            },
        )
        self.assertRedirects(response, reverse("pet_list"))
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.pet_name, "Buddy Updated")

    def test_delete_view(self):
        response = self.client.post(
            reverse("pet_delete", kwargs={"pk": self.pet.pk})
        )
        self.assertRedirects(response, reverse("pet_list"))
        self.assertFalse(Pet.objects.filter(pk=self.pet.pk).exists())
