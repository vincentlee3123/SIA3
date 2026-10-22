import csv

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import PetForm, PetSearchForm, SignUpForm
from .models import Pet

SORT_FIELDS = {
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
    "next_checkup",
    "date_registered",
}


class PetListView(ListView):
    model = Pet
    template_name = "pets/pet_list.html"
    context_object_name = "pets"
    paginate_by = 10

    def get_queryset(self):
        params = self.request.GET
        queryset = (
            Pet.objects.search(params.get("q", "").strip())
            .by_species(params.get("species", "").strip())
            .by_gender(params.get("gender", "").strip())
            .by_status(params.get("status", "").strip())
        )
        sort = params.get("sort", "").strip()
        if sort in SORT_FIELDS:
            if params.get("dir") == "desc":
                sort = f"-{sort}"
            queryset = queryset.order_by(sort)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET
        querystring = params.copy()
        querystring.pop("page", None)
        context.update(
            {
                "filter_form": PetSearchForm(params),
                "querystring": querystring.urlencode(),
                "query": params.get("q", "").strip(),
                "selected_species": params.get("species", "").strip(),
                "selected_gender": params.get("gender", "").strip(),
                "selected_status": params.get("status", "").strip(),
                "species_choices": Pet.Species.choices,
                "gender_choices": Pet.Gender.choices,
                "status_choices": Pet.Status.choices,
                "sort": params.get("sort", "").strip(),
                "direction": params.get("dir", "").strip(),
            }
        )
        return context


class PetDetailView(DetailView):
    model = Pet
    template_name = "pets/pet_detail.html"
    context_object_name = "pet"


class PetCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Pet
    form_class = PetForm
    template_name = "pets/pet_form.html"
    success_url = reverse_lazy("pet_list")
    success_message = "Pet \"%(pet_name)s\" was registered successfully."

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class PetUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Pet
    form_class = PetForm
    template_name = "pets/pet_form.html"
    context_object_name = "pet"
    success_url = reverse_lazy("pet_list")
    success_message = "Pet \"%(pet_name)s\" was updated successfully."


class PetDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Pet
    template_name = "pets/pet_confirm_delete.html"
    context_object_name = "pet"
    success_url = reverse_lazy("pet_list")
    success_message = "Pet \"%(pet_name)s\" was deleted successfully."

    def get_success_message(self, cleaned_data):
        return self.success_message % {"pet_name": self.object.pet_name}


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "pets/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_pets"] = Pet.objects.count()
        context["species_counts"] = (
            Pet.objects.values("species")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        context["gender_counts"] = (
            Pet.objects.values("gender")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        context["status_counts"] = (
            Pet.objects.values("status")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        context["upcoming_checkups"] = Pet.objects.filter(
            next_checkup__gte=timezone.localdate()
        ).order_by("next_checkup")[:5]
        context["recent_pets"] = Pet.objects.all()[:5]
        status_map = {
            row["status"]: row["total"] for row in context["status_counts"]
        }
        context["active_pets"] = status_map.get(Pet.Status.ACTIVE.value, 0)
        context["adopted_pets"] = status_map.get(Pet.Status.ADOPTED.value, 0)
        context["lost_pets"] = status_map.get(Pet.Status.LOST.value, 0)
        context["upcoming_count"] = Pet.objects.filter(
            next_checkup__gte=timezone.localdate()
        ).count()
        context["today"] = timezone.localdate()
        return context


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")
    success_message = "Your account was created. Please log in."


def pet_export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="pets.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "Pet ID",
            "Name",
            "Species",
            "Breed",
            "Color",
            "Age",
            "Weight (kg)",
            "Gender",
            "Status",
            "Owner",
            "Next Checkup",
            "Date Registered",
        ]
    )
    for pet in Pet.objects.all():
        writer.writerow(
            [
                pet.pet_id,
                pet.pet_name,
                pet.species,
                pet.breed,
                pet.color,
                pet.age,
                pet.weight if pet.weight is not None else "",
                pet.gender,
                pet.get_status_display(),
                pet.owner_name,
                pet.next_checkup if pet.next_checkup else "",
                timezone.localtime(pet.date_registered).strftime(
                    "%Y-%m-%d %H:%M"
                ),
            ]
        )
    return response
