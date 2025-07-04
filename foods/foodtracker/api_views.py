from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Sum
from .models import FoodItem, FoodLogEntry
from .serializer import FoodItemSerializer, FoodLogEntrySerializer, FoodSearchSerializer
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import requests
import decimal
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

OPEN_FOOD_FACTS_BASE_URL = "https://world.openfoodfacts.org/cgi/search.pl"
OPEN_FOOD_FACTS_PRODUCT_URL = "https://world.openfoodfacts.org/api/v0/product/"

def search_food_on_open_food_facts(query):
    """
    Searches for food items on Open Food Facts API.
    Returns a list of dictionaries with basic food info.
    """
    params = {
        'search_terms': query,
        'json': 1,
        'page_size': 20 # Limit results to 20 for brevity
    }
    try:

        response = requests.get(OPEN_FOOD_FACTS_BASE_URL, params=params, timeout=10)

# Print raw response text

        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

        data = response.json()


        if 'products' in data:

            foods = []
            for product in data['products']:
                food_name = product.get('product_name') or product.get('product_name_en') or product.get('generic_name')
                nutriments = product.get('nutriments', {})



                if food_name: # Only include if a name is found
                    food_info = {
                        'name': food_name,
                        'external_api_id': product.get('code'), # Use product code as external ID
                        'calories': nutriments.get('energy-kcal_100g'),
                        'protein': nutriments.get('proteins_100g'),
                        'carbs': nutriments.get('carbohydrates_100g'),
                        'fat': nutriments.get('fat_100g'),
                        'sugars': nutriments.get('sugars_100g'),
                        'fiber': nutriments.get('fiber_100g'),
                        'unit': 'g' # Open Food Facts usually provides per 100g
                    }
                    foods.append(food_info)
                

        else:
            print("DEBUG: 'products' key not found in Open Food Facts response or response is empty.")
            foods = [] # Ensure foods is empty if 'products' key is missing or response is empty

        return foods
    except requests.exceptions.RequestException as e:

        return [] # Return empty list on error
    except ValueError as e: # Catch JSON decoding errors

        return []
    except Exception as e: # Catch any other unexpected errors

        return []


def get_food_details_from_open_food_facts(external_id):
    """
    Fetches detailed nutritional information for a specific product from Open Food Facts.
    """
    url = f"{OPEN_FOOD_FACTS_PRODUCT_URL}{external_id}.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'product' in data:
            product = data['product']
            nutriments = product.get('nutriments', {})
            
            food_name = product.get('product_name') or product.get('product_name_en') or product.get('generic_name')
            
            # Construct detailed food info
            detailed_info = {
                'name': food_name,
                'external_api_id': product.get('code'),
                'calories': nutriments.get('energy-kcal_100g'),
                'protein': nutriments.get('proteins_100g'),
                'carbs': nutriments.get('carbohydrates_100g'),
                'fat': nutriments.get('fat_100g'),
                'unit': 'g',
                'sugars': nutriments.get('sugars_100g'),
                'fiber': nutriments.get('fiber_100g'),
            }
            return detailed_info
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Open Food Facts details: {e}")
        return None
    
class FoodSearchApiView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FoodSearchSerializer
    
    @method_decorator(cache_page(60*5))  # Cache for 5 minutes
    def get(self, request, *args, **kwargs):
        print("DEBUG: FoodSearchView GET method hit!")
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data['query']

        # Create a unique cache key based on the query and user
        cache_key = f"food_search_{request.user.id}_{query}"
        cached_results = cache.get(cache_key)
        
        if cached_results is not None:
            return Response(cached_results, status=status.HTTP_200_OK)
            
        search_results = search_food_on_open_food_facts(query)
        
        # Cache the results for 5 minutes (300 seconds)
        cache.set(cache_key, search_results, 300)
        
        return Response(search_results, status=status.HTTP_200_OK)

