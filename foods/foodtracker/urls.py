from django.urls import path
from .api_views import (
    FoodSearchApiView,
    FoodLogEntryListCreateView,
    FoodLogEntryRetrieveUpdateDestroyView,
    DailySummaryView
)

urlpatterns = [
    path('search/', FoodSearchApiView.as_view(), name='food-search'),
    path('logs/', FoodLogEntryListCreateView.as_view(), name='foodlog-list-create'),
    path('logs/<int:pk>/', FoodLogEntryRetrieveUpdateDestroyView.as_view(), name='foodlog-retrieve-update-destroy'),
    path('summary/', DailySummaryView.as_view(), name='daily-summary'),
]
