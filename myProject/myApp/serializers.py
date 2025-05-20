from rest_framework import serializers
from .models import AdminInventory

class AdminInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminInventory
        fields = ['id', 'name', 'price', 'stock', 'image']  # Include 'image' in the fields


        