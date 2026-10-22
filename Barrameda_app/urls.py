from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .api import PetViewSet

router = DefaultRouter()
router.register("pets", PetViewSet, basename="pet")

urlpatterns = [
    path("", views.PetListView.as_view(), name="pet_list"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("export/csv/", views.pet_export_csv, name="pet_export_csv"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("add/", views.PetCreateView.as_view(), name="pet_create"),
    path("<int:pk>/", views.PetDetailView.as_view(), name="pet_detail"),
    path("<int:pk>/edit/", views.PetUpdateView.as_view(), name="pet_update"),
    path("<int:pk>/delete/", views.PetDeleteView.as_view(), name="pet_delete"),
    path("api/", include(router.urls)),
]
