from django.urls import path

from .views import get_recipe

app_name = 'recipes'

urlpatterns = [
    path('s/<int:recipe_id>/', get_recipe, name='get_recipe'),
]
