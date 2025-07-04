from rest_framework import serializers
from .models import FoodItem, FoodLogEntry
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'calories', 'protein', 'carbs', 'fat', 'sugars', 'fiber',
            'unit', 'external_api_id', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']

class FoodLogEntrySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    food_item_name = serializers.CharField(source='food_item.name', read_only=True)
    
    class Meta:
        model = FoodLogEntry
        fields = [
            'id', 'user', 'user_name', 'food_item', 'food_item_name',
            'food_name', 'quantity', 'quantity_unit',
            'calories_consumed', 'protein_consumed', 'carbs_consumed', 'fat_consumed', 'sugars_consumed', 'fiber_consumed',
            'log_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user',
            'user_name',
            'food_item_name',
            'calories_consumed', 'protein_consumed', 'carbs_consumed', 'fat_consumed', 'sugars_consumed', 'fiber_consumed',
            'created_at', 'updated_at'
        ]

        extra_kwargs = {
            'food_name': {'required': True},
            'quantity': {'required': True},
            'quantity_unit': {'required': True},
        }
        
    def create(self, validated_data):
        # Set the user to the authenticated user making the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Ensure user cannot be changed
        if 'user' in validated_data:
            raise serializers.ValidationError({"user": _("User cannot be changed.")})
        return super().update(instance, validated_data)
    

class FoodSearchSerializer(serializers.Serializer):
    query = serializers.CharField(
        max_length=255,
        required=True,
        help_text=_("The food item to search for (e.g., 'apple', 'chicken breast')")
    )