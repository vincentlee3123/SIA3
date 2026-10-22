from rest_framework import serializers

from .models import Pet


class PetSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Pet
        fields = [
            "id",
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
            "created_by",
            "date_registered",
        ]
        read_only_fields = ["id", "date_registered", "created_by"]