class FoodLogEntryListCreateView(generics.ListCreateAPIView):
    serializer_class = FoodLogEntrySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or isinstance(self.request.user, AnonymousUser):
            return FoodLogEntry.objects.none()
        
        queryset = FoodLogEntry.objects.filter(user=self.request.user)
        log_date_str = self.request.query_params.get('date')
        if log_date_str:
            try:
                log_date = timezone.datetime.strptime(log_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(log_date=log_date)
            except ValueError:
                raise serializers.ValidationError({"date": _("Invalid date format. UseYYYY-MM-DD.")})
        return queryset.order_by('-log_date', '-created_at')
    def perform_create(self, serializer):
        food_item_id = self.request.data.get('food_item')
        food_name_input = self.request.data.get('food_name')
        quantity = self.request.data.get('quantity')
        quantity_unit = self.request.data.get('quantity_unit')

        food_item_instance = None
        if food_item_id:
            try:
                food_item_instance = FoodItem.objects.get(id=food_item_id)
            except FoodItem.DoesNotExist:
                raise serializers.ValidationError({"food_item": _("Food item not found.")})

        actual_food_name = food_item_instance.name if food_item_instance else food_name_input

        calories_c = decimal.Decimal(0)
        protein_c = decimal.Decimal(0)
        carbs_c = decimal.Decimal(0)
        fat_c = decimal.Decimal(0)
        sugars_c = decimal.Decimal(0) # <--- NEW
        fiber_c = decimal.Decimal(0)   # <--- NEW

        if food_item_instance and quantity is not None:
            try:
                quantity_dec = decimal.Decimal(str(quantity))
            except decimal.InvalidOperation:
                raise serializers.ValidationError({"quantity": _("Quantity must be a valid number.")})

            if food_item_instance.calories is not None:
                calories_c = (food_item_instance.calories / 100) * quantity_dec
            if food_item_instance.protein is not None:
                protein_c = (food_item_instance.protein / 100) * quantity_dec
            if food_item_instance.carbs is not None:
                carbs_c = (food_item_instance.carbs / 100) * quantity_dec
            if food_item_instance.fat is not None:
                fat_c = (food_item_instance.fat / 100) * quantity_dec
            if food_item_instance.sugars is not None: # <--- NEW
                sugars_c = (food_item_instance.sugars / 100) * quantity_dec
            if food_item_instance.fiber is not None: # <--- NEW
                fiber_c = (food_item_instance.fiber / 100) * quantity_dec
        else:
            # If no food_item is linked, values are assumed to be provided directly by client
            # (or default to 0 if not provided and fields are not required)
            # For this implementation, if no food_item, these values will be 0 as initialized
            pass

        serializer.save(
            user=self.request.user,
            food_item=food_item_instance,
            food_name=actual_food_name,
            quantity=quantity_dec if food_item_instance else quantity,
            quantity_unit=quantity_unit,
            calories_consumed=calories_c,
            protein_consumed=protein_c,
            carbs_consumed=carbs_c,
            fat_consumed=fat_c,
            sugars_consumed=sugars_c, # <--- NEW
            fiber_consumed=fiber_c    # <--- NEW
        )
        
class FoodLogEntryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FoodLogEntrySerializer
    permission_classes = [IsAuthenticated]
    queryset = FoodLogEntry.objects.all()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or isinstance(self.request.user, AnonymousUser):
            return FoodLogEntry.objects.none()
        
        return self.queryset.filter(user=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.instance
        food_item_id = self.request.data.get('food_item')
        quantity = self.request.data.get('quantity')

        food_item_instance = instance.food_item
        if food_item_id is not None:
            try:
                food_item_instance = FoodItem.objects.get(id=food_item_id)
            except FoodItem.DoesNotExist:
                raise serializers.ValidationError({"food_item": _("Food item not found.")})
            serializer.validated_data['food_item'] = food_item_instance
            serializer.validated_data['food_name'] = food_item_instance.name

        quantity_dec = instance.quantity
        if quantity is not None:
            try:
                quantity_dec = decimal.Decimal(str(quantity))
            except decimal.InvalidOperation:
                raise serializers.ValidationError({"quantity": _("Quantity must be a valid number.")})
            serializer.validated_data['quantity'] = quantity_dec

        calories_c = decimal.Decimal(0)
        protein_c = decimal.Decimal(0)
        carbs_c = decimal.Decimal(0)
        fat_c = decimal.Decimal(0)
        sugars_c = decimal.Decimal(0)
        fiber_c = decimal.Decimal(0)

        if food_item_instance and quantity_dec is not None:
            if food_item_instance.calories is not None:
                calories_c = (food_item_instance.calories / 100) * quantity_dec
            if food_item_instance.protein is not None:
                protein_c = (food_item_instance.protein / 100) * quantity_dec
            if food_item_instance.carbs is not None:
                carbs_c = (food_item_instance.carbs / 100) * quantity_dec
            if food_item_instance.fat is not None:
                fat_c = (food_item_instance.fat / 100) * quantity_dec
            if food_item_instance.sugars is not None:
                sugars_c = (food_item_instance.sugars / 100) * quantity_dec
            if food_item_instance.fiber is not None:
                fiber_c = (food_item_instance.fiber / 100) * quantity_dec

        serializer.validated_data['calories_consumed'] = calories_c
        serializer.validated_data['protein_consumed'] = protein_c
        serializer.validated_data['carbs_consumed'] = carbs_c
        serializer.validated_data['fat_consumed'] = fat_c
        serializer.validated_data['sugars_consumed'] = sugars_c
        serializer.validated_data['fiber_consumed'] = fiber_c

        super().perform_update(serializer)
        
class DailySummaryView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FoodLogEntrySerializer
    
    @method_decorator(cache_page(60*15))  # Cache for 15 minutes
    def get(self, request, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False) or isinstance(request.user, AnonymousUser):
            return Response({
                "date": timezone.now().strftime('%Y-%m-%d'),
                "total_calories": 0.00,
                "total_protein": 0.00,
                "total_carbs": 0.00,
                "total_fat": 0.00,
                "total_sugars": 0.00,
                "total_fiber": 0.00,
                "log_entries": []
            }, status=status.HTTP_200_OK)
        
        log_date_str = request.query_params.get('date', timezone.now().strftime('%Y-%m-%d'))
        cache_key = f"daily_summary_{request.user.id}_{log_date_str}"
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data, status=status.HTTP_200_OK)
            
        try:
            log_date = timezone.datetime.strptime(log_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"date": _("Invalid date format. UseYYYY-MM-DD.")},
                          status=status.HTTP_400_BAD_REQUEST)

        daily_logs = FoodLogEntry.objects.filter(
            user=request.user,
            log_date=log_date
        )

        summary = daily_logs.aggregate(
            total_calories=Sum('calories_consumed'),
            total_protein=Sum('protein_consumed'),
            total_carbs=Sum('carbs_consumed'),
            total_fat=Sum('fat_consumed'),
            total_sugars=Sum('sugars_consumed'),
            total_fiber=Sum('fiber_consumed')
        )

        response_data = {
            "date": log_date.strftime('%Y-%m-%d'),
            "total_calories": round(summary['total_calories'] or decimal.Decimal(0), 2),
            "total_protein": round(summary['total_protein'] or decimal.Decimal(0), 2),
            "total_carbs": round(summary['total_carbs'] or decimal.Decimal(0), 2),
            "total_fat": round(summary['total_fat'] or decimal.Decimal(0), 2),
            "total_sugars": round(summary['total_sugars'] or decimal.Decimal(0), 2),
            "total_fiber": round(summary['total_fiber'] or decimal.Decimal(0), 2),
            "log_entries": FoodLogEntrySerializer(daily_logs, many=True, context={'request': request}).data
        }

        # Cache for 15 minutes (900 seconds)
        cache.set(cache_key, response_data, 900)
        
        return Response(response_data, status=status.HTTP_200_OK)