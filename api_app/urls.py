from django.urls import path
from . import views  # Import your views here

urlpatterns = [
    # Define your API endpoints here
    path('', views.index, name='api_index'),  # Example endpoint
] 