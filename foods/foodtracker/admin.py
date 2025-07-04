from django.contrib import admin
from .models import FoodItem, FoodLogEntry

# Register your models here.

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories', 'sugars', 'fiber', 'unit', 'external_api_id', 'created_by')
    search_fields = ('name', 'external_api_id')
    list_filter = ('unit',)
    # Optionally, if you want to make it easier to add/edit created_by in admin
    # raw_id_fields = ('created_by',)


@admin.register(FoodLogEntry)
class FoodLogEntryAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'food_name', 'quantity', 'quantity_unit', 'log_date',
        'calories_consumed', 'protein_consumed', 'carbs_consumed', 'fat_consumed',
        'sugars_consumed', 'fiber_consumed', # <--- NEW FIELDS
        'created_at'
    )
    list_filter = ('user', 'log_date', 'quantity_unit')
    search_fields = ('user__email', 'user__name', 'food_name')
    date_hierarchy = 'log_date' # Adds a date navigation bar
    # raw_id_fields allows you to search for user/food_item by ID, useful for many entries
    raw_id_fields = ('user', 'food_item')
    readonly_fields = (
        'calories_consumed', 'protein_consumed', 'carbs_consumed', 'fat_consumed',
        'sugars_consumed', 'fiber_consumed', # <--- NEW FIELDS
        'created_at', 'updated_at'
    )
