from django.contrib import admin

from .models import Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = (
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
        "created_by",
        "date_registered",
    )
    list_filter = ("species", "gender", "status")
    search_fields = ("pet_id", "pet_name", "owner_name")
    ordering = ("-date_registered",)
    date_hierarchy = "date_registered"
    readonly_fields = ("created_by",)
    list_select_related = ("created_by",)
