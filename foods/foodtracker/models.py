from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
# Create your models here.

class FoodItem(models.Model):
    name = models.CharField(_("Food Name"), max_length=255, unique=True)
    calories = models.DecimalField(_("Calories (per 100g)"), max_digits=8, decimal_places=2, null=True, blank=True)
    protein = models.DecimalField(_("Protien (per 100g)"), max_digits=8, decimal_places=2, null=True, blank=True)
    carbs = models.DecimalField(_("Carps (per 100g)"), max_digits=8, decimal_places=2, null=True, blank=True)
    fat = models.DecimalField(_("Fat (per 100g)"), max_digits=8, decimal_places=2, null=True, blank=True)
    sugars = models.DecimalField(_("Sugars (per 100g)"), max_digits=8, decimal_places=2, null=True, blank=True)
    fiber = models.DecimalField(_("Fiber (per 100g)"), max_digits=8, decimal_places=2, null=True, blank=True)
    
    unit = models.CharField(_("Unit of Measurement"), max_length=50, default="g")
    
    external_api_id = models.CharField(max_length=255, null=True, blank=True, help_text=_("ID from external food database (e.g., Open Food Facts)"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='custom_food_items',
        help_text=_("User who created this custom food item (if applicable)")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Food Item")
        verbose_name_plural = _("Food Items")
        ordering = ['name']

    def __str__(self):
        return self.name


class FoodLogEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='food_logs',
        verbose_name=_("User")
    )
    
    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logged_entries',
        verbose_name=_("Food Item")
    )
    
    food_name = models.CharField(_("Food Name"), max_length=255)
    quantity = models.DecimalField(_("Quantity Consumed"), max_digits=8, decimal_places=2)
    quantity_unit = models.CharField(_("Quantity Unit"), max_length=50)

    calories_consumed = models.DecimalField(_("Calories Consumed"), max_digits=8, decimal_places=2)
    protein_consumed = models.DecimalField(_("Protein Consumed"), max_digits=8, decimal_places=2)
    carbs_consumed = models.DecimalField(_("Carbohydrates Consumed"), max_digits=8, decimal_places=2)
    fat_consumed = models.DecimalField(_("Fat Consumed"), max_digits=8, decimal_places=2)
    sugars_consumed = models.DecimalField(_("Sugars Consumed"), max_digits=8, decimal_places=2, default=0)
    fiber_consumed = models.DecimalField(_("Fiber Consumed"), max_digits=8, decimal_places=2, default=0)
    
    log_date = models.DateField(_("Log Date"), default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Food Log Entry")
        verbose_name_plural = _("Food Log Entries")
        ordering = ['-log_date', '-created_at']
        
    def __str__(self):
        return f"{self.user.name} ate {self.quantity} {self.quantity_unit} of {self.food_name} on {self.log_date}"

    def save(self, *args, **kwargs):
        if self.food_item and self.quantity is not None:
            if not self.food_name:
                self.food_name = self.food_item.name
            if self.food_item.calories is not None:
                self.calories_consumed = (self.food_item.calories / 100) * self.quantity
            if self.food_item.protein is not None:
                self.protein_consumed = (self.food_item.protein / 100) * self.quantity
            if self.food_item.carbs is not None:
                self.carbs_consumed = (self.food_item.carbs / 100) * self.quantity
            if self.food_item.fat is not None:
                self.fat_consumed = (self.food_item.fat / 100) * self.quantity
        elif self.quantity is not None:
            pass
        super().save(*args, **kwargs)